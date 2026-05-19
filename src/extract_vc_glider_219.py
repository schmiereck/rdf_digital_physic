#!/usr/bin/env python3
"""Extract v<c glider structure from g4_rule_083 (iter_219 task 7)."""

import json
from collections import deque
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_219" / "results" / "g4_rule_083_cleaned.json"
OUT_PATH     = PROJECT_ROOT / "archive" / "iter_219" / "results" / "vc_glider_g4_rule_083_structure.json"

GRID_SIZE = 128
SIM_STEPS = 150
CENTER    = GRID_SIZE // 2  # 64

# Standard L-tromino seed at center
LTROMINO_CELLS = [(CENTER, CENTER), (CENTER, CENTER + 1), (CENTER + 1, CENTER + 1)]


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


def find_contiguous_objects(grid: np.ndarray):
    """BFS flood-fill to find all connected components (4-connectivity)."""
    visited = np.zeros_like(grid, dtype=bool)
    objects = []
    rows, cols = np.where(grid > 0)
    for r0, c0 in zip(rows.tolist(), cols.tolist()):
        if visited[r0, c0]:
            continue
        # BFS
        component = []
        queue = deque([(r0, c0)])
        visited[r0, c0] = True
        while queue:
            r, c = queue.popleft()
            component.append((r, c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = (r + dr) % GRID_SIZE, (c + dc) % GRID_SIZE
                if grid[nr, nc] > 0 and not visited[nr, nc]:
                    visited[nr, nc] = True
                    queue.append((nr, nc))
        objects.append(component)
    return objects


def normalize_coords(coords):
    """Shift so the minimum row and column are both 0."""
    if not coords:
        return []
    min_r = min(r for r, c in coords)
    min_c = min(c for r, c in coords)
    return sorted([(r - min_r, c - min_c) for r, c in coords])


def main():
    print(f"Loading rule from {RULE_PATH.name}")
    with open(RULE_PATH) as f:
        data = json.load(f)
    chromosome = data["chromosome"]
    lut = np.asarray(chromosome, dtype=np.uint8)
    print(f"LUT loaded ({len(lut)} entries), non-zero: {int(lut.sum())}")

    # Initialize grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1
    print(f"Seed: L-tromino at {LTROMINO_CELLS}")
    print(f"Running {SIM_STEPS} steps...")

    for step in range(SIM_STEPS):
        grid = step_grid(grid, lut)
        if (step + 1) % 50 == 0:
            total_bits = int(grid.sum())
            print(f"  Step {step+1:4d}: total bits = {total_bits}")

    total_bits = int(grid.sum())
    print(f"\nFinal grid after {SIM_STEPS} steps: {total_bits} live bits")

    # Find contiguous objects
    objects = find_contiguous_objects(grid)
    objects.sort(key=len, reverse=True)
    print(f"Found {len(objects)} contiguous object(s)")
    for i, obj in enumerate(objects):
        print(f"  Object {i}: {len(obj)} bits")

    if not objects:
        print("ERROR: No objects found!")
        return 1

    # Largest object = glider
    glider_raw = objects[0]
    debris_objects = objects[1:]
    debris_count = len(debris_objects)
    glider_bit_count = len(glider_raw)

    print(f"\nGlider: {glider_bit_count} bits")
    print(f"Debris objects discarded: {debris_count}")

    # Normalize
    normalized = normalize_coords(glider_raw)

    # Save result
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "rule_source": str(RULE_PATH.name),
        "simulation_steps": SIM_STEPS,
        "seed": "L-tromino",
        "extraction_method": "largest_contiguous_object",
        "glider_bit_count": glider_bit_count,
        "debris_object_count": debris_count,
        "coordinates": normalized,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved glider structure to {OUT_PATH.name}")
    print(f"glider_bit_count = {glider_bit_count}")
    print(f"debris_object_count = {debris_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
