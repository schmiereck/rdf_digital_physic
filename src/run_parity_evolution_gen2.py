#!/usr/bin/env python3
"""
run_parity_evolution_gen2.py

Breeds a Gen-2 population from the three viable Gen-1 parity-constrained
C2 founders (rule_002, rule_051, rule_024) discovered in iter_138.

Breeding plan (100 children):
  33  from crossover(rule_002, rule_051)
  33  from crossover(rule_051, rule_024)
  34  from crossover(rule_024, rule_002)

10 randomly selected children are mutated (one kernel pair replaced).

Fitness metric: identical to iter_138
  initial state : ash_pattern.json (150x150, 325 bits)
  simulation    : 200 steps with wrapping
  displacement  : COM distance between step 100 and step 200
  bit_ratio     : final_bits / 325
  fitness       : displacement / (1 + (bit_ratio - 1)**2)
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
GEN1_POP_DIR     = PROJECT_ROOT / "archive" / "iter_138" / "population"
ITER_DIR         = PROJECT_ROOT / "archive" / "iter_139"
POPULATION_DIR   = ITER_DIR / "population"
RESULTS_DIR      = ITER_DIR / "results"
RESULT_YAML      = ITER_DIR / "result.yaml"
CSV_PATH         = RESULTS_DIR / "gen2_scores.csv"

POPULATION_SIZE  = 100
STEPS            = 200
LATE_START       = 100
INITIAL_BITS     = 325
N_PAIRS          = 8
N_MUTATIONS      = 10
BREED_SEED       = 139
MAX_BREED_RETRIES = 500
MAX_PAIR_TRIES   = 4000

GEN1_RULE_IDS    = ["rule_002", "rule_051", "rule_024"]
GEN1_TOP_FITNESS = 0.36059001


# ── C2-symmetric rule helpers ─────────────────────────────────────────────────

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def is_valid_c2_pair(a: int, b: int) -> bool:
    if a == b or a == 0 or b == 0:
        return False
    ra = rotate_c2(a)
    rb = rotate_c2(b)
    return len({a, b, ra, rb}) == 4


def is_parity_conserving_pair(a: int, b: int) -> bool:
    """True iff popcount(A) % 2 == popcount(B) % 2."""
    return bin(a).count('1') % 2 == bin(b).count('1') % 2


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


def _pairs_have_conflict(pairs: list) -> bool:
    used: set = set()
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        states = {a, b, ra, rb}
        if states & used:
            return True
        used.update(states)
    return False


def extract_c2_generator_pairs(rule_dict: dict) -> list:
    """Recover the N_PAIRS generator pairs from a C2 rule dict."""
    seen  = set()
    pairs = []
    for a_str, b in rule_dict.items():
        a = int(a_str)
        b = int(b)
        if a == b or a in seen:
            continue
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        seen.update({a, b, ra, rb})
        pairs.append((a, b))
    return pairs


# ── Genetic operators ─────────────────────────────────────────────────────────

def crossover(p1_pairs: list, p2_pairs: list, rng: random.Random) -> list:
    """
    Create a child rule by taking 4 distinct kernel pairs from each parent.
    Both parent pair lists are shuffled independently before splitting.
    """
    p1 = list(p1_pairs)
    p2 = list(p2_pairs)
    rng.shuffle(p1)
    rng.shuffle(p2)
    return p1[:4] + p2[:4]


def generate_random_parity_conserving_pair(
    used_states: set, rng: random.Random, max_tries: int = MAX_PAIR_TRIES
) -> tuple | None:
    """Random valid C2 pair satisfying parity conservation, avoiding used_states."""
    for _ in range(max_tries):
        a = rng.randint(1, 127)
        b = rng.randint(1, 127)
        if not is_valid_c2_pair(a, b):
            continue
        if not is_parity_conserving_pair(a, b):
            continue
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        if {a, b, ra, rb} & used_states:
            continue
        return (a, b)
    return None


def mutate(pairs: list, rng: random.Random) -> list:
    """
    Replace one randomly chosen kernel pair with a new valid parity-conserving pair.
    Returns the original list unchanged if no valid replacement is found.
    """
    pairs = list(pairs)
    idx = rng.randrange(len(pairs))

    used: set = set()
    for i, (a, b) in enumerate(pairs):
        if i == idx:
            continue
        used.update({a, b, rotate_c2(a), rotate_c2(b)})

    new_pair = generate_random_parity_conserving_pair(used, rng)
    if new_pair is not None:
        pairs[idx] = new_pair
    return pairs


def breed_child(
    p1_pairs: list, p2_pairs: list, rng: random.Random, do_mutate: bool
) -> dict | None:
    """Breed one child via 4+4 crossover, optionally mutate, validate, build rule."""
    for _ in range(MAX_BREED_RETRIES):
        candidate = crossover(p1_pairs, p2_pairs, rng)
        if do_mutate:
            candidate = mutate(candidate, rng)
        if len(candidate) != N_PAIRS:
            continue
        if _pairs_have_conflict(candidate):
            continue
        if not is_nonconserving(candidate):
            continue
        rule = try_build_c2_rule(candidate)
        if rule is not None:
            return rule
    return None


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


def evaluate_rule(rule_dict: dict, ash_grid: np.ndarray) -> dict:
    """Identical fitness metric to iter_138 (run_parity_constrained_search.py)."""
    lut  = rule_to_lut(rule_dict)
    grid = ash_grid.copy()

    for _ in range(LATE_START):
        grid = step_grid(grid, lut)

    com_100 = center_of_mass(grid)

    for _ in range(STEPS - LATE_START):
        grid = step_grid(grid, lut)

    com_200    = center_of_mass(grid)
    final_bits = int(grid.sum())

    dq           = com_200[0] - com_100[0]
    dr           = com_200[1] - com_100[1]
    displacement = math.sqrt(dq * dq + dr * dr)
    bit_ratio    = final_bits / INITIAL_BITS
    fitness      = displacement / (1.0 + (bit_ratio - 1.0) ** 2)

    return {
        "displacement": displacement,
        "final_bits":   final_bits,
        "bit_ratio":    bit_ratio,
        "fitness":      fitness,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load ash pattern ──────────────────────────────────────────────────────
    print("Loading ash pattern ...", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    # ── Load Gen-1 founders ───────────────────────────────────────────────────
    print("\nLoading Gen-1 founders from iter_138 ...", flush=True)
    gen1 = {}
    for rule_id in GEN1_RULE_IDS:
        path = GEN1_POP_DIR / f"{rule_id}.json"
        with open(path) as f:
            rule_dict = {int(k): int(v) for k, v in json.load(f).items()}
        pairs = extract_c2_generator_pairs(rule_dict)
        gen1[rule_id] = {"rule_dict": rule_dict, "pairs": pairs}
        print(f"  {rule_id}: {len(pairs)} generator pairs", flush=True)

    # ── Re-evaluate Gen-1 founders ────────────────────────────────────────────
    print("\nRe-evaluating Gen-1 founders ...", flush=True)
    gen1_fitnesses = []
    for rule_id in GEN1_RULE_IDS:
        res = evaluate_rule(gen1[rule_id]["rule_dict"], ash_grid)
        gen1[rule_id]["fitness"] = res["fitness"]
        gen1_fitnesses.append(res["fitness"])
        print(
            f"  {rule_id}: fitness={res['fitness']:.6f}  "
            f"disp={res['displacement']:.4f}  bit_ratio={res['bit_ratio']:.3f}",
            flush=True,
        )
    gen1_mean = float(np.mean(gen1_fitnesses))
    gen1_top  = float(np.max(gen1_fitnesses))
    print(f"  Gen-1 mean fitness: {gen1_mean:.6f}", flush=True)
    print(f"  Gen-1 top fitness:  {gen1_top:.6f}", flush=True)

    # ── Breed Gen-2 population ────────────────────────────────────────────────
    # 33 from (rule_002, rule_051)
    # 33 from (rule_051, rule_024)
    # 34 from (rule_024, rule_002)
    breeding_plan = (
        [("rule_002", "rule_051")] * 33
        + [("rule_051", "rule_024")] * 33
        + [("rule_024", "rule_002")] * 34
    )

    rng        = random.Random(BREED_SEED)
    mutate_set = set(rng.sample(range(POPULATION_SIZE), N_MUTATIONS))
    print(
        f"\nBreeding {POPULATION_SIZE} Gen-2 rules "
        f"(mutate_set={sorted(mutate_set)}) ...",
        flush=True,
    )

    population = []
    failed     = 0
    for i, (pid1, pid2) in enumerate(breeding_plan):
        rule_id    = f"rule_{i:03d}"
        do_mutate  = i in mutate_set
        p1_pairs   = gen1[pid1]["pairs"]
        p2_pairs   = gen1[pid2]["pairs"]

        rule_d = breed_child(p1_pairs, p2_pairs, rng, do_mutate)
        if rule_d is None:
            failed += 1
            print(
                f"  WARNING: breed failed for {rule_id} ({pid1}x{pid2}), cloning {pid1}",
                flush=True,
            )
            rule_d = gen1[pid1]["rule_dict"]

        population.append({
            "rule_id": rule_id,
            "rule_dict": rule_d,
            "parents": f"{pid1}x{pid2}",
            "mutated": do_mutate,
        })

        rule_str  = {str(k): v for k, v in rule_d.items()}
        rule_path = POPULATION_DIR / f"{rule_id}.json"
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True)

        if (i + 1) % 10 == 0:
            print(f"  Bred {i+1}/{POPULATION_SIZE}", flush=True)

    print(f"  Breed failures: {failed}", flush=True)

    # ── Evaluate Gen-2 population ─────────────────────────────────────────────
    print(f"\nEvaluating {POPULATION_SIZE} Gen-2 rules ({STEPS} steps) ...", flush=True)
    rows = []
    for entry in population:
        rule_id   = entry["rule_id"]
        rule_dict = entry["rule_dict"]
        res       = evaluate_rule(rule_dict, ash_grid)

        rows.append({
            "rule_id":      rule_id,
            "fitness":      round(res["fitness"], 8),
            "displacement": round(res["displacement"], 6),
            "final_bits":   res["final_bits"],
            "bit_ratio":    round(res["bit_ratio"], 6),
            "parents":      entry["parents"],
            "mutated":      entry["mutated"],
        })

        if (len(rows)) % 10 == 0:
            r = rows[-1]
            print(
                f"  [{len(rows):3d}/{POPULATION_SIZE}] {r['rule_id']}: "
                f"fitness={r['fitness']:.6f}  disp={r['displacement']:.4f}  "
                f"bit_ratio={r['bit_ratio']:.3f}  parents={r['parents']}"
                + ("  [MUTATED]" if r["mutated"] else ""),
                flush=True,
            )

    # ── Summary statistics ────────────────────────────────────────────────────
    fitnesses        = [r["fitness"] for r in rows]
    gen2_mean        = float(np.mean(fitnesses))
    gen2_top         = float(np.max(fitnesses))
    best_row         = max(rows, key=lambda r: r["fitness"])
    beating_gen1_top = sum(1 for f in fitnesses if f > GEN1_TOP_FITNESS)
    improvement_pct  = (gen2_mean - gen1_mean) / gen1_mean * 100.0 if gen1_mean > 0 else 0.0

    print("\n=== Gen-1 vs Gen-2 Summary ===", flush=True)
    print(f"  gen1_mean_fitness:        {gen1_mean:.8f}", flush=True)
    print(f"  gen2_mean_fitness:        {gen2_mean:.8f}", flush=True)
    print(f"  fitness_improvement_pct:  {improvement_pct:+.4f}%", flush=True)
    print(f"  gen1_top_fitness:         {gen1_top:.8f}", flush=True)
    print(f"  gen2_top_fitness:         {gen2_top:.8f}", flush=True)
    print(f"  rules_beating_gen1_top:   {beating_gen1_top}", flush=True)
    print(f"  best_rule_id:             {best_row['rule_id']}", flush=True)
    print(f"  breed_failures:           {failed}", flush=True)

    # ── Save CSV ──────────────────────────────────────────────────────────────
    fieldnames = [
        "rule_id", "fitness", "displacement", "final_bits",
        "bit_ratio", "parents", "mutated",
    ]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {CSV_PATH}", flush=True)

    # ── Save result.yaml ──────────────────────────────────────────────────────
    result = {
        "gen1_mean_fitness":        round(gen1_mean, 8),
        "gen2_mean_fitness":        round(gen2_mean, 8),
        "fitness_improvement_pct":  round(improvement_pct, 4),
        "gen1_top_fitness":         round(gen1_top, 8),
        "gen2_top_fitness":         round(gen2_top, 8),
        "rules_beating_gen1_top":   int(beating_gen1_top),
        "best_rule_id":             best_row["rule_id"],
        "breed_failures":           int(failed),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
