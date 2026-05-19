#!/usr/bin/env python3
"""
run_and_save_state.py — Run v<c glider simulation and save the final grid state.

1. Load rule from archive/iter_218/results/champion_rule.json
2. Initialize 256x256 numpy grid
3. Place L-tromino seed ((0,0),(1,0),(1,1)) relative to center (128,128)
4. Simulate 300 steps
5. Save final 256x256 grid to archive/iter_219/results/final_grid_state.npy
"""

import json
import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_RULE_PATH = PROJECT_ROOT / "archive" / "iter_218" / "results" / "champion_rule.json"
OUTPUT_PATH     = PROJECT_ROOT / "archive" / "iter_219" / "results" / "final_grid_state.npy"

GRID_SIZE = 256
SIM_STEPS = 300


# ── LUT construction (mirrors engine.build_lut for bits_per_cell=1) ──────────

def build_lut(rule_dict: dict, bits_per_cell: int = 1) -> np.ndarray:
    n = bits_per_cell
    lut_size = 1 << (7 * n)
    full = np.arange(lut_size, dtype=np.uint16)
    for k, v in rule_dict.items():
        ki = int(k)
        full[ki] = int(v)
    center_shift = 6 * n
    center_mask = (1 << n) - 1
    return ((full >> center_shift) & center_mask).astype(np.uint8)


# ── Hexagonal stepping (toroidal wrapping via np.roll) ────────────────────────

def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Advance one hexagonal CA step.

    Uses the same hexagonal neighbourhood directions as engine.py / simulator.py:
        e   = north roll (-1, 0)   → axis 0, roll -1
        w   = south roll (+1, 0)   → axis 0, roll +1
        ne  = northwest roll (-1,-1) → axis 0, roll -1 AND axis 1, roll -1
        sw  = southeast roll (+1,+1) → axis 0, roll +1 AND axis 1, roll +1
        se  = northeast of west  → e rolled +1 in axis 1
        nw  = southwest of east  → w rolled -1 in axis 1
    """
    e   = np.roll(grid, -1, axis=0)
    w   = np.roll(grid,  1, axis=0)
    ne  = np.roll(grid, -1, axis=1)
    sw  = np.roll(grid,  1, axis=1)
    se  = np.roll(e,     1, axis=1)
    nw  = np.roll(w,    -1, axis=1)

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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # 1. Load rule
    with open(CHAMP_RULE_PATH) as f:
        data = json.load(f)
    rule_dict = data["rule_dict"]

    print(f"Loaded champion rule from iter_218")
    print(f"  rule_dict entries: {len(rule_dict)}")
    print(f"  grid_size: {GRID_SIZE}")
    print(f"  sim_steps: {SIM_STEPS}")

    # Build LUT
    lut = build_lut(rule_dict, bits_per_cell=1)

    # 2. Initialize 256x256 grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)

    # 3. Place L-tromino seed ((0,0), (1,0), (1,1)) relative to center (128, 128)
    center_r, center_c = 128, 128
    seed_cells = ((0, 0), (1, 0), (1, 1))
    for dr, dc in seed_cells:
        grid[center_r + dr, center_c + dc] = 1

    initial_bits = int(grid.sum())
    print(f"Initial bit count: {initial_bits}")

    # 4. Simulate 300 steps
    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)

    final_bits = int(grid.sum())
    print(f"Final bit count after {SIM_STEPS} steps: {final_bits}")

    # 5. Save final grid
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(OUTPUT_PATH, grid)
    print(f"Saved final grid state to: {OUTPUT_PATH}")
    print(f"  shape: {grid.shape}")
    print(f"  dtype: {grid.dtype}")
    print(f"  non-zero cells: {int((grid > 0).sum())}")


if __name__ == "__main__":
    main()
