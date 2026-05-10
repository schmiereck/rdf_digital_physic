#!/usr/bin/env python3
"""
iter_027: probe-stationary-target
Two-bit pattern at (50,50) and (51,50) under the arrowhead-glider CA rule.
Checks if the pattern is a fixed point or oscillator.
"""

import sys
import math
import yaml
import numpy as np
from pathlib import Path

N = 100
STEPS = 100

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_027" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_027" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),  # b1: E
    ( 1, -1),  # b2: SE
    ( 0, -1),  # b3: SW
    (-1,  0),  # b4: W
    (-1,  1),  # b5: NW
    ( 0,  1),  # b6: NE
]


def build_rule():
    rule = list(range(128))
    pairs = [(4, 64), (12, 68), (97, 49), (88, 28)]
    for a, b in pairs:
        rule[a] = b
        rule[b] = a
    for x in range(128):
        assert bin(rule[x]).count('1') == bin(x).count('1'), f"popcount mismatch at {x}"
        assert rule[rule[x]] == x, f"not involution at {x}"
    return rule


RULE = build_rule()


def get_neighborhood(grid, q, r):
    n = grid.shape[0]
    val = int(grid[q, r]) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        nq = (q + dq) % n
        nr = (r + dr) % n
        val |= int(grid[nq, nr]) << (5 - i)
    return val


def step_ca(grid: np.ndarray) -> np.ndarray:
    n = grid.shape[0]
    new_grid = np.zeros_like(grid)
    for q in range(n):
        for r in range(n):
            nbr = get_neighborhood(grid, q, r)
            new_val = (RULE[nbr] >> 6) & 1
            new_grid[q, r] = new_val
    return new_grid


def find_ones(grid):
    qs, rs = np.where(grid == 1)
    return sorted(zip(qs.tolist(), rs.tolist()))


def centroid(positions):
    if not positions:
        return (0.0, 0.0)
    return (sum(q for q, r in positions) / len(positions),
            sum(r for q, r in positions) / len(positions))


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    grid = np.zeros((N, N), dtype=np.int8)
    grid[50, 50] = 1
    grid[51, 50] = 1

    print(f"Initial positions: {find_ones(grid)}")
    initial_center = centroid(find_ones(grid))
    print(f"Initial centroid: {initial_center}")

    positions_history = [find_ones(grid)]
    bit_counts = [int(grid.sum())]

    for t in range(STEPS):
        grid = step_ca(grid)
        pos = find_ones(grid)
        cnt = int(grid.sum())
        positions_history.append(pos)
        bit_counts.append(cnt)
        if t < 10 or t % 20 == 19:
            print(f"  t={t+1:3d}  bits={cnt}  pos={pos}")

    # Analysis
    initial_count = bit_counts[0]
    is_bit_conserving = all(c == initial_count for c in bit_counts)

    final_positions = positions_history[-1]
    final_center = centroid(final_positions)
    net_displacement = math.sqrt(
        (final_center[0] - initial_center[0])**2 +
        (final_center[1] - initial_center[1])**2
    )

    # Classify behavior
    all_same = all(ph == positions_history[0] for ph in positions_history)
    if all_same:
        behavior_class = "STATIONARY_FIXED_POINT"
    elif not is_bit_conserving:
        behavior_class = "DECAY"
    else:
        # Check for oscillator: look for period
        # Check net displacement
        if net_displacement >= 2.0:
            behavior_class = "GLIDER"
        else:
            # Check if pattern repeats (oscillator) or wanders (chaotic)
            shapes_seen = set()
            is_oscillator = False
            for ph in positions_history:
                frozen = frozenset(ph)
                if frozen in shapes_seen:
                    is_oscillator = True
                    break
                shapes_seen.add(frozen)
            if is_oscillator:
                behavior_class = "STATIONARY_OSCILLATOR"
            else:
                behavior_class = "CHAOTIC"

    print(f"\n=== Results ===")
    print(f"is_bit_conserving:    {is_bit_conserving}")
    print(f"behavior_class:       {behavior_class}")
    print(f"initial_center:       {initial_center}")
    print(f"final_center:         {final_center}")
    print(f"net_displacement:     {net_displacement:.6f}")
    print(f"final_positions:      {final_positions}")

    result = {
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "net_displacement": round(net_displacement, 6),
        "final_pattern_coords": [[int(q), int(r)] for q, r in final_positions],
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    success = is_bit_conserving and net_displacement < 2.0
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
