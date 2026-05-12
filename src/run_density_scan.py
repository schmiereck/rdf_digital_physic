#!/usr/bin/env python3
"""
run_density_scan.py

Investigates the impact of rule density on the emergence of sustained motion.
Tests three density levels (4, 8, 16 kernel pairs) on the canonical ash pattern,
evaluating each population of 100 rules with the late-displacement fitness metric
(COM displacement between step 100 and step 200).
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
ITER_DIR         = PROJECT_ROOT / "archive" / "iter_129"
RESULTS_DIR      = ITER_DIR / "results"
RESULT_YAML      = ITER_DIR / "result.yaml"

POPULATION_SIZE = 100
STEPS           = 200
LATE_START      = 100
INITIAL_BITS    = 325
INITIAL_OBJECTS = 72
CHAOS_THRESHOLD = 1000
MAX_ATTEMPTS    = 50000

DENSITY_CONFIGS = [
    {"name": "low_density",    "n_pairs": 4,  "seed_base": 1000},
    {"name": "medium_density", "n_pairs": 8,  "seed_base": 2000},
    {"name": "high_density",   "n_pairs": 16, "seed_base": 3000},
]

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


def generate_c2_rule(n_pairs: int, seed: int) -> dict:
    """Generate a random C2-symmetric reversible rule with exactly n_pairs kernel pairs."""
    rng = random.Random(seed)
    for _ in range(MAX_ATTEMPTS):
        pairs: list       = []
        used_states: set  = set()
        ok = True
        for _ in range(n_pairs):
            found = False
            for _ in range(2000):
                a = rng.randint(1, 127)
                b = rng.randint(1, 127)
                if not is_valid_c2_pair(a, b):
                    continue
                ra = rotate_c2(a)
                rb = rotate_c2(b)
                states = {a, b, ra, rb}
                if states & used_states:
                    continue
                pairs.append((a, b))
                used_states.update(states)
                found = True
                break
            if not found:
                ok = False
                break
        if not ok:
            continue
        if not is_nonconserving(pairs):
            continue
        rule = try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(
        f"Failed to generate C2 rule with {n_pairs} pairs after {MAX_ATTEMPTS} attempts"
    )


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
    live     = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    count    = 0
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
        "fitness":           fitness,
        "late_displacement": displacement,
        "final_bits":        final_bits,
        "final_objects":     final_objects,
    }


# ── Density-level evaluation ──────────────────────────────────────────────────

def run_density_level(config: dict, ash_grid: np.ndarray,
                      grid_size: int) -> tuple[list, dict]:
    name      = config["name"]
    n_pairs   = config["n_pairs"]
    seed_base = config["seed_base"]

    print(f"\n=== {name} (n_pairs={n_pairs}, "
          f"{n_pairs * 4} non-identity mappings) ===", flush=True)

    rows = []
    for i in range(POPULATION_SIZE):
        rule_dict = generate_c2_rule(n_pairs, seed_base + i)
        res       = evaluate_rule_late_displacement(rule_dict, ash_grid, grid_size)

        is_chaotic = res["final_bits"] >= CHAOS_THRESHOLD
        is_viable  = res["fitness"] > 0.0 and not is_chaotic

        rows.append({
            "rule_id":           f"rule_{i:03d}",
            "fitness":           round(res["fitness"], 8),
            "late_displacement": round(res["late_displacement"], 6),
            "final_bits":        res["final_bits"],
            "final_objects":     res["final_objects"],
            "chaotic":           is_chaotic,
            "viable":            is_viable,
        })

        if (i + 1) % 10 == 0:
            print(f"  Evaluated {i+1}/{POPULATION_SIZE}  "
                  f"(last: bits={res['final_bits']:5d}  "
                  f"fitness={res['fitness']:.6f})", flush=True)

    fitnesses     = [r["fitness"] for r in rows]
    viable_count  = sum(1 for r in rows if r["viable"])
    chaotic_count = sum(1 for r in rows if r["chaotic"])
    static_count  = sum(1 for r in rows if not r["viable"] and not r["chaotic"])
    top_fitness   = max(fitnesses)
    mean_fitness  = float(np.mean(fitnesses))

    print(f"  viable={viable_count}  chaotic={chaotic_count}  "
          f"static={static_count}", flush=True)
    print(f"  top_fitness={top_fitness:.8f}  "
          f"mean_fitness={mean_fitness:.8f}", flush=True)

    summary = {
        "viable_rules":  viable_count,
        "top_fitness":   round(float(top_fitness), 8),
        "mean_fitness":  round(float(mean_fitness), 8),
        "chaotic_rules": chaotic_count,
        "static_rules":  static_count,
    }
    return rows, summary


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ITER_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading ash pattern ...", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    yaml_result: dict = {}
    fieldnames = ["rule_id", "fitness", "late_displacement", "final_bits",
                  "final_objects", "chaotic", "viable"]

    for config in DENSITY_CONFIGS:
        rows, summary = run_density_level(config, ash_grid, grid_size)
        yaml_result[config["name"]] = summary

        csv_path = RESULTS_DIR / f"{config['name']}_scores.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  Saved CSV: {csv_path}", flush=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved YAML: {RESULT_YAML}", flush=True)

    print("\n=== Final Summary ===", flush=True)
    for name, s in yaml_result.items():
        print(f"  {name}: viable={s['viable_rules']}  "
              f"chaotic={s['chaotic_rules']}  static={s['static_rules']}  "
              f"top={s['top_fitness']:.6f}  mean={s['mean_fitness']:.6f}",
              flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
