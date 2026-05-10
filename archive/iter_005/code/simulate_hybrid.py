#!/usr/bin/env python3
"""
Hybrid 2-bit/cell CA: produces a v=c/2 glider via alternating OSCILLATE/MOVE steps.

States: 0='00' (empty), 1='01' (state A), 2='10' (state B)

Step 1 OSCILLATE (even t): state A ('01') with empty neighbors -> state B ('10')
Step 2 MOVE    (odd  t): state B ('10') shifts right one cell as state A ('01')

Effective velocity = 1 cell per 2 steps = c/2.
"""
import os
import sys
from pathlib import Path

import yaml

LATTICE_SIZE = 100
INITIAL_POS = 20
STEPS = 100

RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULT_YAML = Path(__file__).parent.parent / "result.yaml"
ITER013_RESULTS = Path(__file__).parent.parent.parent / "iter_013" / "results"


def apply_oscillate(lattice):
    """OSCILLATE: '01' -> '10' when neighbors are both '00'."""
    new = lattice.copy()
    n = len(lattice)
    for i in range(n):
        left = lattice[(i - 1) % n]
        center = lattice[i]
        right = lattice[(i + 1) % n]
        if center == 1 and left == 0 and right == 0:
            new[i] = 2
    return new


def apply_move(lattice):
    """MOVE: '10' at i -> '00' at i, '01' at i+1 (if i+1 is empty)."""
    new = lattice.copy()
    n = len(lattice)
    for i in range(n):
        right_idx = (i + 1) % n
        if lattice[i] == 2 and lattice[right_idx] == 0:
            new[i] = 0
            new[right_idx] = 1
    return new


def center_of_mass(lattice):
    positions = [i for i, v in enumerate(lattice) if v > 0]
    if not positions:
        return None
    return sum(positions) / len(positions)


def main():
    lattice = [0] * LATTICE_SIZE
    lattice[INITIAL_POS] = 1  # state A

    history = [list(lattice)]
    positions = [center_of_mass(lattice)]

    for t in range(STEPS):
        if t % 2 == 0:
            lattice = apply_oscillate(lattice)
        else:
            lattice = apply_move(lattice)
        history.append(list(lattice))
        positions.append(center_of_mass(lattice))

    # Effective velocity: displacement over last 50 steps
    last_pos = [p for p in positions[-51:] if p is not None]
    if len(last_pos) >= 2:
        velocity = (last_pos[-1] - last_pos[0]) / (len(last_pos) - 1)
    else:
        velocity = 0.0

    # Stability: particle must still exist
    is_stable = all(p is not None for p in positions[-10:])
    # No growth: single-cell particle throughout
    final_count = sum(1 for v in lattice if v > 0)
    if final_count != 1:
        is_stable = False

    final_pos = positions[-1]

    if is_stable and 0.49 <= velocity <= 0.51:
        behavior_class = "V_HALF_GLIDER"
    elif is_stable and abs(velocity) < 0.01:
        behavior_class = "STATIONARY"
    elif is_stable and abs(velocity) > 0.99:
        behavior_class = "V_C_GLIDER"
    elif not is_stable:
        behavior_class = "DECAY"
    else:
        behavior_class = "CHAOTIC"

    result = {
        "behavior_class": behavior_class,
        "effective_velocity": round(float(velocity), 6),
        "is_stable": bool(is_stable),
        "final_position": float(final_pos) if final_pos is not None else None,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ITER013_RESULTS.mkdir(parents=True, exist_ok=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False)

    iter013_yaml = ITER013_RESULTS / "result.yaml"
    with open(iter013_yaml, "w") as f:
        yaml.dump(result, f, default_flow_style=False)

    print(f"behavior_class:     {behavior_class}")
    print(f"effective_velocity: {velocity:.6f}")
    print(f"is_stable:          {is_stable}")
    print(f"final_position:     {final_pos}")
    print()
    print(f"Position trace (every 10 steps):")
    for i, p in enumerate(positions[::10]):
        print(f"  t={i*10:4d}  pos={p}")

    return result


if __name__ == "__main__":
    main()
