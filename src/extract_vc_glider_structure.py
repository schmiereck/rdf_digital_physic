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
  4. At step 300, get the coordinates of all active cells (np.where(grid > 0)).
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
CHAMP_PATH = PROJECT_ROOT / "archive" / "iter_218" / "results" / "champion_rule.json"
OUT_DIR = PROJECT_ROOT / "archive" / "iter_219" / "results"
OUT_PATH = OUT_DIR / "vc_glider_structure.json"

# ── simulation parameters ────────────────────────────────────────────────────

GRID_SIZE = 256
SIM_STEPS = 300

# Standard 3-bit L-tromino seed placed at the grid centre.
# For a 128x128 grid the seed is [(63,63),(64,63),(64,64)];
# for 256x256 we offset by +64 in each dimension:
LTROMINO_OFFSET = 127  # 256 // 2 - 1
SEED_CELLS = [
    (LTROMINO_OFFSET + 0, LTROMINO_OFFSET + 0),   # (127, 127)
    (LTROMINO_OFFSET + 0, LTROMINO_OFFSET + 1),   # (127, 128)
    (LTROMINO_OFFSET + 1, LTROMINO_OFFSET + 1),   # (128, 128)
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
    e = np.roll(grid, -1, axis=0)
    w = np.roll(grid, 1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid, 1, axis=1)
    se = np.roll(e, 1, axis=1)
    nw = np.roll(w, -1, axis=1)

    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16) << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16) << 2)
        | (nw.astype(np.uint16) << 1)
        | ne.astype(np.uint16)
    ).astype(np.uint8)

    return lut[state]


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

    # 2. Initialize 256x256 grid with L-tromino seed at centre ────────────
    print(f"\n2. Initializing {GRID_SIZE}x{GRID_SIZE} grid …")
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
            print(f"   Step {t + 1:4d}: bits={bc:4d},  CoM≈({com[0]:6.1f}, {com[1]:6.1f})")

    # Unwrap CoM to handle toroidal wraparound
    unwrapped = list(com_history[0])
    for t in range(1, SIM_STEPS):
        unwrapped = unwrap_com_list(com_history, unwrapped, t, GRID_SIZE)

    unwrapped_final = unwrapped
    final_com = com_history[-1]
    print(f"\n   Final (wrapped)  CoM: ({final_com[0]:.2f}, {final_com[1]:.2f})")
    print(f"   Unwrapped final CoM: ({unwrapped_final[0]:.2f}, {unwrapped_final[1]:.2f})")

    # 4. Extract coordinates of all active cells at step 300 ──────────────
    print(f"\n4. Extracting active cell coordinates at step {SIM_STEPS} …")
    rows, cols = np.where(grid > 0)
    active_count = len(rows)
    print(f"   Total active cells: {active_count}")

    if active_count == 0:
        print("   ERROR: No active cells found at final step!")
        return 1

    # Build list of (row, col) pairs
    active_cells = list(zip(rows.tolist(), cols.tolist()))

    # 5. Normalize coordinates relative to centre of mass ─────────────────
    print(f"\n5. Normalizing coordinates relative to centre of mass …")
    com_r = float(np.mean(rows))
    com_c = float(np.mean(cols))
    print(f"   Centre of mass (wrapped): ({com_r:.4f}, {com_c:.4f})")

    # Unwrap the CoM for the final step to avoid toroidal wrap issues
    unwrapped_com_r = unwrapped_final[0]
    unwrapped_com_c = unwrapped_final[1]
    print(f"   Centre of mass (unwrapped): ({unwrapped_com_r:.4f}, {unwrapped_com_c:.4f})")

    # Calculate relative coordinates using unwrapped CoM
    # Map unwrapped CoM back to grid-local reference frame
    grid_com_r = unwrapped_com_r % GRID_SIZE
    grid_com_c = unwrapped_com_c % GRID_SIZE

    relative_coords = []
    for r, c in active_cells:
        # Calculate displacement from unwrapped CoM, accounting for toroidal wrap
        dr = r - unwrapped_com_r
        dc = c - unwrapped_com_c
        # Wrap shortest distance
        if dr > GRID_SIZE / 2:
            dr -= GRID_SIZE
        elif dr < -GRID_SIZE / 2:
            dr += GRID_SIZE
        if dc > GRID_SIZE / 2:
            dc -= GRID_SIZE
        elif dc < -GRID_SIZE / 2:
            dc += GRID_SIZE
        relative_coords.append([round(dr, 6), round(dc, 6)])

    # Sort for deterministic output
    relative_coords.sort(key=lambda p: (p[0], p[1]))

    print(f"   Number of relative coordinates: {len(relative_coords)}")

    # 6. Save to JSON with key "structure" ────────────────────────────────
    print(f"\n6. Saving to {OUT_PATH} …")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "structure": relative_coords,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"   Done! Wrote {len(relative_coords)} relative coordinates.")

    # Print the structure for verification
    print(f"\n   Normalized glider structure (first 20 entries):")
    for coord in relative_coords[:20]:
        print(f"     [{coord[0]:>8.4f}, {coord[1]:>8.4f}]")
    if len(relative_coords) > 20:
        print(f"     ... ({len(relative_coords) - 20} more entries)")

    print("\n" + "=" * 70)
    print("Extraction complete.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
