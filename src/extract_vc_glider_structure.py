#!/usr/bin/env python3
"""
extract_vc_glider_structure.py

Programmatically extracts the structure of the v<c glider discovered in
iter_218 under the champion rule.

Steps:
  1. Load the rule from archive/iter_218/results/champion_rule.json.
  2. Initialize a 256x256 hexagonal grid with the standard 3-bit L-tromino
     seed placed at the centre.
  3. Run the simulation for 300 steps.
  4. At step 299, use flood-fill connected-component analysis to identify the
     main moving object (the glider) near its current centre of mass.
  5. Normalize the glider's cell coordinates relative to its own centre of mass.
  6. Save the list of relative coordinates as JSON to
     archive/iter_219/results/vc_glider_structure.json.
"""

import json
import sys
from pathlib import Path

import numpy as np

# ── paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_218" / "results" / "champion_rule.json"
OUT_DIR      = PROJECT_ROOT / "archive" / "iter_219" / "results"
OUT_PATH     = OUT_DIR / "vc_glider_structure.json"

# ── simulation parameters ────────────────────────────────────────────────────

GRID_SIZE    = 256
SIM_STEPS    = 300

# Standard 3-bit L-tromino seed placed at the grid centre.
# For a 128×128 grid the seed is [(63,63),(64,63),(64,64)];
# for 256×256 we offset by +64 in each dimension:
LTROMINO_OFFSET = 127  # 256 // 2 - 1
SEED_CELLS = [
    (LTROMINO_OFFSET + 0, LTROMINO_OFFSET + 0),   # (127, 127)
    (LTROMINO_OFFSET + 0, LTROMINO_OFFSET + 1),   # (127, 128)
    (LTROMINO_OFFSET + 1, LTROMINO_OFFSET + 1),   # (128, 128)
]

# Hexagonal directions (axial coordinates): E, SE, SW, W, NW, NE
HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


# ── helpers ──────────────────────────────────────────────────────────────────

