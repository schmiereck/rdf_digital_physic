#!/usr/bin/env python3
"""
run_ash_evolution_gen1.py

Generates 100 random, reversible, C2-symmetric, non-conserving rules and
evaluates each using the ash-based displacement fitness metric from iter_120:

    fitness = displacement / (1 + |final_bits - initial_bits|
                                + |final_objects - initial_objects|)

Rules use the iter_095 generation method: k in [2, 4] kernel pairs per rule.
Simulation: 150x150 grid, 200 steps, starting from the canonical ash pattern.
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
POP_DIR          = PROJECT_ROOT / "archive" / "iter_121" / "population"
RESULTS_DIR      = PROJECT_ROOT / "archive" / "iter_121" / "results"
RESULT_YAML      = PROJECT_ROOT / "archive" / "iter_121" / "result.yaml"

POPULATION_SIZE = 100
STEPS           = 200
MAX_ATTEMPTS    = 10000
INITIAL_BITS    = 325
INITIAL_OBJECTS = 72
INERT_BASELINE  = 0.052432

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


# ── C2-symmetric rule generation ──────────────────────────────────────────────
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


def generate_random_c2_rule(rng: random.Random) -> tuple[dict, list]:
    for _ in range(MAX_ATTEMPTS):
        k = rng.randint(2, 4)
        pairs = []
        all_found = True
        for _ in range(k):
            pair_found = False
            for _attempt in range(200):
                a = rng.randint(1, 127)
                b = rng.randint(1, 127)
                if is_valid_c2_pair(a, b):
                    pairs.append((a, b))
                    pair_found = True
                    break
            if not pair_found:
                all_found = False
                break

        if not all_found:
            continue
        if not is_nonconserving(pairs):
            continue

        rule = try_build_c2_rule(pairs)
        if rule is not None:
            return rule, pairs

    raise RuntimeError("Failed to generate a valid C2 rule after many attempts")


# ── Grid simulation ────────────────────────────────────────────────────────────

def rule_to_lut(rule_dict: dict) -> np.ndarray:
    """Convert rule dict (int -> int) to 128-element LUT returning new center bit."""
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


def center_of_mass(grid: np.ndarray):
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def count_objects(grid: np.ndarray, grid_size: int) -> int:
    """Count connected components (6-connected toroidal hex grid)."""
    live    = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    count   = 0

    for start in live:
        if start in visited:
            continue
        count += 1
        stack  = [start]
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


# ── Ash-based fitness evaluation ───────────────────────────────────────────────

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


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    POP_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)

    grid_size = ash_data["grid_size"]
    cells     = ash_data["cells"]

    ash_grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in cells:
        ash_grid[q, r] = 1

    print(f"Ash pattern: {INITIAL_BITS} bits, {INITIAL_OBJECTS} objects "
          f"({grid_size}x{grid_size} grid)", flush=True)

    # ── Step 1: Generate population ───────────────────────────────────────────
    print(f"\n=== Step 1: Generating {POPULATION_SIZE} random C2-symmetric rules ===",
          flush=True)
    rng = random.Random(121)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict, _pairs = generate_random_c2_rule(rng)
        rule_id  = f"rule_{i:03d}"
        out_path = POP_DIR / f"{rule_id}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        rules.append({"rule_id": rule_id, "rule_dict": rule_dict, "path": out_path})
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE} ...", flush=True)

    print(f"  Saved {POPULATION_SIZE} rules to {POP_DIR}", flush=True)

    # ── Step 2: Ash-based evaluation ───────────────────────────────────────────
    print(f"\n=== Step 2: Evaluating {POPULATION_SIZE} rules ({STEPS} steps each) ===",
          flush=True)
    rows = []
    for entry in rules:
        res = evaluate_rule_ash(entry["rule_dict"], ash_grid, grid_size)
        marker = " <-- BEATS BASELINE" if res["fitness"] > INERT_BASELINE else ""
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

    # ── Step 3: Save CSV ───────────────────────────────────────────────────────
    csv_path = RESULTS_DIR / "fitness_scores.csv"
    fieldnames = ["rule_id", "fitness", "displacement", "final_bits", "final_objects"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {csv_path}", flush=True)

    # ── Step 4: Build result.yaml ──────────────────────────────────────────────
    beating = [r for r in rows if r["fitness"] > INERT_BASELINE]
    top_row = max(rows, key=lambda r: r["fitness"])

    print(f"\n=== Summary ===", flush=True)
    print(f"  population_size:        {POPULATION_SIZE}", flush=True)
    print(f"  inert_baseline_fitness: {INERT_BASELINE}", flush=True)
    print(f"  rules_beating_baseline: {len(beating)}", flush=True)
    print(f"  top_fitness_score:      {top_row['fitness']:.8f}", flush=True)
    print(f"  top_rule_id:            {top_row['rule_id']}", flush=True)
    print(f"  top_rule_displacement:  {top_row['displacement']:.6f}", flush=True)
    print(f"  top_rule_final_bits:    {top_row['final_bits']}", flush=True)
    print(f"  top_rule_final_objects: {top_row['final_objects']}", flush=True)

    yaml_result = {
        "population_size":        POPULATION_SIZE,
        "inert_baseline_fitness": INERT_BASELINE,
        "rules_beating_baseline": len(beating),
        "top_fitness_score":      round(float(top_row["fitness"]),      8),
        "top_rule_id":            top_row["rule_id"],
        "top_rule_displacement":  round(float(top_row["displacement"]), 6),
        "top_rule_final_bits":    int(top_row["final_bits"]),
        "top_rule_final_objects": int(top_row["final_objects"]),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
