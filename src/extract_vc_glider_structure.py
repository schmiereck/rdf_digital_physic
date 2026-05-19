#!/usr/bin/env python3
"""
extract_vc_glider_structure.py

Extracts the precise structure of the v<c glider discovered in iter_218
under champion rule g4_rule_083 (champion_vc_rule.json).

Steps:
  1. Load champion rule from archive/iter_218/results/champion_vc_rule.json
  2. Simulate on 128x128 toroidal grid with L-tromino seed for 150 steps
  3. At step 100, identify the moving glider via connected-component analysis
  4. Normalize coordinates so top-left-most bit is at (0,0)
  5. Save final list of relative coordinates to JSON
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

# 3-bit L-tromino centered on 128x128 grid
L_TROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]


# ── Hexagonal-CA helpers ──────────────────────────────────────────────────────

def rule_to_lut(rule_dict: dict) -> np.ndarray:
    """Build 128-element LUT from rule_dict mapping."""
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """One step of the hexagonal CA on a toroidal grid."""
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


# ── Connected-components (4-connectivity for rectangular grid) ────────────────

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
    visited: set = set()
    components = []

    for start in live:
        if start in visited:
            continue
        component: set = set()
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


# ── find_objects utility ─────────────────────────────────────────────────────

def find_objects(grid: np.ndarray, min_size: int = 1) -> list:
    """
    find_objects — identify all connected-component objects on the grid.

    Returns a list of dicts:
        {
            "cells": frozenset of (row, col),
            "bit_count": int,
        }
    Filtered to only include components with at least min_size cells.
    """
    components = find_components(grid)
    objects = []
    for comp in components:
        if len(comp) >= min_size:
            objects.append({
                "cells": comp,
                "bit_count": len(comp),
            })
    # Sort by size descending — the glider should be a small mobile object
    objects.sort(key=lambda o: o["bit_count"], reverse=True)
    return objects


# ── Coordinate normalization ─────────────────────────────────────────────────

def normalize_coordinates(cells: frozenset) -> list:
    """
    Normalize coordinates so the top-left-most bit is at (0,0).
    "Top-left" means minimum row first, then minimum column.
    Returns a list of [row, col] lists.
    """
    cell_list = sorted(cells)  # sort by (row, col)
    min_r, min_c = cell_list[0]
    normalized = sorted(
        [list(cell) for cell in cells],
        key=lambda p: (p[0] - min_r, p[1] - min_c),
    )
    # Shift so top-left is (0,0)
    for p in normalized:
        p[0] -= min_r
        p[1] -= min_c
    # Re-sort for clean output
    normalized.sort()
    return normalized


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=== Extract v<c glider structure from iter_218 champion rule ===\n")

    # 1. Load champion rule
    print(f"Loading champion rule from: {CHAMP_PATH}")
    with open(CHAMP_PATH) as f:
        rule_data = json.load(f)

    rule_dict = rule_data["rule_dict"]
    lut = rule_to_lut(rule_dict)
    print(f"  Rule dict entries: {len(rule_dict)}")
    print(f"  Fitness: {rule_data.get('fitness', 'N/A')}")
    print(f"  Avg velocity: {rule_data['metrics'].get('avg_velocity', 'N/A')}")

    # 2. Initialize grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in L_TROMINO_CELLS:
        grid[r, c] = 1
    initial_bits = int(grid.sum())
    print(f"\nGrid: {GRID_SIZE}x{GRID_SIZE}  Seed: L-tromino at {L_TROMINO_CELLS}")
    print(f"Initial bits: {initial_bits}  Steps: {SIM_STEPS}\n")

    # 3. Run simulation, tracking bit count
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

    # 4. At step 100, extract the glider object
    #    (We need to replay the simulation to step 100)
    print(f"--- Re-running simulation to step {EXTRACT_STEP} for object extraction ---\n")
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in L_TROMINO_CELLS:
        grid[r, c] = 1

    for step in range(1, EXTRACT_STEP + 1):
        grid = step_grid(grid, lut)

    print(f"At step {EXTRACT_STEP}: total live cells = {int(grid.sum())}\n")

    # 5. Use find_objects to identify all components
    objects = find_objects(grid, min_size=1)
    print(f"Connected components found: {len(objects)}")
    for i, obj in enumerate(objects):
        print(f"  Component {i}: {obj['bit_count']} cells")

    # The glider should be the smallest mobile object that's not the still-life ash.
    # For a v<c glider from an L-tromino seed, the glider is typically 3 bits.
    # However, at step 100, there may be ash + the glider.
    # Let's look for small objects (bit_count <= 10) and pick the one with the
    # smallest bit count that is NOT at the same position as the CoM of a large blob.

    # Strategy: find all small components and pick the one most likely to be the glider
    # (smallest moving object). The ash will be large and stationary.
    small_objects = [o for o in objects if o["bit_count"] <= 20]
    large_objects = [o for o in objects if o["bit_count"] > 20]

    print(f"\nSmall objects (<=20 cells): {len(small_objects)}")
    print(f"Large objects (>20 cells):  {len(large_objects)}")

    # The glider is typically the smallest component.
    # If there's a very small component (3-10 bits), it's likely the glider.
    if small_objects:
        glider = small_objects[-1]  # smallest one
    else:
        glider = objects[0]

    print(f"\nSelected glider candidate: {glider['bit_count']} cells")

    # 6. Normalize coordinates
    glider_cells = glider["cells"]
    normalized = normalize_coordinates(glider_cells)

    print(f"Normalized glider structure ({len(normalized)} bits):")
    for coord in normalized:
        print(f"  {coord}")

    # 7. Save output
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "source_rule": "g4_rule_083",
        "source_iteration": "iter_218",
        "extraction_step": EXTRACT_STEP,
        "glider_structure": normalized,
        "bit_count": len(normalized),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved glider structure to: {OUT_PATH}")
    print(f"Metric: glider_bit_count = {len(normalized)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