def build_lut(rule_dict: dict) -> np.ndarray:
    """Build the 128-element lookup table for the 1-bit CA rule."""
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Advance the 2D grid by one synchronous CA step (toroidal wrapping)."""
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


def find_components(grid: np.ndarray) -> list:
    """Find all 6-connected hexagonal components on a toroidal grid.

    Returns a list of frozensets, each containing (row, col) coordinates.
    """
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


def center_of_mass(cells: set) -> tuple[float, float]:
    """Return the centre of mass of a set of (row, col) cells."""
    if not cells:
        return (0.0, 0.0)
    qs = [q for q, _ in cells]
    rs = [r for _, r in cells]
    return (sum(qs) / len(cells), sum(rs) / len(cells))


def normalize_coordinates(cells: set) -> list:
    """Normalize cell coordinates so the centre of mass is at (0, 0).

    Returns a sorted list of [dq, dr] lists rounded to 6 decimal places.
    """
    com_q, com_r = center_of_mass(cells)
    normalized = sorted(
        [
            [round(q - com_q, 6), round(r - com_r, 6)]
            for q, r in cells
        ],
        key=lambda p: (p[0], p[1]),
    )
    return normalized


def unwrap_com_list(com_history, prev_unwrapped, step, n):
    """Unwrap CoM using shortest-path correction for toroidal wraparound."""
    raw_r, raw_c = com_history[step]
    pr, pc = prev_unwrapped
    dr = raw_r - (pr % n)
    dc = raw_c - (pc % n)
    if dr > n / 2:
        dr -= n
    elif dr < -n / 2:
        dr += n
    if dc > n / 2:
        dc -= n
    elif dc < -n / 2:
        dc += n
    return (pr + dr, pc + dc)


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Extract v<c glider structure from iter_218 champion rule")
    print("=" * 70)

    # 1. Load champion rule ────────────────────────────────────────────────
    print(f"\n1. Loading champion rule from: {CHAMP_PATH}")
    with open(CHAMP_PATH) as f:
        rule_data = json.load(f)

    rule_dict = rule_data["rule_dict"]
    lut = build_lut(rule_dict)
    print(f"   Rule dict entries : {len(rule_dict)}")
    print(f"   Fitness           : {rule_data.get('fitness', 'N/A')}")
    print(f"   Avg velocity      : {rule_data['metrics'].get('avg_velocity', 'N/A')}")
    print(f"   Seed particles    : {rule_data['metrics']['initial_bits']}")

    # 2. Initialize 256×256 grid with L-tromino seed at centre ────────────
    print(f"\n2. Initializing {GRID_SIZE}×{GRID_SIZE} grid …")
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    initial_bits = int(grid.sum())
    print(f"   Seed at absolute positions: {SEED_CELLS}")
    print(f"   Initial bits: {initial_bits}")

    # 3. Run simulation for 300 steps, tracking centre of mass ────────────
    print(f"\n3. Running simulation for {SIM_STEPS} steps …")
    com_history = []
    for t in range(SIM_STEPS):
        grid = step_grid(grid, lut)
        rows, cols = np.where(grid > 0)
        if len(rows) > 0:
            com = (float(np.mean(rows)), float(np.mean(cols)))
        else:
            com = (0.0, 0.0)
        com_history.append(com)
        if (t + 1) % 50 == 0:
            bc = int(grid.sum())
            print(f"   Step {t+1:4d}: bits={bc:4d},  CoM≈({com[0]:6.1f}, {com[1]:6.1f})")

    # 4. Identify the main moving object at step 299 ──────────────────────
    print(f"\n4. Identifying main moving object at step {SIM_STEPS} …")
    final_com = com_history[-1]
    print(f"   Final (wrapped) CoM: ({final_com[0]:.2f}, {final_com[1]:.2f})")

    # Find all connected components on the toroidal grid
    components = find_components(grid)
    print(f"   Total components found: {len(components)}")

    # Show component sizes
    sizes = [(len(c), c) for c in components]
    sizes.sort(key=lambda x: x[0], reverse=True)
    print(f"   Largest {min(5, len(sizes))} component sizes:")
    for i, (sz, _) in enumerate(sizes[:5]):
        print(f"     #{i}: {sz} cells")

    # The glider is a small, coherent moving structure.
    # Strategy: use a clustering approach based on spatial proximity to the final CoM.
    # We look for a component whose center of mass is close to the grid CoM,
    # but we also consider that the glider may be embedded in ash.
    #
    # Better approach: look at the region around the unwrapped CoM and find
    # the densest cluster of cells there.

    # Unwrap CoM for velocity estimate
    unwrapped = list(com_history[0])  # start with wrapped CoM
    # Re-run unwrapping
    unwrapped = list(com_history[0])
    for t in range(1, SIM_STEPS):
        unwrapped = unwrap_com_list(com_history, unwrapped, t, GRID_SIZE)

    unwrapped_final = unwrapped
    print(f"   Unwrapped final CoM: ({unwrapped_final[0]:.2f}, {unwrapped_final[1]:.2f})")

    # Map unwrapped CoM back to grid coordinates
    grid_com_r = int(unwrapped_final[0]) % GRID_SIZE
    grid_com_c = int(unwrapped_final[1]) % GRID_SIZE
    print(f"   Grid CoM location: ({grid_com_r}, {grid_com_c})")

    # Strategy: find the component whose centre of mass is closest to the
    # unwrapped trajectory CoM. The glider is typically the second-largest
    # compact component (largest may be ash background).
    #
    # Sort components by size, exclude very large (>10% of grid) ash blobs,
    # then pick the one whose CoM is closest to the unwrapped trajectory.

    ash_threshold = GRID_SIZE * GRID_SIZE * 0.1  # skip very large blobs

    candidate_components = []
    for comp in components:
        comp_com = center_of_mass(comp)
        # distance from unwrapped CoM
        dr = comp_com[0] - unwrapped_final[0]
        dc = comp_com[1] - unwrapped_final[1]
        # wrap distance
        if abs(dr) > GRID_SIZE / 2:
            dr = GRID_SIZE - abs(dr) if dr > 0 else -(GRID_SIZE - abs(dr))
        if abs(dc) > GRID_SIZE / 2:
            dc = GRID_SIZE - abs(dc) if dc > 0 else -(GRID_SIZE - abs(dc))
        dist = (dr ** 2 + dc ** 2) ** 0.5

        candidate_components.append({
            "cells": comp,
            "size": len(comp),
            "co_m": comp_com,
            "dist_to_trajectory": dist,
        })

    # Sort by distance to trajectory, then by size (prefer larger but coherent)
    candidate_components.sort(key=lambda x: (x["dist_to_trajectory"], -x["size"]))

    glider = None
    for c in candidate_components:
        if c["size"] > 5 and c["size"] < 200:  # reasonable glider size
            glider = c
            break

    if glider is None:
        # Fallback: pick the component closest to trajectory regardless of size
        glider = candidate_components[0]

    glider_cells = glider["cells"]
    print(f"\n   Selected glider: {glider['size']} cells")
    print(f"   Distance to trajectory CoM: {glider['dist_to_trajectory']:.2f}")
    print(f"   Glider CoM: ({glider['co_m'][0]:.2f}, {glider['co_m'][1]:.2f})")

    # 5. Normalize coordinates relative to glider centre of mass ──────────
    print(f"\n5. Normalizing coordinates relative to centre of mass …")
    normalized = normalize_coordinates(glider_cells)
    print(f"   Number of cells in normalized structure: {len(normalized)}")

    # 6. Save to JSON ─────────────────────────────────────────────────────
    print(f"\n6. Saving to {OUT_PATH} …")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "glider_structure": normalized,
        "num_cells": len(normalized),
        "source_iteration": "iter_218",
        "source_rule": "champion_rule.json",
        "simulation_grid_size": GRID_SIZE,
        "simulation_steps": SIM_STEPS,
        "extract_step": SIM_STEPS,
        "glider_bit_count": glider["size"],
        "glider_com": [round(glider["co_m"][0], 6), round(glider["co_m"][1], 6)],
        "unwrapped_final_com": [round(unwrapped_final[0], 6), round(unwrapped_final[1], 6)],
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"   Done! Wrote {len(normalized)} relative coordinates.")

    # Print the structure for verification
    print(f"\n   Normalized glider structure:")
    for coord in normalized:
        print(f"     [{coord[0]:>8.4f}, {coord[1]:>8.4f}]")

    print("\n" + "=" * 70)
    print("Extraction complete.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
