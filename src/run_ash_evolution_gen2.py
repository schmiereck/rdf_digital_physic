#!/usr/bin/env python3
"""
run_ash_evolution_gen2.py

Breeds and evaluates a second generation of ash-animating C2-symmetric rules.

1. Load Gen-1 fitness results; identify 11 elites (fitness > 0.052432).
2. Breed 100 Gen-2 rules: top-2 elites carried over + 98 bred via crossover.
3. Evaluate each Gen-2 rule with ash-based fitness (400 steps).
4. Save results and compare Gen-1 vs Gen-2 performance.
"""

import csv
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT     = Path(__file__).parent.parent
ASH_PATTERN_PATH = Path(__file__).parent / "ash_pattern.json"
GEN1_POP_DIR     = PROJECT_ROOT / "archive" / "iter_121" / "population"
GEN1_CSV         = PROJECT_ROOT / "archive" / "iter_121" / "results" / "fitness_scores.csv"
GEN2_POP_DIR     = PROJECT_ROOT / "archive" / "iter_122" / "population"
GEN2_RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_122" / "results"
GEN2_RESULT_YAML = PROJECT_ROOT / "archive" / "iter_122" / "result.yaml"

POPULATION_SIZE = 100
STEPS           = 400
MAX_ATTEMPTS    = 10000
INERT_BASELINE  = 0.052432
INITIAL_BITS    = 325
INITIAL_OBJECTS = 72
GEN1_TOP        = 0.09386   # rule_030 fitness (best Gen-1 rule)
MUTATION_PROB   = 0.10
N_ELITES        = 11
N_CARRY_OVER    = 2

HEX_DIRS = [
    ( 1,  0),  # E
    ( 1, -1),  # SE
    ( 0, -1),  # SW
    (-1,  0),  # W
    (-1,  1),  # NW
    ( 0,  1),  # NE
]


# ── C2-symmetric rule helpers ─────────────────────────────────────────────────
# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1  # E
    b2 = (state >> 4) & 1  # SE
    b3 = (state >> 3) & 1  # SW
    b4 = (state >> 2) & 1  # W
    b5 = (state >> 1) & 1  # NW
    b6 = (state >> 0) & 1  # NE
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def is_valid_c2_pair(a: int, b: int) -> bool:
    if a == b or a == 0 or b == 0:
        return False
    ra = rotate_c2(a)
    rb = rotate_c2(b)
    return len({a, b, ra, rb}) == 4


def is_nonconserving(pairs: list) -> bool:
    return any(bin(a).count('1') != bin(b).count('1') for a, b in pairs)


