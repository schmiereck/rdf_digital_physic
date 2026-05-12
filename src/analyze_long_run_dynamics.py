#!/usr/bin/env python3
"""
analyze_long_run_dynamics.py

Runs the top Gen-3 rule (rule_001) on the canonical ash pattern for 500 steps,
logging displacement, bit count, and object count every 10 steps.
"""

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT     = Path(__file__).parent.parent
SRC_DIR          = Path(__file__).parent
RULE_PATH        = PROJECT_ROOT / "archive" / "iter_123" / "population" / "rule_001.json"
ASH_PATTERN_PATH = SRC_DIR / "ash_pattern.json"
RESULTS_DIR      = PROJECT_ROOT / "archive" / "iter_125" / "results"
CSV_PATH         = RESULTS_DIR / "long_run_data.csv"
RESULT_YAML_PATH = PROJECT_ROOT / "archive" / "iter_125" / "result.yaml"

TOTAL_STEPS   = 500
LOG_INTERVAL  = 10

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


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


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load rule
    print(f"Loading rule: {RULE_PATH}", flush=True)
    with open(RULE_PATH) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)
    print(f"  Rule has {len(rule_dict)} non-identity mappings", flush=True)

    # Load ash pattern
    print(f"Loading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        grid[q, r] = 1
    print(f"  {int(grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    # Initial center of mass (reference point for displacement)
    com0 = center_of_mass(grid)
    print(f"  Initial COM: ({com0[0]:.4f}, {com0[1]:.4f})", flush=True)

    # Run simulation, logging every LOG_INTERVAL steps
    print(f"\nRunning {TOTAL_STEPS} steps (logging every {LOG_INTERVAL})...", flush=True)
    time_series = []

    def record(step: int, g: np.ndarray):
        com = center_of_mass(g)
        dq = com[0] - com0[0]
        dr = com[1] - com0[1]
        disp = math.sqrt(dq * dq + dr * dr)
        bits = int(g.sum())
        objs = count_objects(g, grid_size)
        time_series.append({
            "step":         step,
            "displacement": round(disp, 8),
            "bit_count":    bits,
            "object_count": objs,
        })
        print(f"  step={step:4d}  disp={disp:.6f}  bits={bits:5d}  objs={objs:4d}",
              flush=True)

    # Record step 0 before any simulation
    record(0, grid)

    for s in range(1, TOTAL_STEPS + 1):
        grid = step_grid(grid, lut)
        if s % LOG_INTERVAL == 0:
            record(s, grid)

    # Save CSV
    fieldnames = ["step", "displacement", "bit_count", "object_count"]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(time_series)
    print(f"\nSaved CSV: {CSV_PATH}", flush=True)

    # Extract metrics
    by_step = {row["step"]: row for row in time_series}
    disp_100  = by_step[100]["displacement"]
    disp_500  = by_step[500]["displacement"]
    bits_500  = by_step[500]["bit_count"]
    objs_500  = by_step[500]["object_count"]
    motion_sustained = bool(disp_500 >= 4.0 * disp_100)

    print(f"\n=== Results ===", flush=True)
    print(f"  displacement_at_100_steps: {disp_100}", flush=True)
    print(f"  displacement_at_500_steps: {disp_500}", flush=True)
    print(f"  final_bit_count:           {bits_500}", flush=True)
    print(f"  final_object_count:        {objs_500}", flush=True)
    print(f"  motion_sustained:          {motion_sustained}", flush=True)

    result = {
        "displacement_at_100_steps": disp_100,
        "displacement_at_500_steps": disp_500,
        "final_bit_count":           bits_500,
        "final_object_count":        objs_500,
        "motion_sustained":          motion_sustained,
    }
    with open(RESULT_YAML_PATH, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML_PATH}", flush=True)

    # Standard execution status block
    print(f"""
---
status: ok
artifacts:
  - "archive/iter_125/result.yaml"
  - "archive/iter_125/results/long_run_data.csv"
metrics:
  displacement_at_100_steps: {disp_100}
  displacement_at_500_steps: {disp_500}
  final_bit_count: {bits_500}
  final_object_count: {objs_500}
  motion_sustained: {str(motion_sustained).lower()}
log_excerpt: |
  step=   0  disp=0.000000  bits={by_step[0]['bit_count']:5d}  objs={by_step[0]['object_count']:4d}
  step= 100  disp={disp_100:.6f}  bits={by_step[100]['bit_count']:5d}  objs={by_step[100]['object_count']:4d}
  step= 500  disp={disp_500:.6f}  bits={bits_500:5d}  objs={objs_500:4d}
experimenter_view: |
  Top Gen-3 rule (rule_001) run for 500 steps on the canonical ash pattern.
  Displacement at 500 steps vs 100 steps ratio: {disp_500 / disp_100 if disp_100 > 0 else 'inf':.4f}x
  motion_sustained={motion_sustained} (threshold: 4x displacement growth)
notes: ""
""", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
