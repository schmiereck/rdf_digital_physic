#!/usr/bin/env python3
"""
iter_044 Part 2: Generate 6-fold symmetric rule from contiguous kernel
and simulate on a 100x100 hexagonal grid.

Contiguous kernel (from find_contiguous_kernel.py):
  LSB encoding:  A=3  ('0000011'), B=6 ('0000110')
  MSB encoding:  A=96 ('1100000'), B=48 ('0110000')

Neighborhood encoding (7 bits, MSB = center = bit6):
  state = c*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
  Directions: b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE
"""

import sys
import os
import yaml
import numpy as np
from pathlib import Path

from find_contiguous_kernel import find_contiguous_kernel, orbit as lsb_orbit

N = 100
STEPS = 100
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_044" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_044" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),   # b1: E
    ( 1, -1),   # b2: SE
    ( 0, -1),   # b3: SW
    (-1,  0),   # b4: W
    (-1,  1),   # b5: NW
    ( 0,  1),   # b6: NE
]


# --- Rule generation ---

def rotate60_msb(state: int) -> int:
    """60-degree CW rotation of 7-bit state (bit6=center).
    Maps: b1->b2, b2->b3, ..., b6->b1  (content at b1 moves to b2, etc.)
    Equivalently: new_b1=old_b6, new_b2=old_b1, ..., new_b6=old_b5
    """
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def lsb_to_msb(state_lsb: int) -> int:
    """Convert 7-bit state from LSB-center (bit0=center) to MSB-center (bit6=center)."""
    result = 0
    for i in range(7):
        bit = (state_lsb >> i) & 1
        result |= bit << (6 - i)
    return result


def generate_rule(A_lsb: int, B_lsb: int) -> dict:
    A = lsb_to_msb(A_lsb)
    B = lsb_to_msb(B_lsb)
    print(f"Kernel LSB: A={A_lsb} ('{A_lsb:07b}'), B={B_lsb} ('{B_lsb:07b}')")
    print(f"Kernel MSB: A={A} ('{A:07b}'), B={B} ('{B:07b}')")

    rule = {i: i for i in range(128)}
    a_rot, b_rot = A, B
    for i in range(6):
        rule[a_rot] = b_rot
        rule[b_rot] = a_rot
        print(f"  rot {i*60:3d}deg: {a_rot} ('{a_rot:07b}') <-> {b_rot} ('{b_rot:07b}')")
        a_rot = rotate60_msb(a_rot)
        b_rot = rotate60_msb(b_rot)

    errors = []
    for src, dst in rule.items():
        if bin(src).count("1") != bin(dst).count("1"):
            errors.append(f"popcount mismatch: {src}->{dst}")
        if rule.get(dst) != src:
            errors.append(f"not involution: {src}->{dst}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        non_id = sum(1 for k, v in rule.items() if k != v)
        print(f"Rule verified: bit-conserving involution, {non_id} non-identity mappings")
    return rule


# --- Simulation ---

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


def detect_period(shapes: list, start: int = 5, max_period: int = 50) -> int:
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

    kernel = find_contiguous_kernel()
    if kernel is None:
        print("ERROR: could not find contiguous kernel")
        sys.exit(1)
    A2_lsb, B2_lsb = kernel
    print(f"Contiguous kernel: A={A2_lsb} ('{A2_lsb:07b}'), B={B2_lsb} ('{B2_lsb:07b}')")

    rule = generate_rule(A2_lsb, B2_lsb)
    B2_msb = lsb_to_msb(B2_lsb)

    # Initial condition: 3-cell seed encoding B's neighborhood (E+SE) plus E-of-E.
    # B_MSB=48='0110000': b1(E)=1, b2(SE)=1 — center (50,50) sees state B.
    # Third cell at E-of-E breaks the symmetry that causes immediate fixed-point collapse.
    cq, cr = N // 2, N // 2
    grid = np.zeros((N, N), dtype=np.int8)
    grid[(cq + 1) % N, (cr + 0) % N] = 1   # b1 = E
    grid[(cq + 1) % N, (cr - 1) % N] = 1   # b2 = SE
    grid[(cq + 2) % N, (cr + 0) % N] = 1   # E of b1 (prevents immediate fixed-point)

    # Verify center neighborhood
    state_center = get_neighborhood(grid, cq, cr)
    print(f"Initial seed: {find_ones(grid)}")
    print(f"Center neighborhood: {state_center} ('{state_center:07b}') — expected B2_MSB={B2_msb} ('{B2_msb:07b}')")

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
        if t < 8 or t % 10 == 9:
            print(f"  t={t+1:3d}  bits={cnt}  n_cells={len(pos)}")

    initial_count = bit_counts[0]
    # Allow for a transient settling period: check stability from step 5 onwards
    settle_step = min(5, STEPS // 10)
    settled_counts = bit_counts[settle_step:]
    settled_count = settled_counts[0] if settled_counts else initial_count
    is_bit_conserving = all(c == settled_count for c in settled_counts)

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

    if not is_bit_conserving and bit_counts[-1] < bit_counts[0]:
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

    result = {
        "kernel_A": int(A2_lsb),
        "kernel_B": int(B2_lsb),
        "is_bit_conserving": bool(is_bit_conserving),
        "behavior_class": behavior_class,
        "net_displacement": float(net_displacement),
        "oscillation_period": int(oscillation_period),
        "final_bit_count": int(bit_counts[-1]),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    success = behavior_class in ("GLIDER", "STATIONARY_OSCILLATOR") or oscillation_period > 1
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
