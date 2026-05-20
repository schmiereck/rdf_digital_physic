#!/usr/bin/env python3
"""
show_com.py  -  Run the champion rule for 500 steps and report
                 unwrapped center-of-mass (CoM) coordinates and per-step velocities.

Unwrapping: on a toroidal grid the raw CoM wraps around (e.g. from 127 back to 0).
We detect wrap-around by looking for jumps larger than grid_size/2 in consecutive
steps and subtract/add the grid extent to keep the trajectory continuous.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, center_of_mass  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule.json"
GRID_SIZE = 128
STEPS = 500
REPORT_STEPS = [0, 100, 200, 300, 400, 500]
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_grid():
    """Create a 128x128 grid with the L-tromino seed."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1
    return grid


def unwrap_trajectory(coords, grid_size):
    """Unwrap a list of CoM tuples so the trajectory is continuous.

    Detects jumps > grid_size/2 and subtracts/adds grid_size to cancel
    toroidal wrap-around, producing a monotonically-unwrapped trajectory.

    Parameters
    ----------
    coords : list of (row, col) tuples -- the raw (wrapped) CoM per step.
    grid_size : int -- the linear dimension of the toroidal grid.

    Returns
    -------
    list of (row, col) tuples -- the unwrapped CoM per step.
    """
    HALF = grid_size / 2.0
    unwrapped = [coords[0]]  # start with first CoM

    for i in range(1, len(coords)):
        prev = unwrapped[-1]       # <-- UNWRAPPED previous
        curr = coords[i]           # <-- RAW current
        dx = curr[0] - prev[0]
        dy = curr[1] - prev[1]
        # Adjust for wrap-around
        if dx > HALF:
            dx -= grid_size
        elif dx < -HALF:
            dx += grid_size
        if dy > HALF:
            dy -= grid_size
        elif dy < -HALF:
            dy += grid_size
        unwrapped.append((prev[0] + dx, prev[1] + dy))

    return unwrapped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # --- Load champion rule ---
    print("=" * 70)
    print("CHAMPION RULE -- UNWRAPPED CENTER-OF-MASS REPORT")
    print("=" * 70)

    with open(CHAMPION_JSON) as f:
        champ = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)

    print(f"\nIteration:        iter_221")
    print(f"Fitness:          {champ['fitness']:.6f}")
    print(f"Fitness function: {champ['fitness_function']}")
    print(f"Grid size:        {champ['grid_size']}x{champ['grid_size']}")
    print(f"Seed:             {champ['seed_particle']}")
    print(f"Rule entries:     {len(rule_dict)} of 128")
    print()
    print("Rule dictionary (input_state -> new_centre_bit):")
    for k in sorted(rule_dict.keys()):
        print(f"  state {k:3d} (0b{k:07b}) -> {rule_dict[k]}")
    print()

    # --- Run simulation, recording raw CoM at every step ---
    grid = make_grid()
    raw_history = []  # list of (step, raw_com)

    for t in range(STEPS + 1):
        com = center_of_mass(grid)
        raw_history.append((t, com))

        if t < STEPS:
            grid = step_grid(grid, lut)

    # --- Extract raw CoM list ---
    raw_coms = [com for _, com in raw_history]

    # --- Unwrap the CoM trajectory ---
    unwrapped = unwrap_trajectory(raw_coms, GRID_SIZE)

    # --- Debug: show a few raw vs unwrapped values around wrap points ---
    print("--- Debug: raw vs unwrapped near wrap point ---")
    for t in range(295, 305):
        print(f"  step {t:3d}: raw=({raw_coms[t][0]:8.4f}, {raw_coms[t][1]:8.4f})  "
              f"unwrapped=({unwrapped[t][0]:8.4f}, {unwrapped[t][1]:8.4f})")
    print()

    # --- Print unwrapped CoM at checkpoint steps ---
    print("=" * 70)
    print("UNWRAPPED CENTER OF MASS")
    print("=" * 70)
    hdr = f"  {'Step':>6s} | {'Unwrapped Row':>16s} | {'Unwrapped Col':>16s} | {'Raw Row':>16s} | {'Raw Col':>16s}"
    print(hdr)
    print(f"  {'------':>6}  {'---------------':>16}  {'---------------':>16}  {'---------------':>16}  {'---------------':>16}")

    for t in REPORT_STEPS:
        raw_com = raw_history[t][1]
        uw_com = unwrapped[t]
        print(f"  {t:6d} | {uw_com[0]:16.6f} | {uw_com[1]:16.6f} | "
              f"{raw_com[0]:16.6f} | {raw_com[1]:16.6f}")

    print()

    # --- Per-step velocity between checkpoints ---
    print("=" * 70)
    print("PER-STEP VELOCITY BETWEEN CHECKPOINTS")
    print("=" * 70)

    velocities = []
    for i in range(len(REPORT_STEPS) - 1):
        t0 = REPORT_STEPS[i]
        t1 = REPORT_STEPS[i + 1]
        dt = t1 - t0

        uw0 = unwrapped[t0]
        uw1 = unwrapped[t1]
        dx = uw1[0] - uw0[0]
        dy = uw1[1] - uw0[1]
        dist = math.sqrt(dx ** 2 + dy ** 2)
        speed = dist / dt  # cells/step

        velocities.append(speed)

        print(f"  Steps {t0:4d} -- {t1:4d}: "
              f"d({dx:+8.4f}, {dy:+8.4f})  "
              f"distance = {dist:8.4f}  "
              f"speed  = {speed:8.6f} cells/step")

    print()

    # --- Overall summary ---
    uw_start = unwrapped[0]
    uw_end = unwrapped[STEPS]
    total_dx = uw_end[0] - uw_start[0]
    total_dy = uw_end[1] - uw_start[1]
    total_dist = math.sqrt(total_dx ** 2 + total_dy ** 2)
    avg_velocity = total_dist / STEPS

    print("=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)
    print(f"  Initial unwrapped CoM:  ({uw_start[0]:.4f}, {uw_start[1]:.4f})")
    print(f"  Final   unwrapped CoM:  ({uw_end[0]:.4f}, {uw_end[1]:.4f})")
    print(f"  Total displacement:     ({total_dx:+.4f}, {total_dy:+.4f})")
    print(f"  Total distance:         {total_dist:.4f} cells")
    print(f"  Steps:                  {STEPS}")
    print(f"  Average velocity:       {avg_velocity:.6f} cells/step")
    print()

    if avg_velocity > 0:
        # c = 1 cell/step in hex CA (light-speed)
        if avg_velocity < 1.0 / 3.0:
            speed_class = "sub-light (v < c/3)"
        elif avg_velocity < 0.4:
            speed_class = "sub-light (v ~ c/3)"
        else:
            speed_class = "super-light ? (v > c/3)"
        print(f"  Speed class: {speed_class}")

    print()
    print("=" * 70)
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
