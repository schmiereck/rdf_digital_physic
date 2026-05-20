#!/usr/bin/env python3
"""
run_iter_220_trajectory.py

Full 500-step simulation of the champion rule from iter_220
with L-tromino seed on a 128x128 grid.

Outputs:
  - Center of mass at steps 0, 100, 200, 300, 400, 500
  - Movement classification (moving, oscillating, stationary)
  - Average velocity
  - Trajectory log saved to archive/iter_220/results/trajectory_log.txt
"""

import json
import math
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, center_of_mass

# -- Configuration --

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_rule.json"
OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_220" / "results"
TRAJECTORY_LOG = OUTPUT_DIR / "trajectory_log.txt"

GRID_SIZE = 128
STEPS = 500
L_TROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]

# Steps at which to report center of mass
REPORT_STEPS = [0, 100, 200, 300, 400, 500]


# -- Helpers --

def make_grid():
    """Create a 128x128 grid with the L-tromino seed."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in L_TROMINO_CELLS:
        grid[r, c] = 1
    return grid


def get_active_cells(grid):
    """Return sorted list of (row, col) positions of all active cells."""
    rows, cols = np.where(grid > 0)
    return sorted(zip(rows.tolist(), cols.tolist()))


def get_relative_pattern(grid):
    """Get a canonical relative pattern (for period detection)."""
    cells = get_active_cells(grid)
    if not cells:
        return None
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    return tuple((r - min_r, c - min_c) for r, c in cells)


# -- Main --

def main():
    # Load champion rule
    print("=" * 70)
    print("ITER 220 CHAMPION RULE -- TRAJECTORY ANALYSIS")
    print("=" * 70)

    with open(CHAMPION_JSON) as f:
        champ = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)

    print(f"\nFitness:          {champ['fitness']:.6f}")
    print(f"Fitness function: {champ['fitness_function']}")
    print(f"Grid size:        {champ['grid_size']}x{champ['grid_size']}")
    print(f"Seed:             {champ['seed_particle']}")
    print(f"Seed cells:       {champ['seed_cells']}")
    print(f"Rule entries:     {len(rule_dict)} (of 128 possible)")
    print()
    print("Rule dictionary (input_state -> new_centre_bit):")
    for k in sorted(rule_dict.keys()):
        print(f"  state {k:3d} (0b{k:07b}) -> {rule_dict[k]}")
    print()

    # Run simulation
    grid = make_grid()
    history = []  # list of (step, com, active_cells, relative_pattern)

    for t in range(STEPS + 1):
        com = center_of_mass(grid)
        active = get_active_cells(grid)
        rel = get_relative_pattern(grid)
        history.append({
            "step": t,
            "com": com,
            "bit_count": int(grid.sum()),
            "active_cells": active,
            "relative_pattern": rel,
        })

        if t < STEPS:
            grid = step_grid(grid, lut)

    # -- Analysis --

    # Center of mass at requested steps
    print("=" * 70)
    print("CENTER OF MASS REPORT")
    print("=" * 70)
    for t in REPORT_STEPS:
        h = history[t]
        com = h["com"]
        print(f"  Step {t:4d}: CoM = ({com[0]:>12.6f}, {com[1]:>12.6f}), "
              f"active cells = {h['bit_count']}")
    print()

    # Displacement between report steps
    print("DISPLACEMENT BETWEEN REPORT STEPS:")
    for i in range(len(REPORT_STEPS) - 1):
        t0 = REPORT_STEPS[i]
        t1 = REPORT_STEPS[i + 1]
        com0 = history[t0]["com"]
        com1 = history[t1]["com"]
        dx = com1[0] - com0[0]
        dy = com1[1] - com0[1]
        dist = math.sqrt(dx ** 2 + dy ** 2)
        speed = dist / (t1 - t0)
        print(f"  Steps {t0:4d} - {t1:4d}: Delta({dx:+.6f}, {dy:+.6f}), "
              f"dist = {dist:.6f}, speed = {speed:.6f} cells/step")
    print()

    # Overall velocity
    com_start = history[0]["com"]
    com_end = history[STEPS]["com"]
    total_dx = com_end[0] - com_start[0]
    total_dy = com_end[1] - com_start[1]
    total_dist = math.sqrt(total_dx ** 2 + total_dy ** 2)
    avg_velocity = total_dist / STEPS

    print("=" * 70)
    print("VELOCITY ANALYSIS")
    print("=" * 70)
    print(f"  Initial CoM:  ({com_start[0]:.6f}, {com_start[1]:.6f})")
    print(f"  Final CoM:    ({com_end[0]:.6f}, {com_end[1]:.6f})")
    print(f"  Total Delta:  ({total_dx:+.6f}, {total_dy:+.6f})")
    print(f"  Total dist:   {total_dist:.6f} cells")
    print(f"  Steps:        {STEPS}")
    print(f"  Avg velocity: {avg_velocity:.6f} cells/step")
    print()

    # Movement classification
    print("=" * 70)
    print("MOVEMENT CLASSIFICATION")
    print("=" * 70)

    # Collect per-step velocities (using adjacent steps)
    velocities = []
    for t in range(1, STEPS + 1):
        dx = history[t]["com"][0] - history[t - 1]["com"][0]
        dy = history[t]["com"][1] - history[t - 1]["com"][1]
        v = math.sqrt(dx ** 2 + dy ** 2)
        velocities.append(v)

    max_vel = max(velocities) if velocities else 0
    mean_vel = np.mean(velocities) if velocities else 0
    non_zero_steps = sum(1 for v in velocities if v > 1e-9)
    zero_steps = STEPS - non_zero_steps

    print(f"  Max step velocity:    {max_vel:.6f}")
    print(f"  Mean step velocity:   {mean_vel:.6f}")
    print(f"  Steps with motion:    {non_zero_steps} / {STEPS}")
    print(f"  Steps stationary:     {zero_steps} / {STEPS}")

    # Period detection -- look for the same relative pattern repeating
    patterns = []
    for h in history:
        patterns.append(h["relative_pattern"])

    period = None
    period_offset = None
    period_dx = None
    period_dy = None

    # Look for repeated relative patterns in the latter half
    search_start = STEPS // 2
    for i in range(search_start):
        if patterns[i] is None:
            continue
        for j in range(i + 1, min(i + search_start + 1, STEPS + 1)):
            if patterns[j] is None:
                continue
            if patterns[j] == patterns[i]:
                p_dx = history[j]["com"][0] - history[i]["com"][0]
                p_dy = history[j]["com"][1] - history[i]["com"][1]
                period = j - i
                period_offset = i
                period_dx = p_dx
                period_dy = p_dy
                break
        if period is not None:
            break

    print(f"\n  Period detection:")
    if period is not None:
        print(f"    Period found: {period} steps (offset at step {period_offset})")
        print(f"    Displacement per cycle: ({period_dx:.6f}, {period_dy:.6f})")
        cycle_speed = math.sqrt(period_dx ** 2 + period_dy ** 2) / period
        print(f"    Cycle speed: {cycle_speed:.6f} cells/step")
    else:
        print("    No exact period detected.")

    # Classification
    if avg_velocity < 1e-6:
        classification = "STATIONARY"
    elif zero_steps > STEPS * 0.7:
        classification = "OSCILLATING"
    else:
        classification = "MOVING"

    print()
    print(f"  >>> CLASSIFICATION: {classification}")
    print(f"     Avg velocity = {avg_velocity:.6f} cells/step")
    if avg_velocity > 0:
        if avg_velocity < 1 / 3:
            speed_class = "v < c/3"
        elif avg_velocity < 0.4:
            speed_class = "v ~ c/3"
        else:
            speed_class = "v > c/3"
        print(f"     Speed class: {speed_class}")
    print()

    # -- Write trajectory log --

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append(f"TRAJECTORY LOG -- iter_220 champion rule")
    log_lines.append(f"Seed: {champ['seed_particle']} at {champ['seed_cells']}")
    log_lines.append(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Steps: {STEPS}")
    log_lines.append(f"Rule entries: {len(rule_dict)}")
    log_lines.append(f"")
    log_lines.append(f"Rule dictionary:")
    for k in sorted(rule_dict.keys()):
        log_lines.append(f"  {k:3d} (0b{k:07b}) -> {rule_dict[k]}")
    log_lines.append(f"")
    log_lines.append("=" * 80)
    log_lines.append(f"STEP | CoM_row           | CoM_col           | Active | d_row  | d_col  | Speed")
    log_lines.append("-" * 100)

    prev_com = history[0]["com"]
    for t in range(STEPS + 1):
        h = history[t]
        com = h["com"]
        dc = h["bit_count"]
        dr = com[0] - prev_com[0]
        dcol = com[1] - prev_com[1]
        spd = math.sqrt(dr ** 2 + dcol ** 2)
        marker = " ***" if t in REPORT_STEPS else ""
        log_lines.append(
            f"{t:4d} | {com[0]:19.6f} | {com[1]:19.6f} | {dc:8d} | "
            f"{dr:+8.6f} | {dcol:+8.6f} | {spd:.6f}{marker}"
        )
        prev_com = com

    log_lines.append("-" * 100)
    log_lines.append("")
    log_lines.append(f"SUMMARY")
    log_lines.append("=" * 80)
    log_lines.append(f"Classification:    {classification}")
    log_lines.append(f"Avg velocity:      {avg_velocity:.8f} cells/step")
    log_lines.append(f"Total displacement: ({total_dx:.6f}, {total_dy:.6f})")
    log_lines.append(f"Total distance:    {total_dist:.6f} cells")
    if period is not None:
        log_lines.append(f"Period:            {period} steps (offset {period_offset})")
        log_lines.append(f"Cycle disp:        ({period_dx:.6f}, {period_dy:.6f})")
    log_lines.append(f"Max step speed:    {max_vel:.6f}")
    log_lines.append(f"Mean step speed:   {mean_vel:.6f}")
    log_lines.append(f"Motion steps:      {non_zero_steps}/{STEPS}")
    log_lines.append(f"Stationary steps:  {zero_steps}/{STEPS}")
    log_lines.append("")
    log_lines.append("=" * 80)
    log_lines.append("ACTIVE CELL COORDINATES (selected steps)")
    log_lines.append("-" * 80)
    for t in REPORT_STEPS:
        h = history[t]
        log_lines.append(f"Step {t}:")
        for r, c in h["active_cells"]:
            log_lines.append(f"  ({r:3d}, {c:3d})")
        log_lines.append("")
    log_lines.append("=" * 80)

    TRAJECTORY_LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"\nTrajectory log saved to: {TRAJECTORY_LOG}")
    print("=" * 70)
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
