#!/usr/bin/env python3
"""
iter_019: conditional-swap
Rule: if neighbor b1 == 1, center takes neighbor b2's value.
Neighborhood: b0 b1 b2 b3 b4 b5 b6 (center b0, neighbors clockwise b1..b6)
b1 = East (1,0), b2 = SE (1,-1).
When b1=1: new center = b2; when b1=0: identity.
This is its own inverse at the neighborhood level.
"""

import sys
import yaml
import numpy as np
from pathlib import Path

N = 50
STEPS = 100

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_019" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_019" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),   # b1: E
    ( 1, -1),   # b2: SE
    ( 0, -1),   # b3: SW
    (-1,  0),   # b4: W
    (-1,  1),   # b5: NW
    ( 0,  1),   # b6: NE
]


def step(grid: np.ndarray) -> np.ndarray:
    """new[q,r] = old[q+1,r-1] if old[q+1,r]==1 else old[q,r]"""
    b1 = np.roll(grid, -1, axis=0)   # b1[q,r] = grid[q+1, r]
    b2 = np.roll(b1, 1, axis=1)      # b2[q,r] = grid[q+1, r-1]
    return np.where(b1 == 1, b2, grid)


def step_reference(grid: np.ndarray) -> np.ndarray:
    """Cell-by-cell reference for validation."""
    n = grid.shape[0]
    new = np.empty_like(grid)
    for q in range(n):
        for r in range(n):
            b1 = grid[(q + 1) % n, r]
            b2 = grid[(q + 1) % n, (r - 1) % n]
            new[q, r] = b2 if b1 == 1 else grid[q, r]
    return new


def find_ones(grid: np.ndarray) -> list[tuple[int, int]]:
    qs, rs = np.where(grid == 1)
    return sorted(zip(qs.tolist(), rs.tolist()))


def centroid(positions: list[tuple[int, int]]) -> tuple[float, float]:
    if not positions:
        return (0.0, 0.0)
    return (sum(q for q, r in positions) / len(positions),
            sum(r for q, r in positions) / len(positions))


