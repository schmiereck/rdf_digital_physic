#!/usr/bin/env python3
"""
Characterize the champion rule from archive/iter_221/results/champion_vc_rule.json.

1. Load the rule dictionary from the JSON file.
2. Initialize a 128x128 grid with the L-tromino seed.
3. Simulate it for 500 steps.
4. For each step, record step number, active cell count (bit count), and
   unwrapped center of mass coordinates (row, col).
5. Compute net displacement (Euclidean distance between CoM at step 0 and step 500).
6. Compute average speed (cells per step).
7. Print trajectory details: bit count at each 50 steps, final displacement,
   average speed.
8. Write results to 'archive/iter_221/results/trajectory_analysis.txt'.
"""

from __future__ import annotations

import json
import math
import numpy as np
import sys
from pathlib import Path

# The project root is: archive/iter_221/results/characterize_champion_221.py
#   -> parent: results
#   -> grandparent: iter_221
#   -> great-grandparent: archive
#   -> great-great-grandparent: project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHAMPION_JSON   = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_vc_rule.json"
OUTPUT_DIR      = PROJECT_ROOT / "archive" / "iter_221" / "results"
TRAJECTORY_LOG  = OUTPUT_DIR / "trajectory_analysis.txt"

GRID_SIZE       = 128
STEPS           = 500
SEED_CELLS      = [(63, 63), (64, 63), (64, 64)]       # L-tromino


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_grid() -> np.ndarray:
    """Create a 128x128 grid with the L-tromino seed."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1
    return grid


def active_cells(grid: np.ndarray) -> list[tuple[int, int]]:
    """Return sorted list of (row, col) positions of active cells."""
    rs, cs = np.where(grid > 0)
    return sorted(zip(rs.tolist(), cs.tolist()))


def unwrap_trajectory(raw_cell_lists: list[list[tuple[int, int]]]) -> list[tuple[float, float]]:
    """
    Robustly unwrap cell positions step-by-step to calculate true continuous
    unwrapped center-of-mass coordinates on a toroidal grid.

    Parameters
    ----------
    raw_cell_lists : list of active-cell coordinate lists, one per step.

    Returns
    -------
    list of (unwrapped_row, unwrapped_col) CoM per step.
    """
    if not raw_cell_lists or not raw_cell_lists[0]:
        return [(0.0, 0.0)] * (len(raw_cell_lists) + 1)

    unwrapped_history: list[tuple[float, float]] = []

    # --- step 0 ---
    unwrapped_prev = [np.array(c, dtype=float) for c in raw_cell_lists[0]]
    com_prev = float(np.mean(unwrapped_prev, axis=0)[0]), float(np.mean(unwrapped_prev, axis=0)[1])
    unwrapped_history.append(com_prev)

    for t in range(1, len(raw_cell_lists)):
        cells_t = raw_cell_lists[t]
        if not cells_t:
            unwrapped_history.append((0.0, 0.0))
            continue

        # Find the best alignment between one prev cell and one curr cell
        best_dist = float("inf")
        best_pair = None  # (p_idx, c_idx, toroidal_dr, toroidal_dc)
        for pi, pc in enumerate(unwrapped_prev):
            for ci, cc in enumerate(cells_t):
                dr = (cc[0] - int(pc[0]) + GRID_SIZE // 2) % GRID_SIZE - GRID_SIZE // 2
                dc = (cc[1] - int(pc[1]) + GRID_SIZE // 2) % GRID_SIZE - GRID_SIZE // 2
                d = dr * dr + dc * dc
                if d < best_dist:
                    best_dist = d
                    best_pair = (pi, ci, dr, dc)

        p_idx, c_idx, dr_t, dc_t = best_pair

        # Unwrapped position of current anchor cell
        anchor_unwrapped = unwrapped_prev[p_idx] + np.array([dr_t, dc_t])

        # Compute relative offsets of all current cells from the current anchor
        anchor_grid = cells_t[c_idx]
        unwrapped_curr = []
        for cc in cells_t:
            dr_r = (cc[0] - anchor_grid[0] + GRID_SIZE // 2) % GRID_SIZE - GRID_SIZE // 2
            dc_r = (cc[1] - anchor_grid[1] + GRID_SIZE // 2) % GRID_SIZE - GRID_SIZE // 2
            unwrapped_curr.append(anchor_unwrapped + np.array([dr_r, dc_r]))

        com_curr = float(np.mean(unwrapped_curr, axis=0)[0]), float(np.mean(unwrapped_curr, axis=0)[1])
        unwrapped_history.append(com_curr)
        unwrapped_prev = unwrapped_curr

    return unwrapped_history


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 70)
    print("ITER 221 CHAMPION RULE — TRAJECTORY ANALYSIS")
    print("=" * 70)

    # ---- 1. Load rule ----
    with open(CHAMPION_JSON) as f:
        champ = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)

    print(f"\nSeed        : {champ.get('seed_particle', 'L_TROMINO_3bit')}")
    print(f"Grid size   : {GRID_SIZE}x{GRID_SIZE} (toroidal)")
    print(f"Simulation  : {STEPS} steps")
    print(f"Rule entries: {len(rule_dict)} of 128")
    print(f"Rule dict   : {dict(rule_dict)}")
    print()

    # ---- 2-3. Simulate ----
    grid = make_grid()
    raw_history: list[list[tuple[int, int]]] = []

    for t in range(STEPS + 1):
        raw_history.append(active_cells(grid))
        if t < STEPS:
            grid = step_grid(grid, lut)

    # ---- 4. Unwrap CoM trajectory ----
    unwrapped_coms = unwrap_trajectory(raw_history)

    # Build per-step record
    records = []
    for t in range(STEPS + 1):
        ac = raw_history[t]
        bit_count = len(ac)
        com_u = unwrapped_coms[t]
        # raw CoM (wrapped toroidal)
        if ac:
            com_raw = (float(np.mean([c[0] for c in ac])),
                       float(np.mean([c[1] for c in ac])))
        else:
            com_raw = (0.0, 0.0)
        records.append({
            "step": t,
            "bit_count": bit_count,
            "com_raw": com_raw,
            "com_unwrapped": com_u,
            "active_cells": ac,
        })

    # ---- 5-6. Displacement & average speed ----
    com_start = unwrapped_coms[0]
    com_end   = unwrapped_coms[STEPS]
    dx_total  = com_end[0] - com_start[0]
    dy_total  = com_end[1] - com_start[1]
    net_displacement = math.sqrt(dx_total ** 2 + dy_total ** 2)
    avg_speed = net_displacement / STEPS

    # ---- 7. Print trajectory details ----
    print("=" * 70)
    print("BIT COUNT TIMELINE (every 50 steps)")
    print("=" * 70)
    print(f"  {'Step':>6}  {'Bit Count':>10}  {'CoM (raw)':<30}  {'CoM (unwrapped)':<35}")
    for t in range(0, STEPS + 1, 50):
        r = records[t]
        print(f"  {t:6d}  {r['bit_count']:10d}  "
              f"({r['com_raw'][0]:8.2f}, {r['com_raw'][1]:8.2f})  "
              f"({r['com_unwrapped'][0]:12.2f}, {r['com_unwrapped'][1]:12.2f})")
    print()

    print("=" * 70)
    print("DISPLACEMENT & SPEED")
    print("=" * 70)
    print(f"  Initial CoM   : ({com_start[0]:.6f}, {com_start[1]:.6f})")
    print(f"  Final CoM     : ({com_end[0]:.6f}, {com_end[1]:.6f})")
    print(f"  Net displacement: {net_displacement:.6f} cells")
    print(f"  Average speed : {avg_speed:.6f} cells/step")
    print(f"  Total delta   : dx={dx_total:+.6f}, dy={dy_total:+.6f}")
    print()

    # ---- 8. Write results file ----
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("=" * 80)
    lines.append(f"TRAJECTORY ANALYSIS — iter_221 champion rule")
    lines.append(f"Source: {CHAMPION_JSON.name}")
    lines.append(f"Grid : {GRID_SIZE}x{GRID_SIZE} (toroidal)")
    lines.append(f"Seed : {SEED_CELLS}  ({champ.get('seed_particle', 'N/A')})")
    lines.append(f"Steps: {STEPS}")
    lines.append("")
    lines.append("Rule dictionary:")
    for k in sorted(rule_dict):
        lines.append(f"  {k:3d} (0b{k:07b}) -> {rule_dict[k]}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("FULL TRAJECTORY LOG")
    lines.append("-" * 80)
    lines.append(f"  {'Step':>6}  {'Bit':>4}  {'CoM_raw':<30}  {'CoM_unwrapped':<35}  {'Active Cells':<40}")
    lines.append("  " + "-" * 75)

    for t in range(STEPS + 1):
        r = records[t]
        cells_str = str(r["active_cells"])[:36]
        lines.append(f"  {t:6d}  {r['bit_count']:4d}  "
                     f"({r['com_raw'][0]:8.2f}, {r['com_raw'][1]:8.2f})  "
                     f"({r['com_unwrapped'][0]:12.2f}, {r['com_unwrapped'][1]:12.2f})  "
                     f"{cells_str}")

    lines.append("")
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"  Initial CoM   : ({com_start[0]:.6f}, {com_start[1]:.6f})")
    lines.append(f"  Final CoM     : ({com_end[0]:.6f}, {com_end[1]:.6f})")
    lines.append(f"  Net displacement (Euclidean): {net_displacement:.6f} cells")
    lines.append(f"  Total delta    : dx={dx_total:+.6f}, dy={dy_total:+.6f}")
    lines.append(f"  Average speed  : {avg_speed:.6f} cells/step")
    lines.append("")

    # Bit count stats
    bits = [r["bit_count"] for r in records]
    lines.append(f"  Bit count — min: {min(bits)}, max: {max(bits)}, final: {bits[-1]}")
    lines.append("")

    # Step velocities (unwrapped)
    step_vels = []
    for t in range(1, STEPS + 1):
        dr = unwrapped_coms[t][0] - unwrapped_coms[t - 1][0]
        dc = unwrapped_coms[t][1] - unwrapped_coms[t - 1][1]
        step_vels.append(math.sqrt(dr * dr + dc * dc))
    if step_vels:
        lines.append(f"  Step velocity — min: {min(step_vels):.6f}, max: {max(step_vels):.6f}, mean: {np.mean(step_vels):.6f}")

    lines.append("")
    lines.append("=" * 80)
    TRAJECTORY_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Results written to: {TRAJECTORY_LOG}")
    print("=" * 70)
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