def try_build_c2_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        for src, dst in [(a, b), (b, a), (ra, rb), (rb, ra)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def generate_random_c2_pair(rng: random.Random):
    for _ in range(200):
        a = rng.randint(1, 127)
        b = rng.randint(1, 127)
        if is_valid_c2_pair(a, b):
            return (a, b)
    return None


def generate_random_c2_rule(rng: random.Random) -> tuple[dict, list]:
    for _ in range(MAX_ATTEMPTS):
        k = rng.randint(2, 4)
        pairs = []
        ok = True
        for _ in range(k):
            pair = generate_random_c2_pair(rng)
            if pair is None:
                ok = False
                break
            pairs.append(pair)
        if not ok:
            continue
        if not is_nonconserving(pairs):
            continue
        rule = try_build_c2_rule(pairs)
        if rule is not None:
            return rule, pairs
    raise RuntimeError("Failed to generate a valid C2 rule after many attempts")


# ── Pair extraction ───────────────────────────────────────────────────────────

def extract_generator_pairs(rule_dict: dict) -> list:
    """
    Reverse-engineer the original (a, b) generator pairs from a saved C2 rule.

    Each generator pair (a, b) produces exactly 4 non-identity rule entries:
      a→b, b→a, rotate_c2(a)→rotate_c2(b), rotate_c2(b)→rotate_c2(a).
    Returns one canonical representative per orbit-of-4.
    """
    int_rule = {int(k): int(v) for k, v in rule_dict.items() if int(k) != int(v)}

    processed: set = set()
    pairs = []

    for a in sorted(int_rule.keys()):
        if a in processed:
            continue
        b  = int_rule[a]
        ra = rotate_c2(a)
        rb = rotate_c2(b)

        if (int_rule.get(b) != a or
                int_rule.get(ra) != rb or
                int_rule.get(rb) != ra):
            continue  # inconsistent entry — skip

        if len({a, b, ra, rb}) != 4:
            continue  # degenerate orbit

        pairs.append((a, b))
        processed.update({a, b, ra, rb})

    return pairs


# ── Crossover & mutation ──────────────────────────────────────────────────────

def breed_child(p1_dict: dict, p2_dict: dict, rng: random.Random) -> tuple[dict, list]:
    """
    Create a child rule by crossover and optional mutation.

    Takes a random half of the non-identity kernel pairs from each parent
    (floor(k/2), minimum 1 from each), producing a child with ~8 kernel pairs
    (2 generator pairs × 4 rule-entries each) when parents have k=2.
    Mutation (prob=MUTATION_PROB): replace one selected pair with a fresh
    random valid C2-symmetric pair.
    """
    pairs1 = extract_generator_pairs(p1_dict)
    pairs2 = extract_generator_pairs(p2_dict)

    if not pairs1 or not pairs2:
        return generate_random_c2_rule(rng)

    for _ in range(500):
        c1 = pairs1[:]
        c2 = pairs2[:]
        rng.shuffle(c1)
        rng.shuffle(c2)

        n1 = max(1, len(c1) // 2)
        n2 = max(1, len(c2) // 2)
        selected = c1[:n1] + c2[:n2]

        # Mutation: replace one pair with a new random valid C2 pair
        if rng.random() < MUTATION_PROB:
            new_pair = generate_random_c2_pair(rng)
            if new_pair is not None:
                idx = rng.randint(0, len(selected) - 1)
                selected = selected[:]
                selected[idx] = new_pair

        rule = try_build_c2_rule(selected)
        if rule is None:
            continue
        if not is_nonconserving(selected):
            continue
        return rule, selected

    # Fall back to random generation if crossover keeps failing
    return generate_random_c2_rule(rng)


# ── Grid simulation ───────────────────────────────────────────────────────────

def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lookup: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lookup[state]


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def count_objects(grid: np.ndarray, grid_size: int) -> int:
    live    = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    count   = 0
    for start in live:
        if start in visited:
            continue
        count += 1
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % grid_size, (r + dr) % grid_size)
                if nb in live and nb not in visited:
                    stack.append(nb)
    return count


def evaluate_rule_ash(rule_dict: dict, ash_grid: np.ndarray, grid_size: int) -> dict:
    lut  = rule_to_lut(rule_dict)
    grid = ash_grid.copy()
    com0 = center_of_mass(grid)

    for _ in range(STEPS):
        grid = step_grid(grid, lut)

    final_bits    = int(grid.sum())
    final_objects = count_objects(grid, grid_size)
    com1          = center_of_mass(grid)

    dq           = com1[0] - com0[0]
    dr           = com1[1] - com0[1]
    displacement = math.sqrt(dq * dq + dr * dr)

    denom   = 1.0 + abs(final_bits - INITIAL_BITS) + abs(final_objects - INITIAL_OBJECTS)
    fitness = displacement / denom

    return {
        "fitness":       fitness,
        "displacement":  displacement,
        "final_bits":    final_bits,
        "final_objects": final_objects,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    GEN2_POP_DIR.mkdir(parents=True, exist_ok=True)
    GEN2_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load Gen-1 results and identify elites ────────────────────────
    print("=== Step 1: Loading Gen-1 results ===", flush=True)
    with open(GEN1_CSV) as f:
        gen1_rows = list(csv.DictReader(f))

    gen1_fitnesses = [float(r["fitness"]) for r in gen1_rows]
    gen1_mean      = sum(gen1_fitnesses) / len(gen1_fitnesses)

    elites = [r for r in gen1_rows if float(r["fitness"]) > INERT_BASELINE]
    elites.sort(key=lambda r: float(r["fitness"]), reverse=True)

    print(f"  Gen-1 population size: {len(gen1_rows)}", flush=True)
    print(f"  Gen-1 mean fitness:    {gen1_mean:.8f}", flush=True)
    print(f"  Elites (> {INERT_BASELINE}): {len(elites)}", flush=True)
    for e in elites:
        print(f"    {e['rule_id']}: {float(e['fitness']):.8f}", flush=True)

    if len(elites) != N_ELITES:
        print(f"  WARNING: expected {N_ELITES} elites, found {len(elites)}", flush=True)

    # Load elite rule files
    elite_entries = []
    for e in elites:
        rule_path = GEN1_POP_DIR / e["rule_id"]
        with open(rule_path) as f:
            rule_dict = json.load(f)
        pairs = extract_generator_pairs(rule_dict)
        elite_entries.append({
            "rule_id":   e["rule_id"],
            "fitness":   float(e["fitness"]),
            "rule_dict": rule_dict,
            "pairs":     pairs,
        })
        print(f"  Loaded {e['rule_id']}: k={len(pairs)} generator pairs", flush=True)

    # ── Load ash pattern ──────────────────────────────────────────────────────
    print(f"\nLoading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits, {grid_size}x{grid_size} grid", flush=True)

    # ── Step 2: Build Gen-2 population ───────────────────────────────────────
    print(f"\n=== Step 2: Breeding Gen-2 population ({POPULATION_SIZE} rules) ===",
          flush=True)
    rng       = random.Random(122)
    gen2      = []
    elite_pool = [e["rule_dict"] for e in elite_entries]

    # Elitism: carry over top N_CARRY_OVER directly
    for i, elite in enumerate(elite_entries[:N_CARRY_OVER], 1):
        rule_id  = f"rule_{i:03d}"
        out_path = GEN2_POP_DIR / f"{rule_id}.json"
        rule_str = {str(k): v for k, v in elite["rule_dict"].items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        gen2.append({"rule_id": rule_id, "rule_dict": elite["rule_dict"]})
        print(f"  [carry-over] {rule_id} <- {elite['rule_id']} "
              f"(fitness={elite['fitness']:.6f})", flush=True)

    # Breed remaining
    for i in range(N_CARRY_OVER + 1, POPULATION_SIZE + 1):
        p1_dict, p2_dict = rng.sample(elite_pool, 2)
        rule_dict, pairs = breed_child(p1_dict, p2_dict, rng)

        rule_id  = f"rule_{i:03d}"
        out_path = GEN2_POP_DIR / f"{rule_id}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        gen2.append({"rule_id": rule_id, "rule_dict": rule_dict})

        if i % 10 == 0:
            print(f"  Bred {i}/{POPULATION_SIZE} ...", flush=True)

    print(f"  Saved {len(gen2)} rules to {GEN2_POP_DIR}", flush=True)

    # ── Step 3: Evaluate Gen-2 ────────────────────────────────────────────────
    print(f"\n=== Step 3: Evaluating {POPULATION_SIZE} rules ({STEPS} steps each) ===",
          flush=True)
    rows = []
    for entry in gen2:
        res    = evaluate_rule_ash(entry["rule_dict"], ash_grid, grid_size)
        marker = ""
        if res["fitness"] > GEN1_TOP:
            marker = " <-- BEATS GEN1 TOP"
        elif res["fitness"] > INERT_BASELINE:
            marker = " <-- BEATS BASELINE"
        print(f"  {entry['rule_id']}: fitness={res['fitness']:.6f}  "
              f"disp={res['displacement']:.4f}  "
              f"bits={res['final_bits']:5d}  "
              f"objs={res['final_objects']:4d}{marker}", flush=True)
        rows.append({
            "rule_id":       entry["rule_id"] + ".json",
            "fitness":       round(res["fitness"],      8),
            "displacement":  round(res["displacement"], 6),
            "final_bits":    res["final_bits"],
            "final_objects": res["final_objects"],
        })

    # ── Save CSV ──────────────────────────────────────────────────────────────
    csv_path   = GEN2_RESULTS_DIR / "fitness_scores.csv"
    fieldnames = ["rule_id", "fitness", "displacement", "final_bits", "final_objects"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {csv_path}", flush=True)

    # ── Step 4: Report & Compare ──────────────────────────────────────────────
    gen2_fitnesses      = [r["fitness"] for r in rows]
    gen2_mean           = sum(gen2_fitnesses) / len(gen2_fitnesses)
    gen2_top            = max(gen2_fitnesses)
    improvement_pct     = ((gen2_mean - gen1_mean) / gen1_mean * 100.0) if gen1_mean > 0 else 0.0
    beating_gen1_top    = sum(1 for f in gen2_fitnesses if f > GEN1_TOP)

    print(f"\n=== Summary ===", flush=True)
    print(f"  gen1_mean_fitness:           {gen1_mean:.8f}", flush=True)
    print(f"  gen2_mean_fitness:           {gen2_mean:.8f}", flush=True)
    print(f"  fitness_improvement_pct:     {improvement_pct:.2f}%", flush=True)
    print(f"  gen2_rules_beating_gen1_top: {beating_gen1_top}", flush=True)
    print(f"  gen2_top_fitness:            {gen2_top:.8f}", flush=True)

    yaml_result = {
        "gen1_mean_fitness":           round(float(gen1_mean),       8),
        "gen2_mean_fitness":           round(float(gen2_mean),       8),
        "fitness_improvement_pct":     round(float(improvement_pct), 4),
        "gen2_rules_beating_gen1_top": int(beating_gen1_top),
        "gen2_top_fitness":            round(float(gen2_top),        8),
    }
    with open(GEN2_RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {GEN2_RESULT_YAML}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
