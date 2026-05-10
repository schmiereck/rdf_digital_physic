#!/usr/bin/env python3
"""
iter_032: symmetrized-rule
A fully symmetrized, reversible, bit-conserving rule produces a stable,
non-trivial pattern (glider or oscillator) from a single-bit seed.
"""

import json
import sys
import yaml
import numpy as np
from pathlib import Path

N = 100
STEPS = 100
SEED_Q, SEED_R = 50, 50

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_032" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_032" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),  # b1: E
    ( 1, -1),  # b2: SE
    ( 0, -1),  # b3: SW
    (-1,  0),  # b4: W
    (-1,  1),  # b5: NW
    ( 0,  1),  # b6: NE
]

A = '0100100'   # W=2: center=0, E=1, W=1
B = '1000010'   # W=2: center=1, NW=1


def rotate_neighborhood(state: str, steps: int) -> str:
    """Rotate neighbor bits b1..b6 of '0b1b2b3b4b5b6' rightward by steps (60-deg CW each)."""
    center = state[0]
    neighbors = state[1:]
    steps = steps % 6
    if steps == 0:
        return state
    return center + neighbors[-steps:] + neighbors[:-steps]


def build_rule():
    rule = list(range(128))
    print("Generator rotations:")
    for i in range(6):
        a_rot = rotate_neighborhood(A, i)
        b_rot = rotate_neighborhood(B, i)
        a_int = int(a_rot, 2)
        b_int = int(b_rot, 2)
        print(f"  rot={i}: {a_rot}({a_int}) <-> {b_rot}({b_int})")
        rule[a_int] = b_int
        rule[b_int] = a_int
    return rule


def get_neighborhood(grid, q, r):
    n = grid.shape[0]
    val = int(grid[q, r]) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        nq = (q + dq) % n
        nr = (r + dr) % n
        val |= int(grid[nq, nr]) << (5 - i)
    return val


def step_ca(grid: np.ndarray, rule) -> np.ndarray:
    n = grid.shape[0]
    new_grid = np.zeros_like(grid)
    for q in range(n):
        for r in range(n):
            nbr = get_neighborhood(grid, q, r)
            new_grid[q, r] = (rule[nbr] >> 6) & 1
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

    rule = build_rule()

    non_identity = [(i, rule[i]) for i in range(128) if rule[i] != i]
    print(f"\nNon-identity mappings: {len(non_identity)}")
    for src, dst in non_identity:
        center_in  = (src >> 6) & 1
        center_out = (dst >> 6) & 1
        print(f"  {src:3d} ({src:07b}) -> {dst:3d} ({dst:07b})  "
              f"center: {center_in}->{center_out}  "
              f"popcount: {bin(src).count('1')}->{bin(dst).count('1')}")

    is_involution = all(rule[rule[x]] == x for x in range(128))
    is_bc_rule    = all(bin(rule[x]).count('1') == bin(x).count('1') for x in range(128))
    print(f"\nRule is involution:     {is_involution}")
    print(f"Rule is bit-conserving: {is_bc_rule}")

    # Initial condition: single bit at center
    grid = np.zeros((N, N), dtype=np.int8)
    grid[SEED_Q, SEED_R] = 1
    initial_count = int(grid.sum())
    print(f"\nInitial state: single bit at ({SEED_Q},{SEED_R}), count={initial_count}")
    print(f"Seed neighborhood state: {get_neighborhood(grid, SEED_Q, SEED_R)} "
          f"-> rule output: {rule[get_neighborhood(grid, SEED_Q, SEED_R)]}")

    # Save initial state
    with open(RESULTS_DIR / "grid_t0000.json", "w") as f:
        json.dump({"step": 0, "bit_count": initial_count, "ones": find_ones(grid)},
                  f, separators=(",", ":"))

    bit_counts = [initial_count]
    positions_history = [find_ones(grid)]

    for t in range(STEPS):
        grid = step_ca(grid, rule)
        cnt = int(grid.sum())
        bit_counts.append(cnt)
        ones = find_ones(grid)
        positions_history.append(ones)

        if t < 5 or (t + 1) % 25 == 0:
            print(f"  t={t+1:3d}  bits={cnt}  positions={ones[:6]}")

    # Save final state
    with open(RESULTS_DIR / f"grid_t{STEPS:04d}.json", "w") as f:
        json.dump({"step": STEPS, "bit_count": int(grid.sum()), "ones": find_ones(grid)},
                  f, separators=(",", ":"))

    final_count = bit_counts[-1]
    last_20_counts    = bit_counts[-20:]
    last_20_positions = positions_history[-20:]

    count_stable     = len(set(last_20_counts)) == 1
    position_stable  = all(p == last_20_positions[0] for p in last_20_positions)
    centroids_20     = [centroid(p) for p in last_20_positions]
    moving           = any(abs(centroids_20[i+1][0] - centroids_20[i][0]) > 0.1 or
                           abs(centroids_20[i+1][1] - centroids_20[i][1]) > 0.1
                           for i in range(len(centroids_20) - 1))

    never_changed = all(c == initial_count for c in bit_counts)

    if final_count == 0:
        bclass = "DECAY"
    elif final_count >= 20 or not count_stable:
        bclass = "CHAOTIC_GROWTH"
    elif final_count == 1 and never_changed:
        bclass = "TRIVIAL_SHIFT"
    elif moving and count_stable:
        bclass = "STABLE_GLIDER"
    elif position_stable:
        bclass = "STATIONARY_OSCILLATOR"
    elif count_stable:
        bclass = "STATIONARY_OSCILLATOR"
    else:
        bclass = "TRIVIAL_SHIFT"

    if final_count == 1 and never_changed:
        summary = "1-bit trivial fixed point – single bit never moved"
    elif position_stable:
        summary = f"{final_count}-bit still life"
    elif moving and count_stable:
        dq = centroids_20[-1][0] - centroids_20[0][0]
        dr = centroids_20[-1][1] - centroids_20[0][1]
        summary = f"{final_count}-bit glider, centroid drift ({dq:.1f},{dr:.1f}) over 20 steps"
    elif count_stable:
        summary = f"{final_count}-bit oscillator"
    else:
        summary = f"{final_count}-bit chaotic pattern"

    # Task spec: is_bit_conserving = true if bit count CHANGES from initial
    is_bc_sim = not never_changed

    print(f"\n=== Analysis ===")
    print(f"Initial count:         {initial_count}")
    print(f"Final count (t={STEPS}): {final_count}")
    print(f"Never changed:         {never_changed}")
    print(f"Count stable (last 20):{count_stable}")
    print(f"Position stable:       {position_stable}")
    print(f"Moving:                {moving}")
    print(f"Behavior class:        {bclass}")
    print(f"Final summary:         {summary}")

    result = {
        "is_bit_conserving": bool(is_bc_sim),
        "behavior_class": bclass,
        "final_bit_count": int(final_count),
        "final_pattern_summary": summary,
        "rule_non_identity_count": len(non_identity),
        "rule_is_involution": bool(is_involution),
        "rule_is_bit_conserving": bool(is_bc_rule),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    success = final_count > 1 and final_count < 20 and bclass in ("STABLE_GLIDER", "STATIONARY_OSCILLATOR")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
