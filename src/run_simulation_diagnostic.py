#!/usr/bin/env python3
"""
Diagnostic wrapper for run_simulation.py — uses champion rule from specified iteration,
accepts --num_steps, and prints verbose output.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent


def load_champion_rule(iter_id: str) -> tuple:
    """Load champion rule from the specified iteration."""
    iter_dir = PROJECT_ROOT / "archive" / iter_id / "results"
    champ_path = iter_dir / "champion_rule.json"

    print(f"Loading champion rule from {champ_path}")
    with open(champ_path) as f:
        data = json.load(f)

    chrom = data["chromosome"]
    rule_dict = data.get("rule_dict", None)
    grid_size = data.get("grid_size", 128)
    seed_particle = data.get("seed_particle", None)

    print(f"  Chromosome length: {len(chrom)}")
    print(f"  Grid size: {grid_size}")
    print(f"  Rule dict entries: {len(rule_dict) if rule_dict else 'N/A'}")
    if rule_dict:
        max_rule_val = max(rule_dict.values())
        print(f"  Rule dict max output: {max_rule_val}")
    if seed_particle:
        print(f"  Seed particle: {seed_particle}")

    return chrom, rule_dict, grid_size, seed_particle


def step_grid(grid, lut, grid_size):
    """Single CA step with toroidal boundaries."""
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


def center_of_mass(grid):
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def unwrap_com(prev_com, curr_com, size):
    pr, pc = prev_com
    cr, cc = curr_com
    half = size / 2.0
    dr = cr - pr
    if dr > half:
        cr -= size
    elif dr < -half:
        cr += size
    dc = cc - pc
    if dc > half:
        cc -= size
    elif dc < -half:
        cc += size
    return (cr, cc)


def main():
    parser = argparse.ArgumentParser(description="Diagnostic simulation run")
    parser.add_argument("--iter", default="iter_218", help="Iteration directory name")
    parser.add_argument("--num_steps", type=int, default=20, help="Number of simulation steps")
    parser.add_argument("--grid_size", type=int, default=None, help="Override grid size from rule")
    parser.add_argument("--verbose", action="store_true", help="Extra verbose output")
    args = parser.parse_args()

    iter_id = args.iter
    num_steps = args.num_steps
    print(f"=== Diagnostic Simulation — {iter_id} ===")
    print(f"  Steps: {num_steps}")
    print(f"  Verbose: {args.verbose}")
    print()

    # Load rule
    chrom, rule_dict, grid_size, seed_particle = load_champion_rule(iter_id)

    if args.grid_size:
        grid_size = args.grid_size

    lut = np.asarray(chrom, dtype=np.uint8)
    non_zero = int(lut.sum())
    print(f"LUT: {len(lut)} entries, non-zero: {non_zero}")
    print()

    # Initialize grid
    if seed_particle:
        # Use seed from champion rule
        cells = [(p[0], p[1]) for p in seed_particle]
    else:
        # Default: L-tromino at center
        cells = [(grid_size//2, grid_size//2),
                 (grid_size//2+1, grid_size//2),
                 (grid_size//2+1, grid_size//2+1)]

    INITIAL_BITS = len(cells)
    print(f"Grid: {grid_size}x{grid_size}")
    print(f"Seed cells: {cells}")
    print(f"Initial bits: {INITIAL_BITS}")
    print()

    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in cells:
        grid[r % grid_size, c % grid_size] = 1

    initial_com = center_of_mass(grid)
    prev_raw = initial_com
    unwrapped = initial_com

    print(f"{'step':>6}  {'bit_count':>9}  {'raw_com':>22}  {'unwrapped':>28}  {'disp':>10}")
    print("-" * 90)

    try:
        for step in range(1, num_steps + 1):
            grid = step_grid(grid, lut, grid_size)
            raw_com = center_of_mass(grid)

            adj = unwrap_com(prev_raw, raw_com, grid_size)
            dr = adj[0] - prev_raw[0]
            dc = adj[1] - prev_raw[1]
            unwrapped = (unwrapped[0] + dr, unwrapped[1] + dc)
            prev_raw = raw_com

            bc = int(grid.sum())
            ddx = unwrapped[0] - initial_com[0]
            ddy = unwrapped[1] - initial_com[1]
            disp = math.sqrt(ddx * ddx + ddy * ddy)

            if step % 5 == 0 or args.verbose or bc == 0 or bc != INITIAL_BITS:
                print(f"{step:>6}  {bc:>9}  "
                      f"({raw_com[0]:8.2f},{raw_com[1]:8.2f})  "
                      f"({unwrapped[0]:12.2f},{unwrapped[1]:12.2f})  "
                      f"{disp:10.3f}")

    except Exception as e:
        print(f"\n!!! EXCEPTION at step {step}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Final metrics
    print()
    print("=== Final Metrics ===")
    ddx = unwrapped[0] - initial_com[0]
    ddy = unwrapped[1] - initial_com[1]
    displacement = math.sqrt(ddx * ddx + ddy * ddy)
    final_bc = int(grid.sum())
    print(f"Final bit count:       {final_bc}")
    print(f"Displacement:          {displacement:.4f}")
    print(f"Bits changed:          {final_bc != INITIAL_BITS}")
    print(f"Grid empty:            {final_bc == 0}")
    print()
    print("=== Diagnostic complete — no hang ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
