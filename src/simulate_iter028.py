#!/usr/bin/env python3
"""
iter_028: symmetry
Tests whether a 60-degree rotated arrowhead seed produces a stable glider
with a correspondingly rotated velocity vector.

Same 5-pair permutation rule as iter_024. Only the initial condition changes:
  c=(50,50), c+b5=(49,51) [NW], c+b6=(50,51) [NE]
"""

import sys
import yaml
import numpy as np
from pathlib import Path

N = 100
STEPS = 100

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_028" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_028" / "result.yaml"

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


def shape_normalized(positions):
    if not positions:
        return frozenset()
    ctr = positions[0]
    return frozenset((q - ctr[0], r - ctr[1]) for q, r in positions)


def is_split(positions, n):
    if len(positions) < 2:
        return False
    qs = [q for q, r in positions]
    rs = [r for q, r in positions]
    return (max(qs) - min(qs) > n // 2) or (max(rs) - min(rs) > n // 2)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Rule verification: 5-pair permutation rule built successfully.")

    # Rotated arrowhead: c=(50,50), c+b5=(49,51) [NW], c+b6=(50,51) [NE]
    grid = np.zeros((N, N), dtype=np.int8)
    grid[50, 50] = 1
    grid[49, 51] = 1  # b5 = NW = (-1, +1)
    grid[50, 51] = 1  # b6 = NE = ( 0, +1)

    initial_positions = find_ones(grid)
    print(f"Initial positions: {initial_positions}")
    initial_centroid = centroid(initial_positions)
    print(f"Initial centroid: {initial_centroid}")

    positions_history = [initial_positions]
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

    initial_shape = shape_normalized(positions_history[0])
    unsplit_steps = [ph for ph in positions_history
                     if len(ph) == initial_count and not is_split(ph, N)]
    is_stable = (
        len(unsplit_steps) > STEPS // 2 and
        all(shape_normalized(ph) == initial_shape for ph in unsplit_steps)
    )

    # Velocity from unsplit steps only (avoids wrap-around jumps)
    dqs, drs = [], []
    for t in range(1, len(positions_history)):
        ph_cur = positions_history[t]
        ph_prev = positions_history[t - 1]
        if is_split(ph_cur, N) or is_split(ph_prev, N):
            continue
        ct = centroid(ph_cur)
        cp = centroid(ph_prev)
        dqs.append(ct[0] - cp[0])
        drs.append(ct[1] - cp[1])

    avg_dq = sum(dqs) / len(dqs) if dqs else 0.0
    avg_dr = sum(drs) / len(drs) if drs else 0.0
    velocity = (round(avg_dq, 6), round(avg_dr, 6))

    is_moving = abs(avg_dq) > 0.1 or abs(avg_dr) > 0.1
    velocity_consistent = bool(dqs) and (
        all(abs(d - avg_dq) < 0.6 for d in dqs) and
        all(abs(d - avg_dr) < 0.6 for d in drs)
    )

    if is_bit_conserving and is_moving and velocity_consistent and is_stable:
        behavior_class = "GLIDER"
    elif not is_bit_conserving:
        behavior_class = "CHAOTIC"
    elif not is_moving:
        behavior_class = "STATIONARY"
    else:
        behavior_class = "DECAY"

    final_centroid = centroid(positions_history[-1])

    print(f"\n=== Results ===")
    print(f"is_bit_conserving:    {is_bit_conserving}")
    print(f"is_stable:            {is_stable}")
    print(f"behavior_class:       {behavior_class}")
    print(f"glider_velocity_hex:  {velocity}")
    print(f"initial_centroid:     {initial_centroid}")
    print(f"final_centroid:       {final_centroid}")
    print(f"total_displacement:   dq={final_centroid[0]-initial_centroid[0]:.3f}, dr={final_centroid[1]-initial_centroid[1]:.3f}")
    print(f"final_positions:      {positions_history[-1]}")

    result = {
        "is_bit_conserving": bool(is_bit_conserving),
        "is_stable": bool(is_stable),
        "behavior_class": behavior_class,
        "glider_velocity_hex": list(velocity),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if behavior_class == "GLIDER" else 1


if __name__ == "__main__":
    sys.exit(main())
