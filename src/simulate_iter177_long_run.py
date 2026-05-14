#!/usr/bin/env python3
"""
simulate_iter177_long_run.py

Load champion rule from iter_176 gen_5 (rule_019.json) and the L-tromino seed.
Run 2000 steps on a 128x128 toroidal hexagonal grid, tracking per-step:
  step, com_x, com_y, bit_count.
Save to archive/iter_177/results/long_run_metrics.csv.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT  = Path(__file__).parent.parent
RULE_PATH     = PROJECT_ROOT / "archive" / "iter_176" / "results" / "gen_5" / "rule_019.json"
PARTICLE_PATH = PROJECT_ROOT / "archive" / "iter_176" / "results" / "best_particle.json"
RESULTS_DIR   = PROJECT_ROOT / "archive" / "iter_177" / "results"
CSV_OUT       = RESULTS_DIR / "long_run_metrics.csv"

GRID_SIZE = 128
STEPS     = 2000


def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,     1, axis=1)
    nw = np.roll(w,    -1, axis=1)
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


def center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return 0.0, 0.0
    return float(np.mean(cols)), float(np.mean(rows))  # (com_x, com_y)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RULE_PATH) as f:
        data = json.load(f)
    rule_dict = data["rule"]
    print(f"Loaded rule: {data['rule_id']}  ({len(rule_dict)} transitions, fitness={data['fitness']})")

    with open(PARTICLE_PATH) as f:
        particle_data = json.load(f)
    cells = particle_data["cells"]
    print(f"Loaded seed: {len(cells)} cells at {cells}")

    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in cells:
        grid[r, c] = 1

    records = []
    com_x, com_y = center_of_mass(grid)
    records.append((0, com_x, com_y, int(grid.sum())))

    print(f"\nRunning {STEPS} steps on {GRID_SIZE}x{GRID_SIZE} toroidal grid...")
    print(f"Step    0: bit_count={records[0][3]}, com=({com_x:.3f}, {com_y:.3f})")

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        com_x, com_y = center_of_mass(grid)
        bc = int(grid.sum())
        records.append((t, com_x, com_y, bc))
        if t % 200 == 0:
            print(f"Step {t:5d}: bit_count={bc}, com=({com_x:.3f}, {com_y:.3f})")

    initial_bc = records[0][3]
    final_bc   = records[-1][3]
    initial_com = (records[0][1], records[0][2])
    final_com   = (records[-1][1], records[-1][2])
    displacement = ((final_com[0] - initial_com[0])**2 + (final_com[1] - initial_com[1])**2)**0.5

    print(f"\n=== Simulation Complete ===")
    print(f"Initial bit_count: {initial_bc}")
    print(f"Final   bit_count: {final_bc}")
    print(f"Bit count stable:  {initial_bc == final_bc}")
    print(f"Initial CoM: ({initial_com[0]:.3f}, {initial_com[1]:.3f})")
    print(f"Final   CoM: ({final_com[0]:.3f}, {final_com[1]:.3f})")
    print(f"Total displacement: {displacement:.3f}")

    # Linearity check: fit com_x vs step, compute R²
    steps_arr = np.array([r[0] for r in records], dtype=float)
    comx_arr  = np.array([r[1] for r in records], dtype=float)
    comy_arr  = np.array([r[2] for r in records], dtype=float)
    px = np.polyfit(steps_arr, comx_arr, 1)
    py = np.polyfit(steps_arr, comy_arr, 1)
    res_x = comx_arr - np.polyval(px, steps_arr)
    res_y = comy_arr - np.polyval(py, steps_arr)
    r2_x = 1 - np.var(res_x) / (np.var(comx_arr) + 1e-12)
    r2_y = 1 - np.var(res_y) / (np.var(comy_arr) + 1e-12)
    print(f"Linearity R² com_x: {r2_x:.6f}  (vx={px[0]:.6f} cells/step)")
    print(f"Linearity R² com_y: {r2_y:.6f}  (vy={py[0]:.6f} cells/step)")

    with open(CSV_OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "com_x", "com_y", "bit_count"])
        for row in records:
            writer.writerow([row[0], f"{row[1]:.4f}", f"{row[2]:.4f}", row[3]])
    print(f"\nSaved CSV: {CSV_OUT} ({len(records)} rows)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
