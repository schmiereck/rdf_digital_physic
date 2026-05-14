#!/usr/bin/env python3
"""
simulate_iter176_bit_count.py

Load champion rule g7_rule_076 from iter_174, run 2000 steps with the
standard L-tromino seed on a 128x128 toroidal hexagonal grid, and record
bit_count at every step. Save the per-step profile to
archive/iter_176/results/bit_count_profile.csv.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_174" / "results" / "best_rule.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_176" / "results"
CSV_OUT      = RESULTS_DIR / "bit_count_profile.csv"
TXT_OUT      = PROJECT_ROOT / "archive" / "iter_174" / "results" / "champion_rule_g7_r76.txt"

GRID_SIZE = 128
STEPS     = 2000

# L-tromino seed (same as used in iter_170-174)
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]


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


def make_ltromino_grid() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1
    return grid


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load rule
    with open(RULE_PATH) as f:
        data = json.load(f)
    rule_dict = data["rule"]
    rule_id   = data["rule_id"]
    print(f"Loaded rule: {rule_id}  ({len(rule_dict)} non-identity mappings)")

    # Save rule string to txt for reference
    rule_str = json.dumps({str(k): v for k, v in sorted(
        ((int(k), int(v)) for k, v in rule_dict.items()), key=lambda x: x[0]
    )})
    TXT_OUT.write_text(rule_str)
    print(f"Saved rule string to: {TXT_OUT}")

    lut  = rule_dict_to_lut(rule_dict)
    grid = make_ltromino_grid()

    bit_counts = []
    bit_counts.append(int(grid.sum()))  # step 0

    print(f"\nRunning {STEPS} steps on {GRID_SIZE}x{GRID_SIZE} toroidal grid...")
    print(f"Seed: L-tromino, {len(LTROMINO_CELLS)} bits at {LTROMINO_CELLS}")
    print(f"Step    0: bit_count = {bit_counts[0]}")

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)
        if t % 200 == 0:
            print(f"Step {t:5d}: bit_count = {bc}")

    final_bit_count = bit_counts[-1]
    max_bit_count   = max(bit_counts)
    max_step        = bit_counts.index(max_bit_count)

    print(f"\n=== Simulation Complete ===")
    print(f"max_bit_count:   {max_bit_count}  (at step {max_step})")
    print(f"final_bit_count: {final_bit_count}  (step {STEPS})")
    print(f"initial_bit_count: {bit_counts[0]}")

    # Save CSV
    with open(CSV_OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "bit_count"])
        for t, bc in enumerate(bit_counts):
            writer.writerow([t, bc])
    print(f"\nSaved per-step CSV: {CSV_OUT}")
    print(f"  Rows: {len(bit_counts)} (steps 0 to {STEPS})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
