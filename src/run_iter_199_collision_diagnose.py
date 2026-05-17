#!/usr/bin/env python3
"""
run_iter_199_collision_diagnose.py

Diagnose the 60-degree L-tromino collision timeout from iter_197.1.
Mirrors the setup of run_iter_197_collision_60deg.py but instruments:
  - total_bit_count  (bit conservation check)
  - active_cell_count (cells needing computation = live cells + their 6 hex neighbors)
  - num_components
  - sim_time_ms

Runs up to 1000 steps; stops early on bit blowup.

Writes:
  archive/iter_199/results/collision_log.csv
"""

import csv
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import label

REPO_ROOT  = Path(__file__).resolve().parent.parent
RULE_PATH  = REPO_ROOT / "archive/iter_193/iter_002/results/champion_rule.json"
OUTPUT_DIR = REPO_ROOT / "archive/iter_199/results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUT = OUTPUT_DIR / "collision_log.csv"

GRID_SIZE = 256
SIM_STEPS = 1000
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)

# Stop early if bits explode beyond this fraction of total grid cells
BIT_BLOWUP_THRESHOLD = int(GRID_SIZE * GRID_SIZE * 0.40)  # 40% = 26214 cells

L_TROMINO_STD = [(0, 0), (1, 0), (0, 1)]


def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Single CA step on toroidal hexagonal grid."""
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


def active_cell_count(grid: np.ndarray) -> int:
    """
    Count cells that require computation next step:
    a cell is active if it is ON, or any of its 6 hex neighbors is ON.
    Equivalently: the union of the pattern and all 6 hex-shifted copies.
    """
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,     1, axis=1)
    nw = np.roll(w,    -1, axis=1)
    active = grid | e | w | ne | sw | se | nw
    return int(active.sum())


def place_glider(grid: np.ndarray, base_row: int, base_col: int) -> None:
    for dr, dc in L_TROMINO_STD:
        grid[(base_row + dr) % GRID_SIZE, (base_col + dc) % GRID_SIZE] = 1


# ── Load rule ──────────────────────────────────────────────────────────────────

with open(RULE_PATH) as f:
    champion_data = json.load(f)
rule_dict = champion_data["rule_dict"]
lut = rule_dict_to_lut(rule_dict)
print(f"Loaded champion rule  fitness={champion_data['fitness']}")
print(f"  {len(rule_dict)} explicit transitions")


# ── Build the same 60-degree collision setup as iter_197.1 ─────────────────────

SCALE = 2.0
HALF_A_ROW = int(-7 * SCALE)   # = -14
HALF_A_COL = int(-47 * SCALE)  # = -94

# Hex +60° rotation (axial q=col, r=row): q'=q+r, r'=-q
HALF_B_COL = HALF_A_COL + HALF_A_ROW   # -94 + -14 = -108
HALF_B_ROW = -HALF_A_COL               # 94

CENTER = GRID_SIZE // 2   # 128

A_BASE = ((CENTER + HALF_A_ROW) % GRID_SIZE, (CENTER + HALF_A_COL) % GRID_SIZE)
B_BASE = ((CENTER + HALF_B_ROW) % GRID_SIZE, (CENTER + HALF_B_COL) % GRID_SIZE)

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
place_glider(grid, *A_BASE)
place_glider(grid, *B_BASE)

initial_bits = int(grid.sum())
initial_active = active_cell_count(grid)
print(f"Grid {GRID_SIZE}x{GRID_SIZE}  initial bits={initial_bits}  active={initial_active}")
print(f"Glider A base: {A_BASE}")
print(f"Glider B base: {B_BASE}")


# ── Run, logging every step ────────────────────────────────────────────────────

rows = []   # (step, bit_count, active_cell_count, num_components, sim_time_ms)

# step 0 baseline
t0 = time.perf_counter()
nc0 = int(label(grid, structure=LABEL_STRUCT)[1])
t1 = time.perf_counter()
rows.append((0, initial_bits, initial_active, nc0, (t1 - t0) * 1000.0))
print(f"  step    0: bits={initial_bits:6d}  active={initial_active:6d}  ncomp={nc0}")

stop_reason = "completed"
last_step = 0

run_start = time.perf_counter()

for t in range(1, SIM_STEPS + 1):
    t_step_start = time.perf_counter()
    grid = step_grid(grid, lut)
    bc = int(grid.sum())
    ac = active_cell_count(grid)
    nc = int(label(grid, structure=LABEL_STRUCT)[1])
    t_step_end = time.perf_counter()

    step_ms = (t_step_end - t_step_start) * 1000.0
    rows.append((t, bc, ac, nc, step_ms))
    last_step = t

    if t % 50 == 0 or t <= 10:
        elapsed = time.perf_counter() - run_start
        print(f"  step {t:4d}: bits={bc:6d}  active={ac:6d}  ncomp={nc:3d}  "
              f"step_ms={step_ms:6.2f}  wall={elapsed:.1f}s")

    if bc >= BIT_BLOWUP_THRESHOLD:
        stop_reason = f"bit_blowup (bits={bc} >= {BIT_BLOWUP_THRESHOLD})"
        print(f"  EARLY STOP at step {t}: {stop_reason}")
        break

total_wall = time.perf_counter() - run_start
print(f"\nLoop done: last_step={last_step}, stop_reason={stop_reason}, "
      f"total_wall={total_wall:.2f}s")


# ── Write CSV ──────────────────────────────────────────────────────────────────

with open(CSV_OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["step", "bit_count", "active_cell_count", "num_components", "sim_time_ms"])
    w.writerows(rows)
print(f"Wrote {CSV_OUT}  ({len(rows)} rows)")


# ── Summary ────────────────────────────────────────────────────────────────────

bits_series   = [r[1] for r in rows]
active_series = [r[2] for r in rows]
ncomp_series  = [r[3] for r in rows]
time_series   = [r[4] for r in rows]

print("\n=== Diagnostic summary ===")
print(f"  steps logged:           {len(rows) - 1}")
print(f"  stop_reason:            {stop_reason}")
print(f"  bits  min/max/last:     {min(bits_series)} / {max(bits_series)} / {bits_series[-1]}")
print(f"  active min/max/last:    {min(active_series)} / {max(active_series)} / {active_series[-1]}")
print(f"  ncomp min/max/last:     {min(ncomp_series)} / {max(ncomp_series)} / {ncomp_series[-1]}")
print(f"  step_ms min/max/avg:    {min(time_series):.2f} / {max(time_series):.2f} / "
      f"{sum(time_series)/len(time_series):.2f}")
print(f"  total wall time:        {total_wall:.2f}s")
print(f"  bits increased by:      {bits_series[-1] - bits_series[0]}  "
      f"(x{bits_series[-1]/max(bits_series[0],1):.1f})")
print(f"  active increased by:    {active_series[-1] - active_series[0]}  "
      f"(x{active_series[-1]/max(active_series[0],1):.1f})")