def relative_shape(positions: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not positions:
        return []
    q0, r0 = positions[0]
    return sorted((q - q0, r - r0) for q, r in positions)


def classify_single(positions_history: list, bit_counts: list) -> tuple[str, tuple | None]:
    """Classify single-bit simulation: STATIONARY, GLIDER, OSCILLATOR, or DECAY."""
    if any(c == 0 for c in bit_counts):
        return "DECAY", None

    if any(c != 1 for c in bit_counts):
        return "DECAY", None

    initial_pos = positions_history[0][0]

    if all(len(ph) == 1 and ph[0] == initial_pos for ph in positions_history):
        return "STATIONARY", None

    # Check linear motion
    q0, r0 = initial_pos
    q1, r1 = positions_history[1][0]
    dq = int((q1 - q0 + N // 2) % N - N // 2)
    dr = int((r1 - r0 + N // 2) % N - N // 2)

    if dq != 0 or dr != 0:
        is_linear = all(
            len(positions_history[t]) == 1
            and positions_history[t][0] == ((q0 + t * dq) % N, (r0 + t * dr) % N)
            for t in range(1, len(positions_history))
        )
        if is_linear:
            return "GLIDER", (dq, dr)

    return "OSCILLATOR", None


def classify_two(positions_history: list, bit_counts: list) -> tuple[str, tuple | None]:
    """Classify two-bit simulation: GLIDER, STATIONARY_OSCILLATOR, DECAY, or CHAOTIC."""
    initial_count = bit_counts[0]
    final_count = bit_counts[-1]

    if max(bit_counts) > 5 * initial_count:
        return "CHAOTIC", None

    if any(c != initial_count for c in bit_counts):
        return "DECAY", None

    # Bit-conserving: check for motion
    c0 = centroid(positions_history[0])
    c_final = centroid(positions_history[-1])
    net_dq = c_final[0] - c0[0]
    net_dr = c_final[1] - c0[1]

    # Also check if shape is constant (required for glider)
    shape0 = relative_shape(positions_history[0])
    shapes_constant = all(relative_shape(ph) == shape0 for ph in positions_history)

    # Check for consistent per-step motion
    step_dqs = []
    step_drs = []
    for t in range(1, min(len(positions_history), 20)):
        ct = centroid(positions_history[t])
        ct_prev = centroid(positions_history[t - 1])
        step_dqs.append(ct[0] - ct_prev[0])
        step_drs.append(ct[1] - ct_prev[1])

    if step_dqs:
        avg_dq = sum(step_dqs) / len(step_dqs)
        avg_dr = sum(step_drs) / len(step_drs)
        velocity_consistent = all(
            abs(d - avg_dq) < 0.6 for d in step_dqs
        ) and all(
            abs(d - avg_dr) < 0.6 for d in step_drs
        )
        is_moving = abs(avg_dq) > 0.1 or abs(avg_dr) > 0.1
    else:
        velocity_consistent = False
        is_moving = False

    if is_moving and velocity_consistent:
        vel_q = round(avg_dq * 2) / 2
        vel_r = round(avg_dr * 2) / 2
        return "GLIDER", (vel_q, vel_r)

    # Stationary — check for oscillation
    return "STATIONARY_OSCILLATOR", None


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
        grid = step(grid)
        count = int(grid.sum())
        positions = find_ones(grid)
        bit_counts.append(count)
        positions_history.append(positions)

        if verbose and (t < 6 or t % 20 == 19):
            print(f"  t={t+1:4d}  {count:4d}  {positions[:4]}")

    if verbose:
        print(f"Final count: {bit_counts[-1]}")

    return {
        "bit_counts": bit_counts,
        "positions_history": positions_history,
        "initial_count": initial_count,
        "final_count": int(bit_counts[-1]),
    }


def main() -> int:
    # Validate vectorized step
    test = np.zeros((7, 7), dtype=np.int8)
    test[3, 3] = 1
    assert np.array_equal(step(test), step_reference(test)), \
        "Single-bit validation failed!"
    test2 = np.zeros((7, 7), dtype=np.int8)
    test2[3, 3] = 1
    test2[4, 3] = 1  # East neighbor
    assert np.array_equal(step(test2), step_reference(test2)), \
        "Two-bit validation failed!"
    print("Validation passed.")

    cq, cr = N // 2, N // 2
    dq1, dr1 = HEX_DIRS[0]  # b1 = East = (1, 0)

    # Simulation 1: single bit at center
    grid1 = np.zeros((N, N), dtype=np.int8)
    grid1[cq, cr] = 1
    results1 = run_simulation(grid1, "Simulation 1 (Single Bit)")

    # Simulation 2: two adjacent bits — center + b1 (East neighbor)
    grid2 = np.zeros((N, N), dtype=np.int8)
    grid2[cq, cr] = 1
    grid2[(cq + dq1) % N, (cr + dr1) % N] = 1
    results2 = run_simulation(grid2, "Simulation 2 (Two Bits: center + East)")

    # Classify
    single_behavior, single_velocity = classify_single(
        results1["positions_history"], results1["bit_counts"]
    )
    two_behavior, two_velocity = classify_two(
        results2["positions_history"], results2["bit_counts"]
    )

    is_nontrivial = (single_behavior == "STATIONARY" and two_behavior == "GLIDER")

    glider_velocity_hex = None
    if two_behavior == "GLIDER" and two_velocity:
        glider_velocity_hex = list(two_velocity)

    print(f"\n=== Classification ===")
    print(f"single_bit_behavior:    {single_behavior}")
    print(f"two_bit_behavior:       {two_behavior}")
    print(f"is_nontrivial_motion:   {is_nontrivial}")
    print(f"final_bit_count_single: {results1['final_count']}")
    print(f"final_bit_count_two:    {results2['final_count']}")
    print(f"glider_velocity_hex:    {glider_velocity_hex}")

    # Show first 10 two-bit positions for inspection
    print("\nTwo-bit positions history (first 10 steps):")
    for t in range(min(11, len(results2["positions_history"]))):
        ph = results2["positions_history"][t]
        print(f"  t={t:3d}: count={results2['bit_counts'][t]}  {ph}")

    result = {
        "single_bit_behavior": single_behavior,
        "two_bit_behavior": two_behavior,
        "is_nontrivial_motion": bool(is_nontrivial),
        "final_bit_count_single": int(results1["final_count"]),
        "final_bit_count_two": int(results2["final_count"]),
        "glider_velocity_hex": glider_velocity_hex,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)

    print(f"\nResult written to: {RESULT_YAML}")

    return 0 if is_nontrivial else 1


if __name__ == "__main__":
    sys.exit(main())
