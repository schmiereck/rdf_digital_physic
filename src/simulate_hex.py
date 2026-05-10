#!/usr/bin/env python3
"""
iter_021: composite-rule
Composite two-condition swap rule on 2D hex grid.
For each cell c=(q,r):
  Condition 1: if East neighbor b1=(q+1,r)==1, swap c with SE neighbor b2=(q+1,r-1).
  Condition 2: else if SE neighbor b2=(q+1,r-1)==1, swap c with East neighbor b1=(q+1,r).
Sequential in-place; each swap sees the current modified state.
"""

import sys
import yaml
import numpy as np
from pathlib import Path

N = 50
STEPS = 100

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_021" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_021" / "result.yaml"

# Axial-coordinate neighbor directions clockwise (b1..b6)
HEX_DIRS = [
    ( 1,  0),   # b1: E
    ( 1, -1),   # b2: SE
    ( 0, -1),   # b3: SW
    (-1,  0),   # b4: W
    (-1,  1),   # b5: NW
    ( 0,  1),   # b6: NE
]


def step(grid: np.ndarray) -> None:
    """Sequential in-place composite swap.

    For each cell c=(q,r):
      Condition 1: if b1=(q+1,r)==1, swap c with b2=(q+1,r-1).
      Condition 2: else if b2=(q+1,r-1)==1, swap c with b1=(q+1,r).
    """
    n = grid.shape[0]
    for q in range(n):
        for r in range(n):
            b1_q = (q + 1) % n
            b1_r = r
            b2_q = (q + 1) % n
            b2_r = (r - 1) % n
            if grid[b1_q, b1_r] == 1:
                # Condition 1: b1 is 1, swap c with b2
                grid[q, r], grid[b2_q, b2_r] = grid[b2_q, b2_r], grid[q, r]
            elif grid[b2_q, b2_r] == 1:
                # Condition 2: b2 is 1, swap c with b1
                grid[q, r], grid[b1_q, b1_r] = grid[b1_q, b1_r], grid[q, r]


def find_ones(grid: np.ndarray) -> list:
    qs, rs = np.where(grid == 1)
    return sorted(zip(qs.tolist(), rs.tolist()))


def centroid(positions: list) -> tuple:
    if not positions:
        return (0.0, 0.0)
    return (sum(q for q, r in positions) / len(positions),
            sum(r for q, r in positions) / len(positions))


def classify_control(positions_history: list, bit_counts: list) -> str:
    """Returns 'STATIONARY' or 'MOVED'."""
    initial_pos = positions_history[0]
    if all(ph == initial_pos for ph in positions_history):
        return "STATIONARY"
    return "MOVED"


def classify_test(positions_history: list, bit_counts: list) -> str:
    """Returns 'GLIDER', 'OSCILLATOR', 'STATIONARY', or 'CHAOTIC'."""
    initial_count = bit_counts[0]

    if any(c != initial_count for c in bit_counts):
        return "CHAOTIC"

    initial_positions = positions_history[0]
    if all(ph == initial_positions for ph in positions_history):
        return "STATIONARY"

    # Compute per-step centroid displacement over first 20 steps
    step_dqs = []
    step_drs = []
    for t in range(1, min(len(positions_history), 21)):
        ct = centroid(positions_history[t])
        ct_prev = centroid(positions_history[t - 1])
        step_dqs.append(ct[0] - ct_prev[0])
        step_drs.append(ct[1] - ct_prev[1])

    if step_dqs:
        avg_dq = sum(step_dqs) / len(step_dqs)
        avg_dr = sum(step_drs) / len(step_drs)
        is_moving = abs(avg_dq) > 0.1 or abs(avg_dr) > 0.1
        velocity_consistent = (
            all(abs(d - avg_dq) < 0.6 for d in step_dqs) and
            all(abs(d - avg_dr) < 0.6 for d in step_drs)
        )
        if is_moving and velocity_consistent:
            return "GLIDER"

    return "OSCILLATOR"


