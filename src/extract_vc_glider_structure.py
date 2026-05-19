#!/usr/bin/env python3
"""
extract_vc_glider_structure.py

Extracts the precise structure of the v<c glider discovered in iter_218
under champion rule g4_rule_083 (champion_vc_rule.json).

Uses the EXACT same seed placement as the fitness evaluation:
absolute positions (0,0), (0,1), (1,1) — matching run_vc_search.py.
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_218" / "results" / "champion_vc_rule.json"
OUT_DIR      = PROJECT_ROOT / "archive" / "iter_219" / "results"
OUT_PATH     = OUT_DIR / "vc_glider_g4_rule_083_structure.json"

GRID_SIZE    = 128
SIM_STEPS    = 150
EXTRACT_STEP = 100

# EXACT seed placement from run_vc_search.py / leaky_fitness.py:
# absolute coordinates (0,0), (0,1), (1,1)
SEED_CELLS = [(0, 0), (0, 1), (1, 1)]


def build_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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

    return lut[state]


HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


def find_components(grid: np.ndarray) -> list:
    """Find connected components on a toroidal grid using hex neighbors."""
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited = set()
    components = []

    for start in live:
        if start in visited:
            continue
        component = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            component.add(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % GRID_SIZE, (r + dr) % GRID_SIZE)
                if nb in live and nb not in visited:
                    stack.append(nb)
        components.append(frozenset(component))

    return components


def find_objects(grid: np.ndarray, min_size: int = 1) -> list:
    components = find_components(grid)
    objects = []
    for comp in components:
        if len(comp) >= min_size:
            objects.append({
                "cells": comp,
                "bit_count": len(comp),
            })
    objects.sort(key=lambda o: o["bit_count"], reverse=True)
    return objects


def normalize_coordinates(cells: frozenset) -> list:
    cell_list = sorted(cells)
    min_r, min_c = cell_list[0]
    normalized = sorted(
        [list(cell) for cell in cells],
        key=lambda p: (p[0] - min_r, p[1] - min_c),
    )
    for p in normalized:
        p[0] -= min_r
        p[1] -= min_c
    normalized.sort()
    return normalized


def make_grid_from_seed() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1
    return grid


def main() -> int:
    print("=== Extract v<c glider structure from iter_218 champion rule ===\n")

    # 1. Load champion rule
    print(f"Loading champion rule from: {CHAMP_PATH}")
    with open(CHAMP_PATH) as f:
        rule_data = json.load(f)

    rule_dict = rule_data["rule_dict"]
    lut = build_lut(rule_dict)
    print(f"  Rule dict entries: {len(rule_dict)}")
    print(f"  Fitness: {rule_data.get('fitness', 'N/A')}")
    print(f"  Avg velocity: {rule_data['metrics'].get('avg_velocity', 'N/A')}")
    print(f"  Initial CoM:   {rule_data['metrics']['initial_com']}")
    print(f"  Final CoM:     {rule_data['metrics']['final_com']}")

    # 2. Initialize grid with EXACT seed placement from fitness evaluation
    grid = make_grid_from_seed()
    initial_bits = int(grid.sum())
    print(f"\nGrid: {GRID_SIZE}x{GRID_SIZE}  Seed at absolute: {SEED_CELLS}")
    print(f"Initial bits: {initial_bits}  Steps: {SIM_STEPS}\n")

    # 3. Run simulation
    print(f"{'Step':>6}  {'Bits':>6}  {'CoM':>22}")
    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)

        bc = int(grid.sum())
        rows, cols = np.where(grid > 0)
        if len(rows) > 0:
            com = (float(np.mean(rows)), float(np.mean(cols)))
        else:
            com = (0.0, 0.0)

        if step % 25 == 0 or step == EXTRACT_STEP or step == SIM_STEPS:
            print(f"{step:>6}  {bc:>6}  ({com[0]:8.2f}, {com[1]:8.2f})")

    print()

    # 4. Replay to step 100 for extraction
    print(f"--- Re-running simulation to step {EXTRACT_STEP} for object extraction ---\n")
    grid = make_grid_from_seed()

    for step in range(1, EXTRACT_STEP + 1):
        grid = step_grid(grid, lut)

    total = int(grid.sum())
    print(f"At step {EXTRACT_STEP}: total live cells = {total}\n")

    # 5. Find connected components
    objects = find_objects(grid, min_size=1)
    print(f"Connected components found: {len(objects)}")
    for i, obj in enumerate(objects):
        cells_sorted = sorted(obj["cells"])
        print(f"  Component {i}: {obj['bit_count']} cells @ {cells_sorted}")

    # The glider is the smallest mobile object.
    # From the fitness metrics, initial_bits=3 and conservation=1.0 at step 100,
    # so the glider should have exactly 3 bits if it survived.
    small_objects = [o for o in objects if o["bit_count"] <= 20]
    large_objects = [o for o in objects if o["bit_count"] > 20]

    print(f"\nSmall objects (<=20 cells): {len(small_objects)}")
    print(f"Large objects (>20 cells):  {len(large_objects)}")

    # Pick the smallest object (the glider)
    if small_objects:
        glider = small_objects[-1]  # smallest
    else:
        glider = objects[0]

    print(f"\nSelected glider candidate: {glider['bit_count']} cells")

    # 6. Normalize coordinates
    glider_cells = glider["cells"]
    normalized = normalize_coordinates(glider_cells)
    normalized = [[int(p[0]), int(p[1])] for p in normalized]

    print(f"Normalized glider structure ({len(normalized)} bits):")
    for coord in normalized:
        print(f"  {coord}")

    # 7. Save output
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_PATH, "w") as f:
        json.dump(normalized, f, indent=2)

    print(f"\nSaved glider structure to: {OUT_PATH}")
    print(f"Metric: glider_bit_count = {len(normalized)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
