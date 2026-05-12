#!/usr/bin/env python3
"""
generate_ash_pattern.py

Generates the canonical 'ash' pattern by running the cooling rule
(archive/iter_105/population/rule_023.json) on a 150x150 random soup
(25% density, seed=42) for 200 steps, then saves the live cell
coordinates to src/ash_pattern.json.
"""

import json
from pathlib import Path

import numpy as np

PROJECT_ROOT      = Path(__file__).parent.parent
COOLING_RULE_PATH = PROJECT_ROOT / "archive" / "iter_105" / "population" / "rule_023.json"
ASH_PATTERN_PATH  = Path(__file__).parent / "ash_pattern.json"

GRID_SIZE     = 150
DENSITY       = 0.25
COOLING_STEPS = 200
RANDOM_SEED   = 42


def load_lookup(path: Path) -> np.ndarray:
    """128-element uint8 LUT: index = 7-bit neighborhood, value = new center bit."""
    with open(path) as f:
        raw = json.load(f)
    lut = np.arange(128, dtype=np.uint8)
    for k, v in raw.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lookup: np.ndarray) -> np.ndarray:
    """One synchronous CA step on a toroidal hex grid using a pre-built LUT."""
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)

    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)

    return lookup[state]


def main():
    print(f"Loading cooling rule: {COOLING_RULE_PATH}")
    lookup = load_lookup(COOLING_RULE_PATH)

    rng  = np.random.default_rng(RANDOM_SEED)
    grid = (rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"Initial soup: {int(grid.sum())} live cells  "
          f"({GRID_SIZE}x{GRID_SIZE}, density={DENSITY}, seed={RANDOM_SEED})")

    for step in range(COOLING_STEPS):
        grid = step_grid(grid, lookup)
        if (step + 1) % 50 == 0:
            print(f"  Step {step+1:3d}: {int(grid.sum()):6d} live cells")

    ash_bit_count = int(grid.sum())
    print(f"Cooling complete (step {COOLING_STEPS}). Ash: {ash_bit_count} live cells")

    qs, rs = np.where(grid == 1)
    cells  = [[int(q), int(r)] for q, r in zip(qs, rs)]

    payload = {
        "grid_size": GRID_SIZE,
        "bit_count": ash_bit_count,
        "cells": cells,
    }
    with open(ASH_PATTERN_PATH, "w") as f:
        json.dump(payload, f)
    print(f"Saved {len(cells)} live cells to {ASH_PATTERN_PATH}")


if __name__ == "__main__":
    main()