def compute_glider_velocity(positions_history: list) -> tuple:
    """Compute average dq and dr per step over the full simulation."""
    if len(positions_history) < 2:
        return (0.0, 0.0)
    dqs = []
    drs = []
    for t in range(1, len(positions_history)):
        ct = centroid(positions_history[t])
        ct_prev = centroid(positions_history[t - 1])
        dqs.append(ct[0] - ct_prev[0])
        drs.append(ct[1] - ct_prev[1])
    avg_dq = sum(dqs) / len(dqs)
    avg_dr = sum(drs) / len(drs)
    return (round(avg_dq, 6), round(avg_dr, 6))


def run_simulation(grid_init: np.ndarray, label: str, verbose: bool = True) -> dict:
    grid = grid_init.copy()
    initial_count = int(grid.sum())
    bit_counts = [initial_count]
    positions_history = [find_ones(grid)]

    if verbose:
        print(f"\n=== {label} ===")
        print(f"Initial count: {initial_count}, positions: {positions_history[0][:4]}")
        print(f"{'t':>6}  {'#1s':>4}  positions")

    for t in range(STEPS):
        step(grid)
        count = int(grid.sum())
        positions = find_ones(grid)
        bit_counts.append(count)
        positions_history.append(positions)

        if verbose and (t < 5 or t % 20 == 19):
            print(f"  t={t+1:4d}  {count:4d}  {positions[:4]}")

    if verbose:
        print(f"Final: count={bit_counts[-1]}, positions={positions_history[-1][:4]}")

    return {
        "bit_counts": bit_counts,
        "positions_history": positions_history,
        "initial_count": initial_count,
        "final_count": int(bit_counts[-1]),
    }


def main() -> int:
    # Validate bit conservation
    vgrid = np.zeros((7, 7), dtype=np.int8)
    vgrid[3, 3] = 1
    vgrid[4, 3] = 1
    before = int(vgrid.sum())
    step(vgrid)
    assert int(vgrid.sum()) == before, "Bit conservation failed in validation!"
    print("Validation passed: bit conservation holds after one step.")

    cq, cr = N // 2, N // 2
    dq1, dr1 = HEX_DIRS[0]  # b1 = East = (1, 0)

    # Sim 1 (Control): single bit at center
    grid_control = np.zeros((N, N), dtype=np.int8)
    grid_control[cq, cr] = 1
    results_control = run_simulation(grid_control, "Sim 1 – Control (single bit at center)")

    # Sim 2 (Test): two bits — center + East neighbor (b1)
    grid_test = np.zeros((N, N), dtype=np.int8)
    grid_test[cq, cr] = 1
    grid_test[(cq + dq1) % N, (cr + dr1) % N] = 1
    results_test = run_simulation(grid_test, "Sim 2 – Test (two bits: center + East)")

    # Classify
    control_behavior = classify_control(
        results_control["positions_history"], results_control["bit_counts"]
    )
    test_behavior = classify_test(
        results_test["positions_history"], results_test["bit_counts"]
    )

    is_bit_conserving = (
        results_control["initial_count"] == results_control["final_count"] and
        results_test["initial_count"] == results_test["final_count"]
    )
    is_nontrivial_motion = (
        control_behavior == "STATIONARY" and
        test_behavior == "GLIDER"
    )

    glider_velocity = compute_glider_velocity(results_test["positions_history"])

    final_bit_count_test = results_test["final_count"]

    print(f"\n=== Classification ===")
    print(f"is_bit_conserving:     {is_bit_conserving}")
    print(f"control_behavior:      {control_behavior}")
    print(f"test_behavior:         {test_behavior}")
    print(f"is_nontrivial_motion:  {is_nontrivial_motion}")
    print(f"final_bit_count_test:  {final_bit_count_test}")
    print(f"glider_velocity_hex:   {glider_velocity}")

    print("\nTest positions history (first 8 steps):")
    for t in range(min(9, len(results_test["positions_history"]))):
        print(f"  t={t:3d}: {results_test['positions_history'][t]}")

    result = {
        "is_bit_conserving": bool(is_bit_conserving),
        "control_behavior": control_behavior,
        "test_behavior": test_behavior,
        "is_nontrivial_motion": bool(is_nontrivial_motion),
        "final_bit_count_test": final_bit_count_test,
        "glider_velocity_hex": list(glider_velocity),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)

    print(f"\nResult written to: {RESULT_YAML}")

    return 0 if is_nontrivial_motion else 1


if __name__ == "__main__":
    sys.exit(main())
