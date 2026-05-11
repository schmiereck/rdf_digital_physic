#!/usr/bin/env python3
"""
iter_050: Simulate the W=3 symmetric rule (A=7, B=14) from a 3-bit seed.

Hypothesis: dynamics-w3 — the symmetric rule from the W=3 kernel (A=7, B=14)
produces a stable, bit-conserving, non-trivial object from a 3-bit seed.

Grid: 100x100 hexagonal, periodic boundaries.
Steps: 200
Rule: loaded from src/symmetric_rule_w3_a7_b14.json

Initial condition: 3-bit seed creating neighborhood B=14 for center (50,50):
  1's at E=(51,50), SE=(51,49), SW=(50,49)
"""

import sys
import json
import yaml
import numpy as np
from pathlib import Path

from generate_w3_rule import generate_w3_rule, RULE_PATH

N = 100
STEPS = 200
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_050" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_050" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),   # b1: E
    ( 1, -1),   # b2: SE
    ( 0, -1),   # b3: SW
    (-1,  0),   # b4: W
    (-1,  1),   # b5: NW
    ( 0,  1),   # b6: NE
]


def load_rule() -> dict:
    if not RULE_PATH.exists():
        print(f"Rule file not found at {RULE_PATH}, generating...")
        generate_w3_rule()
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
    return (sum(q for q, r in positions) / len(positions),
            sum(r for q, r in positions) / len(positions))


def canonical_shape(positions):
    if not positions:
        return frozenset()
    q0, r0 = positions[0]
    return frozenset((q - q0, r - r0) for q, r in positions)


def detect_period(shapes: list, start: int = 10, max_period: int = 50) -> int:
    n = len(shapes)
    for period in range(1, max_period + 1):
        if n - 1 < period:
            break
        matches = 0
        checks = 0
        for t in range(start, n):
            if t - period < 0:
                continue
            checks += 1
            if shapes[t] == shapes[t - period]:
                matches += 1
        if checks > 0 and matches == checks:
            return period
    return 0


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate rule file if needed, then load it
    if not RULE_PATH.exists():
        generate_w3_rule()
    rule = load_rule()
    print(f"Loaded rule from {RULE_PATH} ({len(rule)} entries)")

    # Initial condition: 3-bit seed creating neighborhood B=14 for center (50,50)
    # B=14 LSB = '0001110': center=0, E=1, SE=1, SW=1
    # Place 1's at E=(51,50), SE=(51,49), SW=(50,49)
    cq, cr = 50, 50
    grid = np.zeros((N, N), dtype=np.int8)
    grid[(cq + 1) % N, (cr + 0) % N] = 1   # E
    grid[(cq + 1) % N, (cr - 1) % N] = 1   # SE
    grid[(cq + 0) % N, (cr - 1) % N] = 1   # SW

    # Verify center neighborhood
    nbr_center = get_neighborhood(grid, cq, cr)
    print(f"Seed cells: {find_ones(grid)}")
    print(f"Center ({cq},{cr}) neighborhood: {nbr_center} ('{nbr_center:07b}')")
    print(f"Expected B_MSB=56 ('{56:07b}')")

    positions_history = [find_ones(grid)]
    shapes_history = [canonical_shape(find_ones(grid))]
    bit_counts = [int(grid.sum())]

    for t in range(STEPS):
        grid = step_ca(grid, rule)
        pos = find_ones(grid)
        cnt = int(grid.sum())
        positions_history.append(pos)
        shapes_history.append(canonical_shape(pos) if pos else frozenset())
        bit_counts.append(cnt)
        if t < 10 or t % 20 == 19:
            print(f"  t={t+1:3d}  bits={cnt}  pos={pos}")

    initial_count = bit_counts[0]
    settle_step = min(10, STEPS // 10)
    settled_counts = bit_counts[settle_step:]
    is_bit_conserving = all(c == initial_count for c in bit_counts)

    all_same = all(ph == positions_history[settle_step] for ph in positions_history[settle_step:])

    c0 = centroid(positions_history[settle_step])
    cf = centroid(positions_history[-1])
    net_displacement = round(((cf[0] - c0[0])**2 + (cf[1] - c0[1])**2)**0.5, 6)

    oscillation_period = detect_period(shapes_history, start=settle_step + 5, max_period=50)

    dqs, drs = [], []
    for t in range(1, len(positions_history)):
        if not positions_history[t] or not positions_history[t-1]:
            continue
        ct = centroid(positions_history[t])
        cp = centroid(positions_history[t-1])
        dqs.append(ct[0] - cp[0])
        drs.append(ct[1] - cp[1])

    avg_dq = sum(dqs) / len(dqs) if dqs else 0.0
    avg_dr = sum(drs) / len(drs) if drs else 0.0
    is_moving = abs(avg_dq) > 0.1 or abs(avg_dr) > 0.1
    velocity_consistent = bool(dqs) and (
        all(abs(d - avg_dq) < 0.6 for d in dqs) and
        all(abs(d - avg_dr) < 0.6 for d in drs)
    )

    if bit_counts[-1] == 0:
        behavior_class = "ANNIHILATION"
    elif not is_bit_conserving and bit_counts[-1] < bit_counts[0]:
        behavior_class = "DECAY"
    elif not is_bit_conserving:
        behavior_class = "CHAOTIC"
    elif all_same:
        behavior_class = "FIXED_POINT"
    elif is_bit_conserving and is_moving and velocity_consistent:
        behavior_class = "GLIDER"
    elif is_bit_conserving and oscillation_period > 1:
        behavior_class = "STATIONARY_OSCILLATOR"
    elif is_bit_conserving and not is_moving:
        behavior_class = "STATIONARY_OSCILLATOR"
    else:
        behavior_class = "STATIONARY_OSCILLATOR"

    print(f"\n=== Results ===")
    print(f"behavior_class:      {behavior_class}")
    print(f"is_bit_conserving:   {is_bit_conserving}")
    print(f"net_displacement:    {net_displacement}")
    print(f"oscillation_period:  {oscillation_period}")
    print(f"all_same (fixed pt): {all_same}")
    print(f"avg_velocity:        ({round(avg_dq,4)}, {round(avg_dr,4)})")
    print(f"final_bit_count:     {bit_counts[-1]}")
    print(f"bit_counts min/max:  {min(bit_counts)}/{max(bit_counts)}")

    result = {
        "kernel_A": KERNEL_A_LSB,
        "kernel_B": KERNEL_B_LSB,
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "net_displacement": float(net_displacement),
        "oscillation_period": int(oscillation_period),
        "final_bit_count": int(bit_counts[-1]),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    success = (
        bit_counts[-1] == initial_count
        and behavior_class in ("GLIDER", "STATIONARY_OSCILLATOR")
        and not all_same
    )
    return 0 if success else 1


KERNEL_A_LSB = 7
KERNEL_B_LSB = 14

if __name__ == "__main__":
    sys.exit(main())
