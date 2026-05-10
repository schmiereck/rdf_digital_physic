#!/usr/bin/env python3
"""
iter_017: dynamics-2D-swap
"Swap Center with Neighbor 1" rule on a 2D hexagonal grid.

Rule: For neighborhood b0b1b2b3b4b5b6, output is b1b0b2b3b4b5b6.
New center = b1 (the first clockwise / East neighbor).
This is a simple bit-permutation that is its own inverse (reversible).
"""

import sys
import yaml
import numpy as np
from pathlib import Path

N = 50  # grid size (50x50 as specified)
STEPS = 50

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_017" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_017" / "result.yaml"

# Axial-coordinate neighbor directions in clockwise order (b1..b6)
HEX_DIRS = [
    ( 1,  0),   # b1: E
    ( 1, -1),   # b2: SE
    ( 0, -1),   # b3: SW
    (-1,  0),   # b4: W
    (-1,  1),   # b5: NW
    ( 0,  1),   # b6: NE
]


def step(grid: np.ndarray) -> np.ndarray:
    """Apply one step of the Swap-Center-with-Neighbor-1 rule.

    new_state[q, r] = old_state[q + dq1, r + dr1]
    where (dq1, dr1) = HEX_DIRS[0] = (1, 0) = East (b1).
    Implemented as a single array roll.
    """
    dq, dr = HEX_DIRS[0]  # b1 = East = (1, 0)
    # np.roll(arr, -k, axis) gives new[i] = old[i+k]
    return np.roll(grid, -dq, axis=0)


def step_reference(grid: np.ndarray) -> np.ndarray:
    """Reference cell-by-cell implementation (for validation)."""
    n = grid.shape[0]
    new = np.empty_like(grid)
    dq, dr = HEX_DIRS[0]
    for q in range(n):
        for r in range(n):
            new[q, r] = grid[(q + dq) % n, (r + dr) % n]
    return new


def find_ones(grid: np.ndarray) -> list[tuple[int, int]]:
    qs, rs = np.where(grid == 1)
    return list(zip(qs.tolist(), rs.tolist()))


def detect_oscillation_period(positions_history: list, max_period: int = 50) -> int | None:
    """Find smallest T>0 such that position[t] == position[t+T] for all available t."""
    n = len(positions_history)
    for T in range(1, min(max_period + 1, n)):
        all_match = True
        checks = 0
        for t in range(n - T):
            if len(positions_history[t]) != len(positions_history[t + T]):
                all_match = False
                break
            if positions_history[t] != positions_history[t + T]:
                all_match = False
                break
            checks += 1
        if all_match and checks > 0:
            return T
    return None


def main() -> int:
    # Validate vectorized step against reference on small grid
    test = np.zeros((5, 5), dtype=np.int8)
    test[2, 2] = 1
    assert np.array_equal(step(test), step_reference(test)), \
        "Vectorized and reference steps disagree!"

    # Initialise grid: all zeros except single '1' at center
    grid = np.zeros((N, N), dtype=np.int8)
    cq, cr = N // 2, N // 2
    grid[cq, cr] = 1

    initial_count = int(grid.sum())
    bit_counts: list[int] = [initial_count]
    positions_history: list[list[tuple[int, int]]] = [find_ones(grid)]

    print(f"Grid:          {N}x{N} (axial coords, periodic)")
    print(f"Rule:          Swap Center with Neighbor 1 (new center = East neighbor)")
    print(f"Initial cell:  ({cq}, {cr})")
    print(f"Initial count: {initial_count}")
    print(f"{'Step':>6}  {'#1s':>6}  positions")

    # Run simulation
    for t in range(STEPS):
        grid = step(grid)
        count = int(grid.sum())
        positions = find_ones(grid)
        bit_counts.append(count)
        positions_history.append(positions)

        if t < 10 or t % 10 == 9:
            print(f"  t={t+1:4d}  count={count:4d}  pos={positions[:3]}")

    # Analysis
    final_count = bit_counts[-1]
    is_bit_conserving = all(c == initial_count for c in bit_counts)

    oscillation_period = detect_oscillation_period(positions_history)

    # Determine displacement per step (for single-bit case)
    glider_velocity = None
    if is_bit_conserving and final_count == 1 and len(positions_history[0]) == 1:
        q0, r0 = positions_history[0][0]
        q1, r1 = positions_history[1][0]
        dq = int((q1 - q0 + N // 2) % N - N // 2)
        dr = int((r1 - r0 + N // 2) % N - N // 2)
        glider_velocity = (dq, dr)

    # Check if the bit returns to start after period P (stationary oscillator)
    # vs translates continuously (glider)
    is_stationary = False
    if oscillation_period is not None and is_bit_conserving and final_count == 1:
        q0, r0 = positions_history[0][0]
        # Check if all positions within one period are within a bounded region
        period_positions = {positions_history[t][0] for t in range(oscillation_period + 1)}
        # Stationary oscillator: stays near original position
        max_dist = max(
            abs(q - q0) + abs(r - r0)
            for q, r in period_positions
        )
        is_stationary = (max_dist <= 1)  # within 1 hex step

    # Classify
    if final_count == 0:
        behavior_class = "DECAY"
    elif is_bit_conserving and is_stationary and oscillation_period is not None:
        behavior_class = "STATIONARY_OSCILLATOR"
    elif is_bit_conserving and glider_velocity is not None and glider_velocity != (0, 0):
        behavior_class = "GLIDER"
    elif is_bit_conserving and final_count == initial_count:
        behavior_class = "STABLE"
    elif max(bit_counts) > 5 * initial_count:
        behavior_class = "CHAOTIC"
    else:
        behavior_class = "UNKNOWN"

    print()
    print(f"is_bit_conserving:   {is_bit_conserving}")
    print(f"behavior_class:      {behavior_class}")
    print(f"final_bit_count:     {final_count}")
    print(f"oscillation_period:  {oscillation_period}")
    print(f"glider_velocity:     {glider_velocity}")
    print(f"is_stationary:       {is_stationary}")

    # Show all positions in first few steps for analysis
    print("\nFirst 10 positions:")
    for t in range(min(11, len(positions_history))):
        print(f"  t={t:3d}: {positions_history[t]}")

    # Write result.yaml
    result = {
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "final_bit_count": int(final_count),
        "oscillation_period": int(oscillation_period) if oscillation_period is not None else None,
        "glider_velocity": list(glider_velocity) if glider_velocity else None,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)

    print(f"\nResult written to: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
