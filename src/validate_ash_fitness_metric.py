#!/usr/bin/env python3
"""
validate_ash_fitness_metric.py

Loads the canonical ash pattern (src/ash_pattern.json) and evaluates
a displacement-based fitness metric for two rules:

  Inert rule : src/symmetric_rule_nonconserving_A3_B14.json
  Chaotic rule: archive/iter_084/population/rule_023.json

Fitness = displacement / (1 + |initial_bits - final_bits|
                              + |initial_objects - final_objects|)

where displacement is the Euclidean distance the center of mass travels
from step 0 to step 500.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT     = Path(__file__).parent.parent
ASH_PATTERN_PATH = Path(__file__).parent / "ash_pattern.json"
INERT_RULE_PATH  = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
CHAOTIC_RULE_PATH = PROJECT_ROOT / "archive" / "iter_084" / "population" / "rule_023.json"
RESULT_YAML      = PROJECT_ROOT / "archive" / "iter_120" / "result.yaml"

STEPS = 500

# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


# ── Rule loading ───────────────────────────────────────────────────────────────

def load_lookup(path: Path) -> np.ndarray:
    """128-element uint8 LUT: index = 7-bit neighborhood, value = new center bit."""
    with open(path) as f:
        raw = json.load(f)
    lut = np.arange(128, dtype=np.uint8)
    for k, v in raw.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Grid stepping ──────────────────────────────────────────────────────────────

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


# ── Geometry helpers ───────────────────────────────────────────────────────────

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


# ── Evaluation ─────────────────────────────────────────────────────────────────

def evaluate_rule(rule_path: Path, ash_grid: np.ndarray,
                  initial_bits: int, initial_objects: int,
                  grid_size: int, label: str) -> dict:
    lookup = load_lookup(rule_path)
    grid   = ash_grid.copy()

    com0 = center_of_mass(grid)
    print(f"\n  [{label}] Starting simulation ({STEPS} steps) ...", flush=True)

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lookup)
        if t % 100 == 0:
            print(f"    Step {t:4d}: bit_count={int(grid.sum()):6d}", flush=True)

    final_bits    = int(grid.sum())
    final_objects = count_objects(grid, grid_size)
    com1          = center_of_mass(grid)

    dq           = com1[0] - com0[0]
    dr           = com1[1] - com0[1]
    displacement = math.sqrt(dq * dq + dr * dr)

    denom   = 1.0 + abs(initial_bits - final_bits) + abs(initial_objects - final_objects)
    fitness = displacement / denom

    print(f"    final_bits={final_bits}  final_objects={final_objects}  "
          f"displacement={displacement:.4f}  fitness={fitness:.6f}")

    return {
        "final_bits":    final_bits,
        "final_objects": final_objects,
        "displacement":  displacement,
        "fitness":       fitness,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading ash pattern: {ASH_PATTERN_PATH}")
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)

    grid_size     = ash_data["grid_size"]
    initial_bits  = ash_data["bit_count"]
    cells         = ash_data["cells"]

    ash_grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in cells:
        ash_grid[q, r] = 1

    initial_objects = count_objects(ash_grid, grid_size)
    print(f"Ash pattern: {initial_bits} bits, {initial_objects} objects "
          f"({grid_size}x{grid_size} grid)")

    inert_res   = evaluate_rule(INERT_RULE_PATH,   ash_grid, initial_bits,
                                initial_objects, grid_size, "inert_rule")
    chaotic_res = evaluate_rule(CHAOTIC_RULE_PATH, ash_grid, initial_bits,
                                initial_objects, grid_size, "chaotic_rule")

    print("\n=== Summary ===")
    print(f"  initial_ash_bits:        {initial_bits}")
    print(f"  initial_ash_objects:     {initial_objects}")
    print(f"  inert_rule_fitness:      {inert_res['fitness']:.6f}")
    print(f"  inert_rule_final_bits:   {inert_res['final_bits']}")
    print(f"  chaotic_rule_fitness:    {chaotic_res['fitness']:.6f}")
    print(f"  chaotic_rule_final_bits: {chaotic_res['final_bits']}")

    yaml_result = {
        "initial_ash_bits":        initial_bits,
        "initial_ash_objects":     initial_objects,
        "inert_rule_fitness":      round(inert_res["fitness"],   8),
        "inert_rule_final_bits":   inert_res["final_bits"],
        "inert_rule_displacement": round(inert_res["displacement"], 4),
        "chaotic_rule_fitness":    round(chaotic_res["fitness"],  8),
        "chaotic_rule_final_bits": chaotic_res["final_bits"],
        "chaotic_rule_displacement": round(chaotic_res["displacement"], 4),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
