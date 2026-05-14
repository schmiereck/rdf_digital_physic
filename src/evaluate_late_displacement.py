#!/usr/bin/env python3
"""
evaluate_late_displacement.py

Evaluate the late-displacement fitness metric for rule_021 (champion from iter_153).

Metric: Euclidean distance between center-of-mass at step 1200 and step 2000.
A rule that has settled (stopped moving) by step 1200 will score near zero.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RULE_FILE    = PROJECT_ROOT / "archive" / "iter_153" / "results" / "population_gen3.json"
RULE_ID      = "rule_021"
GRID_SIZE    = 150
DENSITY      = 0.25
SEED         = 21
TOTAL_STEPS  = 2000
COM_T1       = 1200
COM_T2       = 2000
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_156" / "results"
RESULT_YAML  = OUTPUT_DIR / "results.yaml"


def _rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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
    return lut[state]


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def main() -> int:
    print(f"Loading {RULE_ID} from {RULE_FILE}")
    with open(RULE_FILE) as f:
        population = json.load(f)

    if RULE_ID not in population:
        print(f"[error] {RULE_ID} not found in {RULE_FILE}", file=sys.stderr)
        return 1

    rule_dict = population[RULE_ID]
    print(f"Rule {RULE_ID}: {len(rule_dict)} entries")

    lut  = _rule_to_lut(rule_dict)
    rng  = np.random.default_rng(SEED)
    grid = (rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"Soup: {GRID_SIZE}x{GRID_SIZE}, density={DENSITY}, seed={SEED}")
    print(f"Running {TOTAL_STEPS} steps, recording CoM at t={COM_T1} and t={COM_T2} ...")

    com_1200 = None
    com_2000 = None

    for t in range(1, TOTAL_STEPS + 1):
        grid = _step_grid(grid, lut)
        if t == COM_T1:
            com_1200 = _center_of_mass(grid)
            print(f"  t={COM_T1}: CoM = {com_1200}")
        if t == COM_T2:
            com_2000 = _center_of_mass(grid)
            print(f"  t={COM_T2}: CoM = {com_2000}")

    dx = com_2000[0] - com_1200[0]
    dy = com_2000[1] - com_1200[1]
    late_displacement = math.sqrt(dx * dx + dy * dy)

    print(f"\nlate_displacement_fitness = {late_displacement:.6f}")
    print(f"  CoM at t={COM_T1}: ({com_1200[0]:.4f}, {com_1200[1]:.4f})")
    print(f"  CoM at t={COM_T2}: ({com_2000[0]:.4f}, {com_2000[1]:.4f})")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "rule_id":                    RULE_ID,
        "late_displacement_fitness":  round(late_displacement, 6),
        "com_at_t1200":               [round(com_1200[0], 4), round(com_1200[1], 4)],
        "com_at_t2000":               [round(com_2000[0], 4), round(com_2000[1], 4)],
        "grid_size":                  GRID_SIZE,
        "density":                    DENSITY,
        "seed":                       SEED,
        "total_steps":                TOTAL_STEPS,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
