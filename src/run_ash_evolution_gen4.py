#!/usr/bin/env python3
"""
run_ash_evolution_gen4.py

Breeds and evaluates a fourth generation of ash-animating C2-symmetric rules.

1. Load 5 Gen-3 elite rules.
2. Breed 100 Gen-4 rules via crossover + 10% mutation.
3. Evaluate each rule with a late-displacement fitness metric
   (COM displacement between step 100 and step 200).
4. Save results to archive/iter_127/.
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

ELITE_PATHS = [
    PROJECT_ROOT / "archive" / "iter_122" / "population" / "rule_010.json",
    PROJECT_ROOT / "archive" / "iter_122" / "population" / "rule_055.json",
    PROJECT_ROOT / "archive" / "iter_123" / "population" / "rule_001.json",
    PROJECT_ROOT / "archive" / "iter_123" / "population" / "rule_002.json",
    PROJECT_ROOT / "archive" / "iter_123" / "population" / "rule_007.json",
]

GEN4_POP_DIR     = PROJECT_ROOT / "archive" / "iter_127" / "population"
GEN4_RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_127" / "results"
GEN4_RESULT_YAML = PROJECT_ROOT / "archive" / "iter_127" / "result.yaml"

POPULATION_SIZE = 100
STEPS           = 200
LATE_START      = 100
MAX_ATTEMPTS    = 10000
INITIAL_BITS    = 325
INITIAL_OBJECTS = 72
MUTATION_PROB   = 0.10

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


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
        k     = rng.randint(2, 4)
        pairs = []
        ok    = True
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
    int_rule  = {int(k): int(v) for k, v in rule_dict.items() if int(k) != int(v)}
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
            continue
        if len({a, b, ra, rb}) != 4:
            continue
        pairs.append((a, b))
        processed.update({a, b, ra, rb})
    return pairs


# ── Crossover & mutation ──────────────────────────────────────────────────────

def breed_child(p1_dict: dict, p2_dict: dict, rng: random.Random) -> tuple[dict, list]:
    pairs1 = extract_generator_pairs(p1_dict)
    pairs2 = extract_generator_pairs(p2_dict)

    if not pairs1 or not pairs2:
        return generate_random_c2_rule(rng)

    for _ in range(500):
        c1 = pairs1[:]
        c2 = pairs2[:]
        rng.shuffle(c1)
        rng.shuffle(c2)

        n1       = max(1, len(c1) // 2)
        n2       = max(1, len(c2) // 2)
        selected = c1[:n1] + c2[:n2]

        if rng.random() < MUTATION_PROB:
            new_pair = generate_random_c2_pair(rng)
            if new_pair is not None:
                idx      = rng.randint(0, len(selected) - 1)
                selected = selected[:]
                selected[idx] = new_pair

        rule = try_build_c2_rule(selected)
        if rule is None:
            continue
        if not is_nonconserving(selected):
            continue
        return rule, selected

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


def evaluate_rule_late_displacement(rule_dict: dict, ash_grid: np.ndarray,
                                    grid_size: int) -> dict:
    lut  = rule_to_lut(rule_dict)
    grid = ash_grid.copy()

    for _ in range(LATE_START):
        grid = step_grid(grid, lut)

    com_100 = center_of_mass(grid)

    for _ in range(STEPS - LATE_START):
        grid = step_grid(grid, lut)

    com_200       = center_of_mass(grid)
    final_bits    = int(grid.sum())
    final_objects = count_objects(grid, grid_size)

    dq           = com_200[0] - com_100[0]
    dr           = com_200[1] - com_100[1]
    displacement = math.sqrt(dq * dq + dr * dr)

    denom   = 1.0 + abs(final_bits - INITIAL_BITS) + abs(final_objects - INITIAL_OBJECTS)
    fitness = displacement / denom

    return {
        "fitness":            fitness,
        "late_displacement":  displacement,
        "final_bits":         final_bits,
        "final_objects":      final_objects,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    GEN4_POP_DIR.mkdir(parents=True, exist_ok=True)
    GEN4_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load elites and ash pattern ──────────────────────────────────
    print("=== Step 1: Loading Gen-3 elite rules ===", flush=True)
    elite_pool = []
    for path in ELITE_PATHS:
        with open(path) as f:
            rule_dict = json.load(f)
        pairs = extract_generator_pairs(rule_dict)
        elite_pool.append(rule_dict)
        print(f"  Loaded {path.parent.name}/{path.name}: k={len(pairs)} pairs",
              flush=True)

    print(f"\nLoading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits, {grid_size}x{grid_size} grid", flush=True)

    # ── Step 2: Breed Gen-4 population ───────────────────────────────────────
    print(f"\n=== Step 2: Breeding Gen-4 population ({POPULATION_SIZE} rules) ===",
          flush=True)
    rng  = random.Random(127)
    gen4 = []

    for i in range(1, POPULATION_SIZE + 1):
        p1_dict, p2_dict = rng.sample(elite_pool, 2)
        rule_dict, _pairs = breed_child(p1_dict, p2_dict, rng)

        rule_id  = f"rule_{i:03d}"
        out_path = GEN4_POP_DIR / f"{rule_id}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        gen4.append({"rule_id": rule_id, "rule_dict": rule_dict})

        if i % 10 == 0:
            print(f"  Bred {i}/{POPULATION_SIZE} ...", flush=True)

    print(f"  Saved {len(gen4)} rules to {GEN4_POP_DIR}", flush=True)

    # ── Step 3: Evaluate Gen-4 with late-displacement metric ─────────────────
    print(f"\n=== Step 3: Evaluating {POPULATION_SIZE} rules "
          f"({STEPS} steps, late-displacement from step {LATE_START}) ===",
          flush=True)
    rows = []
    for entry in gen4:
        res = evaluate_rule_late_displacement(entry["rule_dict"], ash_grid, grid_size)
        print(f"  {entry['rule_id']}: fitness={res['fitness']:.8f}  "
              f"late_disp={res['late_displacement']:.4f}  "
              f"bits={res['final_bits']:5d}  objs={res['final_objects']:4d}",
              flush=True)
        rows.append({
            "rule_id":           entry["rule_id"] + ".json",
            "fitness":           round(res["fitness"],           8),
            "late_displacement": round(res["late_displacement"], 6),
            "final_bits":        res["final_bits"],
            "final_objects":     res["final_objects"],
        })

    # ── Save CSV ──────────────────────────────────────────────────────────────
    csv_path   = GEN4_RESULTS_DIR / "fitness_scores.csv"
    fieldnames = ["rule_id", "fitness", "late_displacement", "final_bits", "final_objects"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {csv_path}", flush=True)

    # ── Step 4: Compute summary metrics ──────────────────────────────────────
    fitnesses            = [r["fitness"] for r in rows]
    top_fitness          = max(fitnesses)
    best_row             = max(rows, key=lambda r: r["fitness"])
    rules_with_motion    = sum(1 for f in fitnesses if f > 1e-6)

    print(f"\n=== Summary ===", flush=True)
    print(f"  top_fitness_score:            {top_fitness:.8f}", flush=True)
    print(f"  top_rule_id:                  {best_row['rule_id']}", flush=True)
    print(f"  top_rule_displacement_100_200:{best_row['late_displacement']:.6f}", flush=True)
    print(f"  top_rule_final_bits:          {best_row['final_bits']}", flush=True)
    print(f"  top_rule_final_objects:       {best_row['final_objects']}", flush=True)
    print(f"  rules_with_sustained_motion:  {rules_with_motion}", flush=True)

    yaml_result = {
        "population_size":              POPULATION_SIZE,
        "rules_with_sustained_motion":  int(rules_with_motion),
        "top_fitness_score":            round(float(top_fitness), 8),
        "top_rule_id":                  best_row["rule_id"],
        "top_rule_displacement_100_200": round(float(best_row["late_displacement"]), 6),
        "top_rule_final_bits":          int(best_row["final_bits"]),
        "top_rule_final_objects":       int(best_row["final_objects"]),
    }
    with open(GEN4_RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {GEN4_RESULT_YAML}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
