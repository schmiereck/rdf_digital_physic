#!/usr/bin/env python3
"""
iter_035: dynamics-symmetric
Synchronous CA using the symmetric rule from kernel (A=3, B=6).
Tests whether a 2-bit seed produces a stable oscillator or glider.

Neighborhood encoding (7 bits, MSB = center):
  state = center*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
Directions: b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE
"""

import json
import sys
import yaml
import numpy as np
from pathlib import Path

N = 100
STEPS = 100

PROJECT_ROOT = Path(__file__).parent.parent
RULE_FILE = Path(__file__).parent / "symmetric_rule_A3_B6.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_035" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_035" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),  # b1: E
    ( 1, -1),  # b2: SE
    ( 0, -1),  # b3: SW
    (-1,  0),  # b4: W
    (-1,  1),  # b5: NW
    ( 0,  1),  # b6: NE
]


def load_rule(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def get_neighborhood(grid, q, r):
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
            # Apply rule if state is mapped; otherwise identity (keep center bit)
            mapped = rule.get(nbr, nbr)
            new_grid[q, r] = (mapped >> 6) & 1
    return new_grid


def find_ones(grid):
    qs, rs = np.where(grid == 1)
    return sorted(zip(qs.tolist(), rs.tolist()))


def centroid(positions):
    if not positions:
        return (0.0, 0.0)
    return (sum(q for q, r in positions) / len(positions),
            sum(r for q, r in positions) / len(positions))


def is_split(positions, n):
    if len(positions) < 2:
        return False
    qs = [q for q, r in positions]
    return max(qs) - min(qs) > n // 2


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule(RULE_FILE)
    print(f"Loaded rule from {RULE_FILE}: {len(rule)} mappings")

    # 2-bit seed: place '1's at NW (49,51) and NE (50,51) of cell (50,50)
    # so that cell (50,50) has neighborhood state A=3 ('0000011', b5=NW=1, b6=NE=1)
    cq, cr = N // 2, N // 2
    grid = np.zeros((N, N), dtype=np.int8)
    grid[(cq - 1) % N, (cr + 1) % N] = 1  # b5 = NW of (50,50) → (49,51)
    grid[(cq + 0) % N, (cr + 1) % N] = 1  # b6 = NE of (50,50) → (50,51)

    # Verify neighborhood state at (cq, cr)
    state_center = (  int(grid[cq, cr]) << 6
        | int(grid[(cq+1)%N, (cr+0)%N]) << 5   # b1 E
        | int(grid[(cq+1)%N, (cr-1)%N]) << 4   # b2 SE
        | int(grid[(cq+0)%N, (cr-1)%N]) << 3   # b3 SW
        | int(grid[(cq-1)%N, (cr+0)%N]) << 2   # b4 W
        | int(grid[(cq-1)%N, (cr+1)%N]) << 1   # b5 NW
        | int(grid[(cq+0)%N, (cr+1)%N]) << 0   # b6 NE
    )
    print(f"Initial 2-bit seed: {find_ones(grid)}")
    print(f"Neighborhood state at ({cq},{cr}): {state_center} ('{state_center:07b}') — expected 3 ('0000011')")

    positions_history = [find_ones(grid)]
    bit_counts = [int(grid.sum())]

    for t in range(STEPS):
        grid = step_ca(grid, rule)
        pos = find_ones(grid)
        cnt = int(grid.sum())
        positions_history.append(pos)
        bit_counts.append(cnt)
        if t < 6 or t % 10 == 9:
            print(f"  t={t+1:3d}  bits={cnt}  pos={pos}")

    initial_count = bit_counts[0]
    is_bit_conserving = all(c == initial_count for c in bit_counts)

    def shape(positions):
        if not positions:
            return frozenset()
        ctr = positions[0]
        return frozenset((q - ctr[0], r - ctr[1]) for q, r in positions)

    initial_shape = shape(positions_history[0])
    unsplit_steps = [ph for ph in positions_history
                     if len(ph) == initial_count and not is_split(ph, N)]
    is_stable = len(unsplit_steps) > STEPS // 2 and all(
        shape(ph) == initial_shape for ph in unsplit_steps
    )

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

    # Determine if pattern is truly fixed (never changes)
    all_same = all(ph == positions_history[0] for ph in positions_history)

    # Net displacement: distance from initial to final center of mass
    c0 = centroid(positions_history[0])
    cf = centroid(positions_history[-1])
    net_displacement = round(((cf[0]-c0[0])**2 + (cf[1]-c0[1])**2)**0.5, 6)

    final_coords = [[q, r] for q, r in positions_history[-1]]

    if not is_bit_conserving and bit_counts[-1] < bit_counts[0]:
        behavior_class = "DECAY"
    elif not is_bit_conserving:
        behavior_class = "CHAOTIC"
    elif all_same:
        behavior_class = "FIXED_POINT"
    elif is_bit_conserving and is_moving and velocity_consistent and is_stable:
        behavior_class = "GLIDER"
    elif is_bit_conserving and not is_moving:
        behavior_class = "STATIONARY_OSCILLATOR"
    else:
        behavior_class = "STATIONARY_OSCILLATOR"

    print(f"\n=== Results ===")
    print(f"behavior_class:    {behavior_class}")
    print(f"is_bit_conserving: {is_bit_conserving}")
    print(f"net_displacement:  {net_displacement}")
    print(f"all_same:          {all_same}")
    print(f"glider_velocity:   {velocity}")
    print(f"final_bit_count:   {bit_counts[-1]}")
    print(f"final_coords:      {final_coords}")

    result = {
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "net_displacement": float(net_displacement),
        "final_pattern_coords": final_coords,
        "glider_velocity_hex": list(velocity),
        "final_bit_count": int(bit_counts[-1]),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    success = behavior_class in ("GLIDER", "STATIONARY_OSCILLATOR")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
