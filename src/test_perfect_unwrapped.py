#!/usr/bin/env python3
"""
test_perfect_unwrapped.py
=========================

Implements the spatially unwrapped ``com_and_bits`` and a step-by-step
``continuous_com`` simulation loop.

1. Loads the champion rule from archive/iter_221/results/champion_rule.json
2. Runs a 500-step simulation with spatially unwrapped CoM tracking
3. Prints unwrapped COM at steps 0, 100, 200, 300, 400, 500
4. Prints the resulting DisplacementConsistencyFitness score
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, GRID_SIZE            # noqa: E402
from new_fitness import DisplacementConsistencyFitness                  # noqa: E402


# ── helpers ──────────────────────────────────────────────────────────────────

def com_and_bits(grid):
    """Return (raw_toroidal_COM, bit_count) for a grid.

    Parameters
    ----------
    grid : np.ndarray of uint8, shape (H, W)

    Returns
    -------
    com : (row, col) tuple
        Centre of mass in toroidal coordinates [0, grid_size).
    bits : int
        Number of live cells.
    """
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())


def _unwrap_com(prev_com, raw_com, grid_size=GRID_SIZE):
    """Unwrap one raw CoM step relative to the previous raw CoM.

    The grid wraps at *grid_size*.  If the difference between
    consecutive raw CoM positions exceeds half the grid size in either
    direction, we subtract/add *grid_size* to remove the toroidal
    discontinuity.
    """
    pr, pc = prev_com
    cr, cc = raw_com
    half   = grid_size / 2.0

    dr = cr - pr
    dc = cc - pc

    if dr > half:
        cr -= grid_size
    elif dr < -half:
        cr += grid_size

    if dc > half:
        cc -= grid_size
    elif dc < -half:
        cc += grid_size

    return (cr, cc)


def continuous_com(rule_dict, steps, seed_cells, grid_size=GRID_SIZE):
    """Run the CA simulation step-by-step, recording unwrapped CoM every step.

    Parameters
    ----------
    rule_dict   : dict[int, int]
    steps       : int
    seed_cells  : list of (row, col)
    grid_size   : int

    Returns
    -------
    history : list[dict]   -- each entry has 'step', 'com' (unwrapped),
                              'bit_count', 'grid'
    """
    lut = rule_dict_to_lut(rule_dict)
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in seed_cells:
        grid[r, c] = 1

    history = []

    # Initial snapshot
    raw_c0, b0 = com_and_bits(grid)
    prev_raw = (raw_c0[0], raw_c0[1])      # raw CoM at step 0 (anchor)
    history.append({
        "step": 0,
        "com": (prev_raw[0], prev_raw[1]),  # step 0 unwrapped = raw
        "bit_count": b0,
        "grid": grid.copy(),
    })

    # Step-by-step loop
    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = com_and_bits(grid)

        # Unwrap the raw CoM relative to the PREVIOUS RAW CoM
        unwrapped = _unwrap_com(prev_raw, raw_c, grid_size)
        prev_raw = raw_c

        history.append({
            "step": t,
            "com": unwrapped,
            "bit_count": bc,
            "grid": grid.copy(),
        })

    return history


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    # 1. Load champion rule ────────────────────────────────────────────────
    champion_path = (
        PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule.json"
    )
    with open(champion_path) as f:
        champion = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champion["rule_dict"].items()}
    seed_cells = champion["seed_cells"]
    grid_size = champion.get("grid_size", GRID_SIZE)
    steps = champion.get("horizon", 500)

    sep = "=" * 78
    thsep = "-" * 78

    print(sep)
    print("  PERFECT UNWRAPPED SIMULATION -- champion rule (iter_221)")
    print(sep)
    print(f"  Rule dict          : {rule_dict}")
    print(f"  Seed cells         : {seed_cells}")
    print(f"  Grid size          : {grid_size}x{grid_size}")
    print(f"  Steps              : {steps}")
    print()

    # 2. Run simulation ────────────────────────────────────────────────────
    print(f"Running continuous_com simulation ({steps} steps) ...")
    history = continuous_com(rule_dict, steps, seed_cells, grid_size)
    print(f"  Done. {len(history)} snapshots recorded.\n")

    # 3. Print unwrapped COM at key steps ──────────────────────────────────
    print(thsep)
    print("  UNWRAPPED CENTRE-OF-MASS")
    print(thsep)
    print(f"  {'t':>4s}  {'COM_r':>14s}  {'COM_c':>14s}  {'bit_count':>10s}")
    for t in range(0, steps + 1, 100):
        entry = history[t]
        com_r, com_c = entry["com"]
        bc = entry["bit_count"]
        print(f"  {t:>4d}  {com_r:>14.4f}  {com_c:>14.4f}  {bc:>10d}")
    print()

    # 4. Also print wrapped CoM for comparison ─────────────────────────────
    print(thsep)
    print("  WRAPPED CENTRE-OF-MASS (for comparison)")
    print(thsep)
    print(f"  {'t':>4s}  {'COM_r':>14s}  {'COM_c':>14s}  {'bit_count':>10s}")
    for t in range(0, steps + 1, 100):
        entry = history[t]
        com_r, com_c = entry["com"]
        wr = com_r % grid_size
        wc = com_c % grid_size
        bc = entry["bit_count"]
        print(f"  {t:>4d}  {wr:>14.4f}  {wc:>14.4f}  {bc:>10d}")
    print()

    # 5. DisplacementConsistencyFitness score ──────────────────────────────
    print(thsep)
    print("  DISPLACEMENT CONSISTENCY FITNESS")
    print(thsep)
    fitness_fn = DisplacementConsistencyFitness(num_windows=5)
    score = fitness_fn(history)
    print(f"  Fitness score : {score:.6f}")
    print()

    # 6. Per-window velocity summary ───────────────────────────────────────
    print(thsep)
    print("  PER-WINDOW VELOCITY (5 windows, 100 steps each)")
    print(thsep)
    num_windows = 5
    steps_per_window = steps / num_windows

    for w in range(num_windows):
        t_a = int(w * steps_per_window)
        t_b = int((w + 1) * steps_per_window)
        entry_a = history[t_a]
        entry_b = history[t_b]
        dx = entry_b["com"][0] - entry_a["com"][0]
        dy = entry_b["com"][1] - entry_a["com"][1]
        speed = math.sqrt(dx * dx + dy * dy) / steps_per_window
        angle = math.degrees(math.atan2(dy, dx))
        print(f"  Window {w+1} (t={t_a}->{t_b}): "
              f"dx={dx:+.4f}  dy={dy:+.4f}  speed={speed:.6f}  angle={angle:.2f} deg")
    print()

    # 7. Overall statistics ────────────────────────────────────────────────
    first = history[0]
    last  = history[-1]
    overall_dr = last["com"][0] - first["com"][0]
    overall_dc = last["com"][1] - first["com"][1]
    overall_dist = math.sqrt(overall_dr ** 2 + overall_dc ** 2)
    overall_speed = overall_dist / steps
    overall_angle = math.degrees(math.atan2(overall_dc, overall_dr))

    bit_counts = [e["bit_count"] for e in history]

    print(thsep)
    print("  OVERALL STATISTICS")
    print(thsep)
    print(f"  Total displacement : {overall_dist:.4f} cells")
    print(f"  Average speed      : {overall_speed:.6f} cells/step")
    print(f"  Direction          : {overall_angle:.2f} deg (from +row, CCW)")
    print(f"  Bit count          : {bit_counts[0]} -> {bit_counts[-1]} "
          f"(min={min(bit_counts)}, max={max(bit_counts)})")
    print()

    # 8. Linearity check ───────────────────────────────────────────────────
    path_length = sum(
        math.sqrt(
            (history[t]["com"][0] - history[t - 1]["com"][0]) ** 2
            + (history[t]["com"][1] - history[t - 1]["com"][1]) ** 2
        )
        for t in range(1, len(history))
    )
    linearity = overall_dist / path_length if path_length > 0 else 1.0
    print(thsep)
    print("  LINEARITY")
    print(thsep)
    print(f"  Straight-line distance : {overall_dist:.4f}")
    print(f"  Path length            : {path_length:.4f}")
    print(f"  Linearity              : {linearity:.4f}  (1.0 = perfectly straight)")
    if linearity > 0.99:
        print("  -> Near-perfect straight-line motion -- excellent glider!")
    elif linearity > 0.95:
        print("  -> Almost perfectly straight.")
    elif linearity > 0.80:
        print("  -> Mostly straight with slight wobble.")
    else:
        print("  -> Curved or meandering path.")
    print()

    print(sep)
    print(f"  FINAL FITNESS SCORE: {score:.6f}")
    print(sep)


if __name__ == "__main__":
    main()
