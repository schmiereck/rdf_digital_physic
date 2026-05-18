#!/usr/bin/env python3
"""
characterize_v_lt_c_glider.py
Detailed quantitative analysis of the v<c glider discovered in iter_200.

Outputs:
  - archive/iter_201/results/glider_timeseries.csv  (per-step data)
  - stdout: velocity vector, speed, period, bit conservation status
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evolution import rule_dict_to_lut, step_grid

GRID_SIZE = 128
STEPS = 1024
# L-tromino seed centered on 128x128 grid (matches seeds.py)
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]


def make_initial_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


def center_of_mass(grid):
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0)
    return (float(np.mean(rows)), float(np.mean(cols)))


def unwrap_com(raw_com, prev_unwrapped):
    """Unwrap CoM position using shortest-path correction to handle toroidal wraparound."""
    r, c = raw_com
    pr, pc = prev_unwrapped
    dr = r - (pr % GRID_SIZE)
    dc = c - (pc % GRID_SIZE)
    if dr > GRID_SIZE / 2:
        dr -= GRID_SIZE
    elif dr < -GRID_SIZE / 2:
        dr += GRID_SIZE
    if dc > GRID_SIZE / 2:
        dc -= GRID_SIZE
    elif dc < -GRID_SIZE / 2:
        dc += GRID_SIZE
    return (pr + dr, pc + dc)


def state_hash(grid):
    """MD5 hash of active cell positions relative to rounded CoM (detects internal periodicity)."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return "empty"
    cr = round(float(np.mean(rows)))
    cc = round(float(np.mean(cols)))
    rel = tuple(sorted((int(r) - cr, int(c) - cc) for r, c in zip(rows, cols)))
    return hashlib.md5(str(rel).encode()).hexdigest()[:16]


def detect_period(hashes, start=256, max_period=300, confirm_cycles=4):
    """Find smallest period p such that hash[start + k*p] == hash[start] for confirm_cycles k."""
    ref = hashes[start]
    for p in range(1, max_period + 1):
        ok = True
        for k in range(1, confirm_cycles + 1):
            idx = start + k * p
            if idx >= len(hashes):
                ok = False
                break
            if hashes[idx] != ref:
                ok = False
                break
        if ok:
            return p
    return -1


def load_rule():
    base = Path(__file__).parent.parent / "archive"
    candidates = [
        base / "iter_200" / "results" / "champion_v_lt_c_rule.json",
        base / "iter_200.1" / "results" / "champion_v_lt_c_rule.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    print("ERROR: champion_v_lt_c_rule.json not found in iter_200 or iter_200.1", file=sys.stderr)
    sys.exit(1)


def main():
    rule_path = load_rule()
    print(f"Loading rule from: {rule_path}")
    with open(rule_path) as f:
        rule_data = json.load(f)

    rule_dict = rule_data["rule_dict"]
    print(f"Rule mappings: {len(rule_dict)}")
    print(f"Fitness: {rule_data.get('fitness', 'N/A')}")

    lut = rule_dict_to_lut(rule_dict)

    grid = make_initial_grid()
    initial_bits = int(grid.sum())
    print(f"Initial bits: {initial_bits}  (L-tromino seed)")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE} toroidal  |  Steps: {STEPS}")
    print()

    rows_data = []
    hashes = []
    unwrapped_r = []
    unwrapped_c = []

    raw_com0 = center_of_mass(grid)
    prev_unwrapped = raw_com0
    h0 = state_hash(grid)
    hashes.append(h0)
    unwrapped_r.append(raw_com0[0])
    unwrapped_c.append(raw_com0[1])
    rows_data.append({
        'step': 0,
        'CoM_x': raw_com0[1],
        'CoM_y': raw_com0[0],
        'bit_count': initial_bits,
        'state_hash': h0,
    })

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        bits = int(grid.sum())
        raw_com = center_of_mass(grid)
        uw = unwrap_com(raw_com, prev_unwrapped)
        prev_unwrapped = uw
        unwrapped_r.append(uw[0])
        unwrapped_c.append(uw[1])

        h = state_hash(grid)
        hashes.append(h)
        rows_data.append({
            'step': t,
            'CoM_x': uw[1],   # column = x
            'CoM_y': uw[0],   # row    = y
            'bit_count': bits,
            'state_hash': h,
        })

        if t % 128 == 0:
            print(f"  Step {t:4d}: bits={bits:3d}, "
                  f"CoM=({uw[1]:.2f}, {uw[0]:.2f}), hash={h}")

    # --- Average velocity over last 512 steps ---
    start_v = STEPS - 512
    dr = unwrapped_r[STEPS] - unwrapped_r[start_v]
    dc = unwrapped_c[STEPS] - unwrapped_c[start_v]
    vel_y = dr / 512.0  # rows/step
    vel_x = dc / 512.0  # cols/step
    speed = float(np.sqrt(vel_x**2 + vel_y**2))

    # --- Period detection ---
    period = detect_period(hashes, start=256, max_period=300, confirm_cycles=4)

    # --- Bit conservation ---
    bit_counts = [r['bit_count'] for r in rows_data]
    stable = all(b == initial_bits for b in bit_counts)

    # --- Save CSV ---
    out_dir = Path(__file__).parent.parent / "archive" / "iter_201" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "glider_timeseries.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['step', 'CoM_x', 'CoM_y', 'bit_count', 'state_hash'],
        )
        writer.writeheader()
        for row in rows_data:
            writer.writerow({
                'step': row['step'],
                'CoM_x': f"{row['CoM_x']:.6f}",
                'CoM_y': f"{row['CoM_y']:.6f}",
                'bit_count': row['bit_count'],
                'state_hash': row['state_hash'],
            })
    print(f"\nSaved: {csv_path}  ({len(rows_data)} rows)")

    # --- Final report ---
    print("\n========== RESULTS ==========")
    print(f"Average velocity (steps {start_v}-{STEPS}):")
    print(f"  vel_x (col) = {vel_x:+.6f} cells/step")
    print(f"  vel_y (row) = {vel_y:+.6f} cells/step")
    print(f"  speed       = {speed:.6f} c  (fraction of max propagation speed)")
    print(f"Period: {period} steps{'  [not found within 300]' if period < 0 else ''}")
    print(f"Bit conservation: {'STABLE (bit count constant)' if stable else 'UNSTABLE'}")
    if not stable:
        changes = [(r['step'], r['bit_count']) for r in rows_data if r['bit_count'] != initial_bits]
        print(f"  First deviation at step {changes[0][0]}: bits={changes[0][1]}")
    print("=============================")


if __name__ == "__main__":
    main()
