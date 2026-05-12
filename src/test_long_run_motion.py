#!/usr/bin/env python3
"""
test_long_run_motion.py

Long-duration simulation of the top-evolved rule from iter_131 (rule_011)
on the canonical ash pattern.  Verifies whether sustained motion persists
over 1000 steps.
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
RULE_PATH        = PROJECT_ROOT / "archive" / "iter_131" / "population" / "rule_011.json"
ASH_PATTERN_PATH = SRC_DIR / "ash_pattern.json"
RESULTS_DIR      = PROJECT_ROOT / "archive" / "iter_132" / "results"
CSV_PATH         = RESULTS_DIR / "long_run_metrics.csv"
RESULT_YAML_PATH = PROJECT_ROOT / "archive" / "iter_132" / "result.yaml"

TOTAL_STEPS  = 1000
LOG_INTERVAL = 20
GRID_SIZE    = 200

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

    print(f"Loading rule: {RULE_PATH}", flush=True)
    with open(RULE_PATH) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)
    print(f"  Rule has {len(rule_dict)} non-identity mappings", flush=True)

    print(f"Loading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        if q < GRID_SIZE and r < GRID_SIZE:
            grid[q, r] = 1
    print(f"  {int(grid.sum())} bits on {GRID_SIZE}x{GRID_SIZE} grid", flush=True)

    com0 = center_of_mass(grid)
    print(f"  Initial COM: ({com0[0]:.4f}, {com0[1]:.4f})", flush=True)

    print(f"\nRunning {TOTAL_STEPS} steps (logging every {LOG_INTERVAL})...", flush=True)
    time_series = []

    def record(step: int, g: np.ndarray):
        com = center_of_mass(g)
        dq  = com[0] - com0[0]
        dr  = com[1] - com0[1]
        disp = math.sqrt(dq * dq + dr * dr)
        bits = int(g.sum())
        objs = count_objects(g, GRID_SIZE)
        time_series.append({
            "step":         step,
            "bit_count":    bits,
            "object_count": objs,
            "com_q":        round(com[0], 6),
            "com_r":        round(com[1], 6),
            "displacement": round(disp, 8),
        })
        print(f"  step={step:4d}  disp={disp:.6f}  bits={bits:5d}  objs={objs:4d}",
              flush=True)

    record(0, grid)

    for s in range(1, TOTAL_STEPS + 1):
        grid = step_grid(grid, lut)
        if s % LOG_INTERVAL == 0:
            record(s, grid)

    fieldnames = ["step", "bit_count", "object_count", "com_q", "com_r", "displacement"]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(time_series)
    print(f"\nSaved CSV: {CSV_PATH}", flush=True)

    by_step = {row["step"]: row for row in time_series}
    initial_bit_count = by_step[0]["bit_count"]
    bits_200          = by_step[200]["bit_count"]
    bits_1000         = by_step[1000]["bit_count"]
    disp_200          = by_step[200]["displacement"]
    disp_1000         = by_step[1000]["displacement"]

    remnant_stable   = bool(abs(bits_1000 - bits_200) / max(bits_200, 1) <= 0.05)
    motion_sustained = bool(disp_1000 > 4.5 * disp_200)

    ratio = (disp_1000 / disp_200) if disp_200 > 0 else float("inf")
    linear_note = (
        "Displacement grew roughly linearly (5x ratio expected for constant velocity; "
        f"observed {ratio:.2f}x)."
        if abs(ratio - 5.0) < 1.5
        else f"Displacement ratio was {ratio:.2f}x (expected ~5x for constant velocity)."
    )
    stability_note = (
        "Remnant form was stable (bit count within 5% between step 200 and 1000)."
        if remnant_stable
        else f"Remnant form changed: {bits_200} bits at step 200 vs {bits_1000} at step 1000."
    )

    print(f"\n=== Results ===", flush=True)
    print(f"  initial_bit_count:          {initial_bit_count}", flush=True)
    print(f"  final_bit_count:            {bits_1000}", flush=True)
    print(f"  remnant_stable:             {remnant_stable}", flush=True)
    print(f"  displacement_at_200_steps:  {disp_200}", flush=True)
    print(f"  displacement_at_1000_steps: {disp_1000}", flush=True)
    print(f"  motion_sustained:           {motion_sustained}", flush=True)

    result_doc = {
        "status": "ok",
        "metrics": {
            "initial_bit_count":          initial_bit_count,
            "final_bit_count":            bits_1000,
            "remnant_stable":             remnant_stable,
            "displacement_at_200_steps":  round(disp_200, 8),
            "displacement_at_1000_steps": round(disp_1000, 8),
            "motion_sustained":           motion_sustained,
        },
        "experimenter_view": (
            f"rule_011 from iter_131 was run for 1000 steps on the canonical ash pattern "
            f"(200x200 grid with wrapping boundaries).  "
            f"{linear_note}  "
            f"{stability_note}  "
            f"motion_sustained={motion_sustained} "
            f"(criterion: disp_1000 > 4.5 * disp_200; {disp_1000:.4f} vs {4.5 * disp_200:.4f})."
        ),
    }

    with open(RESULT_YAML_PATH, "w") as f:
        yaml.dump(result_doc, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML_PATH}", flush=True)

    print(f"""
---
status: ok
artifacts:
  - "archive/iter_132/result.yaml"
  - "archive/iter_132/results/long_run_metrics.csv"
metrics:
  initial_bit_count: {initial_bit_count}
  final_bit_count: {bits_1000}
  remnant_stable: {str(remnant_stable).lower()}
  displacement_at_200_steps: {disp_200}
  displacement_at_1000_steps: {disp_1000}
  motion_sustained: {str(motion_sustained).lower()}
log_excerpt: |
  step=   0  disp=0.000000  bits={by_step[0]['bit_count']:5d}  objs={by_step[0]['object_count']:4d}
  step= 200  disp={disp_200:.6f}  bits={bits_200:5d}  objs={by_step[200]['object_count']:4d}
  step=1000  disp={disp_1000:.6f}  bits={bits_1000:5d}  objs={by_step[1000]['object_count']:4d}
experimenter_view: |
  {result_doc['experimenter_view']}
notes: iter_132 long-run verification of rule_011 motion over 1000 steps
""", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
