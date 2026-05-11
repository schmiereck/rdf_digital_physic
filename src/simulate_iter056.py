#!/usr/bin/env python3
"""
iter_056: Composite-adjacent hypothesis.

Two 3-bit straight-line still lifes placed immediately adjacent (no gap)
on a 100x100 hexagonal grid with periodic boundaries.

Still Life 1: (20,50), (21,50), (22,50)
Still Life 2: (23,50), (24,50), (25,50)
(no gap between them – total 6 bits)

Rule: W=3 symmetric rule (A=7, B=14) from src/symmetric_rule_w3_a7_b14.json
"""

import json
import sys
import yaml
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_a7_b14.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_056" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_056" / "result.yaml"

N = 100
STEPS = 200
MAX_PERIOD_SEARCH = 100

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


def load_rule() -> dict:
    with open(RULE_PATH) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


def get_neighborhood(grid: np.ndarray, q: int, r: int) -> int:
    n = grid.shape[0]
    val = int(grid[q, r]) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        nq = (q + dq) % n
        nr = (r + dr) % n
        val |= int(grid[nq, nr]) << (5 - i)
    return val


def step_ca(grid: np.ndarray, rule: dict) -> np.ndarray:
    n = grid.shape[0]
    new_grid = np.zeros_like(grid)
    for q in range(n):
        for r in range(n):
            nbr = get_neighborhood(grid, q, r)
            mapped = rule.get(nbr, nbr)
            new_grid[q, r] = (mapped >> 6) & 1
    return new_grid


def find_ones(grid: np.ndarray):
    qs, rs = np.where(grid == 1)
    return sorted(zip(qs.tolist(), rs.tolist()))


def centroid(positions):
    if not positions:
        return (0.0, 0.0)
    return (
        sum(q for q, r in positions) / len(positions),
        sum(r for q, r in positions) / len(positions),
    )


def canonical_shape(positions):
    """Translation-invariant canonical form for cycle detection."""
    if not positions:
        return frozenset()
    sorted_pos = sorted(positions)
    q0, r0 = sorted_pos[0]
    return frozenset((q - q0, r - r0) for q, r in sorted_pos)


def detect_cycle(shapes: list, centers: list, start: int = 5, max_period: int = MAX_PERIOD_SEARCH):
    """
    Find the smallest period p such that shapes[-1] == shapes[-1-p].
    Returns (period, dq, dr) or (0, 0.0, 0.0).
    """
    n = len(shapes)
    if n < 2:
        return 0, 0.0, 0.0
    for period in range(1, min(max_period + 1, n)):
        t = n - 1
        t_prev = t - period
        if t_prev < start:
            continue
        if shapes[t] == shapes[t_prev]:
            dq = centers[t][0] - centers[t_prev][0]
            dr = centers[t][1] - centers[t_prev][1]
            # Wrap displacement for periodic boundaries
            if abs(dq) > N / 2:
                dq -= N * (1 if dq > 0 else -1)
            if abs(dr) > N / 2:
                dr -= N * (1 if dr > 0 else -1)
            return period, dq, dr
    return 0, 0.0, 0.0


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule()
    print(f"Loaded rule: {len(rule)} entries from {RULE_PATH}")

    # Initialize grid: two adjacent 3-bit straight-line still lifes, no gap
    grid = np.zeros((N, N), dtype=np.int8)
    still_life_1 = [(20, 50), (21, 50), (22, 50)]
    still_life_2 = [(23, 50), (24, 50), (25, 50)]

    for q, r in still_life_1 + still_life_2:
        grid[q % N, r % N] = 1

    initial_positions = find_ones(grid)
    initial_count = int(grid.sum())
    print(f"Initial 1-cells ({initial_count} total): {initial_positions}")

    shapes = [canonical_shape(initial_positions)]
    centers = [centroid(initial_positions)]
    bit_counts = [initial_count]

    found_period = 0
    found_dq = 0.0
    found_dr = 0.0
    stable_since = None

    for t in range(STEPS):
        grid = step_ca(grid, rule)
        pos = find_ones(grid)
        cnt = int(grid.sum())
        shape = canonical_shape(pos)

        bit_counts.append(cnt)
        shapes.append(shape)
        centers.append(centroid(pos))

        if t < 15 or t % 25 == 24:
            print(f"  t={t+1:3d}  bits={cnt:3d}  com=({centers[-1][0]:.2f}, {centers[-1][1]:.2f})")

        if cnt == initial_count and found_period == 0 and t >= 10:
            period, dq, dr = detect_cycle(shapes, centers, start=5)
            if period > 0:
                found_period = period
                found_dq = dq
                found_dr = dr
                stable_since = t + 1
                print(f"  *** Cycle detected at t={t+1}: period={period}, "
                      f"displacement=({dq:.4f}, {dr:.4f})")

    # --- Final analysis ---
    is_bit_conserving = all(c == initial_count for c in bit_counts)
    final_count = bit_counts[-1]

    if found_period == 0:
        found_period, found_dq, found_dr = detect_cycle(shapes, centers, start=5)

    net_displacement = round((found_dq ** 2 + found_dr ** 2) ** 0.5, 6)
    object_period = found_period

    if final_count == 0:
        behavior_class = "DECAY"
    elif not is_bit_conserving:
        if final_count < initial_count:
            behavior_class = "DECAY"
        else:
            behavior_class = "CHAOTIC"
    elif found_period == 0:
        behavior_class = "CHAOTIC"
    elif net_displacement > 0.5:
        behavior_class = "GLIDER"
    elif found_period == 1:
        behavior_class = "STILL_LIFE"
    else:
        behavior_class = "OSCILLATOR"

    glider_found = behavior_class == "GLIDER"

    print(f"\n=== Results ===")
    print(f"behavior_class:      {behavior_class}")
    print(f"glider_found:        {glider_found}")
    print(f"is_bit_conserving:   {is_bit_conserving}")
    print(f"final_bit_count:     {final_count}")
    print(f"object_period:       {object_period}")
    print(f"net_displacement:    {net_displacement}")
    print(f"displacement_vec:    ({found_dq:.4f}, {found_dr:.4f})")
    print(f"bit_counts range:    {min(bit_counts)} - {max(bit_counts)}")
    if stable_since:
        print(f"cycle_detected_at:   t={stable_since}")

    trace_path = RESULTS_DIR / "bit_count_trace.yaml"
    with open(trace_path, "w") as f:
        yaml.dump({"bit_counts": bit_counts}, f, default_flow_style=True)
    print(f"Written: {trace_path}")

    result = {
        "glider_found": bool(glider_found),
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "final_bit_count": int(final_count),
        "net_displacement": float(net_displacement),
        "object_period": int(object_period),
        "displacement_vec": [float(found_dq), float(found_dr)],
        "initial_bit_count": int(initial_count),
        "bit_count_min": int(min(bit_counts)),
        "bit_count_max": int(max(bit_counts)),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"Written: {RESULT_YAML}")

    return 0 if (is_bit_conserving and found_period > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
