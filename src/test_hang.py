#!/usr/bin/env python3
"""
Diagnostic test for run_simulation.py hang check.
- Uses a specified rule file.
- Runs only --num_steps (default 20).
- Prints progress and exits.
"""

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent

# ── Parse arguments ──────────────────────────────────────────────────────────

rule_file = "archive/iter_219/results/g4_rule_083_cleaned.json"
num_steps = 20

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--rule_file" and i + 1 < len(args):
        rule_file = args[i + 1]
        i += 2
    elif args[i] == "--num_steps" and i + 1 < len(args):
        num_steps = int(args[i + 1])
        i += 2
    else:
        i += 1

print(f"Rule file : {rule_file}")
print(f"Steps     : {num_steps}")

# ── Load rule ────────────────────────────────────────────────────────────────

with open(rule_file) as f:
    data = json.load(f)

chrom = data["chromosome"]
lut = np.asarray(chrom, dtype=np.uint8)
grid_size = data.get("grid_size", 128)
seed_particle = data.get("seed_particle", [[63, 63], [64, 63], [64, 4]])

print(f"LUT loaded ({len(lut)} entries)  non-zero: {int(lut.sum())}")
print(f"Grid size   : {grid_size}")
print(f"Seed cells  : {seed_particle}")

# ── Simulation primitives ────────────────────────────────────────────────────

def make_grid(cells, gs):
    """Seed_particle is a flat list of [row, col] pairs."""
    grid = np.zeros((gs, gs), dtype=np.uint8)
    for r, c in cells:
        grid[r % gs, c % gs] = 1
    return grid

def step_grid(grid, lut):
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

# ── Run simulation ──────────────────────────────────────────────────────────

grid = make_grid(seed_particle, grid_size)
initial_bits = int(grid.sum())
initial_com = center_of_mass(grid)
prev_raw = initial_com
unwrapped = initial_com

print(f"\nInitial bit count: {initial_bits}")
print(f"Initial COM       : {initial_com}")
print(f"\n{'step':>6}  {'bits':>6}  {'raw_com':>22}  {'unwrapped':>26}  {'disp':>10}")
print("-" * 80)

t0 = time.time()
bit_error = False

for step in range(1, num_steps + 1):
    grid = step_grid(grid, lut)
    raw_com = center_of_mass(grid)

    # unwrap
    pr, pc = prev_raw
    cr, cc = raw_com
    half = grid_size / 2.0
    dr = cr - pr
    dc = cc - pc
    if dr > half: cr -= grid_size
    elif dr < -half: cr += grid_size
    if dc > half: cc -= grid_size
    elif dc < -half: cc += grid_size
    unwrapped = (unwrapped[0] + (cr - pr), unwrapped[1] + (cc - pc))
    prev_raw = raw_com

    bc = int(grid.sum())
    if bc != initial_bits:
        bit_error = True

    if step % 5 == 0 or step == num_steps:
        ddx = unwrapped[0] - initial_com[0]
        ddy = unwrapped[1] - initial_com[1]
        disp = math.sqrt(ddx * ddx + ddy * ddy)
        print(f"{step:>6}  {bc:>6}  "
              f"({raw_com[0]:8.2f},{raw_com[1]:8.2f})  "
              f"({unwrapped[0]:10.2f},{unwrapped[1]:10.2f})  "
              f"{disp:10.3f}")

elapsed = time.time() - t0

print(f"\n{'='*60}")
print(f"Simulation completed in {elapsed:.3f} seconds")
print(f"Final bit count : {int(grid.sum())}")
print(f"Bit count error : {bit_error}")
ddx = unwrapped[0] - initial_com[0]
ddy = unwrapped[1] - initial_com[1]
print(f"Displacement    : {math.sqrt(ddx*ddx + ddy*ddy):.4f}")
print(f"Target time     : 60 seconds")
print(f"Status          : {'PASS' if elapsed < 60 else 'FAIL (timeout)'}")

sys.exit(0 if elapsed < 60 else 1)
