#!/usr/bin/env python3
"""
iter_016: dynamics-2D-hex
Bit-rotation rule on a 2D hexagonal grid with 7-cell neighborhood.

Rule: "Rotate Right"
  Input neighborhood:  b0 b1 b2 b3 b4 b5 b6  (b0=center, b1-b6=CW neighbors)
  Output:              b6 b0 b1 b2 b3 b4 b5
  New center = new b0 = b6  (the last clockwise neighbor)
"""

import sys
import yaml
import numpy as np
from pathlib import Path

N = 51  # grid size (odd so center cell is well-defined)
STEPS = 100

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_016" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_016" / "result.yaml"

# Axial-coordinate neighbor directions in clockwise order (b1..b6)
# Using the standard hex axial system: axes q (East) and r (NE)
HEX_DIRS = [
    ( 1,  0),   # b1: E
    ( 1, -1),   # b2: SE
    ( 0, -1),   # b3: SW
    (-1,  0),   # b4: W
    (-1,  1),   # b5: NW
    ( 0,  1),   # b6: NE
]


def step_vectorized(grid: np.ndarray) -> np.ndarray:
    """Apply one step of the Rotate-Right rule to the entire grid.

    new_state[q, r] = old_state[q + dq6, r + dr6]
    where (dq6, dr6) = HEX_DIRS[5] = (0, 1).
    Implemented as an array roll (exact, zero-allocation beyond the output).
    """
    dq, dr = HEX_DIRS[5]  # b6 direction
    # np.roll(arr, -k, axis) moves element at index i+k to index i,
    # i.e. new[i] = old[i+k].  So roll by -dq and -dr.
    new = np.roll(grid, -dq, axis=0)
    if dr:
        new = np.roll(new, -dr, axis=1)
    return new


def step_reference(grid: np.ndarray) -> np.ndarray:
    """Reference cell-by-cell implementation (used for validation)."""
    n = grid.shape[0]
    new = np.empty_like(grid)
    for q in range(n):
        for r in range(n):
            dq, dr = HEX_DIRS[5]
            new[q, r] = grid[(q + dq) % n, (r + dr) % n]
    return new


def find_ones(grid: np.ndarray) -> list[tuple[int, int]]:
    qs, rs = np.where(grid == 1)
    return list(zip(qs.tolist(), rs.tolist()))


def detect_glider_period(positions_history: list) -> int | None:
    """Return smallest T>0 such that glider pattern repeats at same relative position."""
    if not positions_history or len(positions_history[0]) != 1:
        return None
    q0, r0 = positions_history[0][0]
    if len(positions_history) < 2 or len(positions_history[1]) != 1:
        return None
    q1, r1 = positions_history[1][0]
    dq = (q1 - q0) % N
    dr = (r1 - r0) % N
    # For a pure-translation glider the shape never changes; period = 1.
    # Check that all positions follow t*(dq,dr) exactly.
    for t in range(1, min(len(positions_history), 20)):
        if len(positions_history[t]) != 1:
            return None
        qt, rt = positions_history[t][0]
        if qt != (q0 + t * dq) % N or rt != (r0 + t * dr) % N:
            return None
    return 1  # single-bit glider with constant velocity: internal period = 1


def main() -> int:
    # --- Validate vectorized step against reference on small grid ---
    test = np.zeros((5, 5), dtype=np.int8)
    test[2, 2] = 1
    assert np.array_equal(step_vectorized(test), step_reference(test)), \
        "Vectorized and reference steps disagree!"

    # --- Initialise grid ---
    grid = np.zeros((N, N), dtype=np.int8)
    cq, cr = N // 2, N // 2
    grid[cq, cr] = 1

    initial_count = int(grid.sum())
    bit_counts: list[int] = [initial_count]
    positions_history: list[list[tuple[int, int]]] = [find_ones(grid)]

    print(f"Grid:          {N}x{N} (axial coords, periodic)")
    print(f"Initial cell:  ({cq}, {cr})")
    print(f"Initial count: {initial_count}")
    print(f"{'Step':>6}  {'#1s':>6}  positions")

    # --- Run simulation ---
    for t in range(STEPS):
        grid = step_vectorized(grid)
        count = int(grid.sum())
        positions = find_ones(grid)
        bit_counts.append(count)
        positions_history.append(positions)

        if t % 10 == 9 or t < 7:
            print(f"  t={t+1:4d}  count={count:4d}  pos={positions[:3]}")

    # --- Analysis ---
    final_count = bit_counts[-1]
    is_bit_conserving = (final_count == initial_count)

    glider_velocity_hex = None
    glider_period = None

    if is_bit_conserving and final_count == 1:
        # Compute per-step displacement from first two frames
        q0, r0 = positions_history[0][0]
        q1, r1 = positions_history[1][0]
        dq = int(q1 - q0)
        dr = int(r1 - r0)

        # Verify linear motion over all recorded steps
        is_linear = all(
            len(positions_history[t]) == 1
            and positions_history[t][0] == ((q0 + t * dq) % N, (r0 + t * dr) % N)
            for t in range(1, STEPS + 1)
        )

        if is_linear:
            glider_velocity_hex = (dq, dr)
            glider_period = detect_glider_period(positions_history)

    # Classify
    if final_count == 0:
        behavior_class = "DECAY"
    elif glider_velocity_hex is not None and glider_velocity_hex != (0, 0):
        behavior_class = "GLIDER"
    elif is_bit_conserving and final_count == initial_count:
        behavior_class = "STABLE"
    elif max(bit_counts) > 5 * initial_count:
        behavior_class = "CHAOTIC"
    else:
        behavior_class = "DECAY"

    print()
    print(f"is_bit_conserving:   {is_bit_conserving}")
    print(f"behavior_class:      {behavior_class}")
    print(f"final_bit_count:     {final_count}")
    print(f"glider_velocity_hex: {glider_velocity_hex}")
    print(f"glider_period:       {glider_period}")

    # --- Write result.yaml ---
    result = {
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "final_bit_count": int(final_count),
        "glider_velocity_hex": list(glider_velocity_hex) if glider_velocity_hex else None,
        "glider_period": int(glider_period) if glider_period is not None else None,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)

    print(f"\nResult written to: {RESULT_YAML}")

    return 0 if behavior_class == "GLIDER" else 1


if __name__ == "__main__":
    sys.exit(main())
