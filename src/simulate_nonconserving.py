#!/usr/bin/env python3
"""
Simulate the non-conserving 2-cycle rule (A=3, B=14) on a 100x100 periodic hex grid.

Grid coordinates: (x, y) where x = q-axis (row), y = r-axis (column).
MSB encoding for neighborhoods: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
Hex directions: E=(+1,0), SE=(+1,-1), SW=(0,-1), W=(-1,0), NW=(-1,+1), NE=(0,+1)

Initial condition: '1' at E=(51,50), SE=(51,49), SW=(50,49) of center cell (50,50).
This makes the center cell a '0' with neighborhood B=14 (MSB=56).
"""

import json
import yaml
import numpy as np
from pathlib import Path

KERNEL_A = 3
KERNEL_B = 14
STEPS = 300
GRID_SIZE = 100

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_066"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULT_DIR / "result.yaml"


def load_rule() -> np.ndarray:
    with open(RULE_PATH) as f:
        raw = json.load(f)
    rule_dict = {int(k): int(v) for k, v in raw.items()}
    return np.array([rule_dict.get(i, i) for i in range(128)], dtype=np.int32)


def compute_neighborhoods(grid: np.ndarray) -> np.ndarray:
    """Compute 7-bit MSB neighborhood index for every cell."""
    g = grid.astype(np.int32)
    E  = np.roll(g, -1, axis=0)
    SE = np.roll(np.roll(g, -1, axis=0), 1, axis=1)
    SW = np.roll(g, 1, axis=1)
    W  = np.roll(g, 1, axis=0)
    NW = np.roll(np.roll(g, 1, axis=0), -1, axis=1)
    NE = np.roll(g, -1, axis=1)
    return (g << 6 | E << 5 | SE << 4 | SW << 3 | W << 2 | NW << 1 | NE)


def step_grid(grid: np.ndarray, rule_arr: np.ndarray) -> np.ndarray:
    nbr = compute_neighborhoods(grid)
    mapped = rule_arr[nbr]
    return ((mapped >> 6) & 1).astype(np.uint8)


def center_of_mass(grid: np.ndarray):
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_arr = load_rule()
    print(f"Loaded rule: {RULE_PATH.name}")

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    # Seed: E, SE, SW neighbors of center cell (50,50) set to 1
    grid[51, 50] = 1   # E  of (50,50)
    grid[51, 49] = 1   # SE of (50,50)
    grid[50, 49] = 1   # SW of (50,50)

    initial_count = int(grid.sum())
    print(f"Initial cells: {sorted(zip(*np.where(grid > 0)))}, bit_count={initial_count}")

    bit_counts = [initial_count]
    history = [grid.copy()]
    state_index = {grid.tobytes(): 0}

    cycle_found = False
    cycle_start = -1
    cycle_period = 0

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, rule_arr)
        bc = int(grid.sum())
        bit_counts.append(bc)

        key = grid.tobytes()
        if not cycle_found:
            if key in state_index:
                cycle_found = True
                cycle_start = state_index[key]
                cycle_period = t - cycle_start
                print(f"Step {t}: cycle detected — period={cycle_period}, start=step {cycle_start}")
            else:
                state_index[key] = t
            history.append(grid.copy())

        if t <= 5 or t % 50 == 0:
            com = center_of_mass(grid)
            print(f"Step {t:3d}: bit_count={bc:4d}, com=({com[0]:.2f},{com[1]:.2f})")

        if bc == 0:
            print(f"Step {t}: DECAY — all cells dead")
            break
        if bc > 500:
            print(f"Step {t}: CHAOTIC_GROWTH — bit_count={bc}")
            break

    final_count = int(grid.sum())
    min_count = min(bit_counts)
    max_count = max(bit_counts)
    is_bit_conserving = bool(min_count == max_count == initial_count)

    net_displacement = [0, 0]
    if cycle_found and cycle_period > 0 and cycle_start + cycle_period < len(history):
        com0 = center_of_mass(history[cycle_start])
        com1 = center_of_mass(history[cycle_start + cycle_period])
        drow = com1[0] - com0[0]
        dcol = com1[1] - com0[1]
        # Unwrap periodic boundary
        if abs(drow) > GRID_SIZE // 2:
            drow -= GRID_SIZE * (1 if drow > 0 else -1)
        if abs(dcol) > GRID_SIZE // 2:
            dcol -= GRID_SIZE * (1 if dcol > 0 else -1)
        net_displacement = [round(drow), round(dcol)]

    if final_count == 0:
        behavior_class = "DECAY"
        object_found = False
        object_period = 0
    elif max_count > initial_count * 10 or max_count > 500:
        behavior_class = "CHAOTIC_GROWTH"
        object_found = False
        object_period = 0
    elif cycle_found:
        object_found = True
        object_period = cycle_period
        if net_displacement != [0, 0]:
            behavior_class = "GLIDER"
        elif cycle_period == 1:
            behavior_class = "STILL_LIFE"
        else:
            behavior_class = "OSCILLATOR"
    else:
        behavior_class = "CHAOTIC_GROWTH"
        object_found = False
        object_period = 0

    print(f"\n=== Summary ===")
    print(f"object_found:             {object_found}")
    print(f"behavior_class:           {behavior_class}")
    print(f"final_bit_count:          {final_count}")
    print(f"is_globally_bit_conserving: {is_bit_conserving}")
    print(f"object_period:            {object_period}")
    print(f"net_displacement:         {net_displacement}")
    print(f"bit_count range:          {min_count}..{max_count}")

    result = {
        "kernel_A": KERNEL_A,
        "kernel_B": KERNEL_B,
        "object_found": bool(object_found),
        "behavior_class": behavior_class,
        "final_bit_count": int(final_count),
        "is_globally_bit_conserving": is_bit_conserving,
        "object_period": int(object_period),
        "net_displacement": net_displacement,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Written: {RESULT_YAML}")

    # Save bit count history
    with open(RESULTS_DIR / "bit_counts.yaml", "w") as f:
        yaml.dump({"bit_counts": bit_counts}, f, default_flow_style=False)


if __name__ == "__main__":
    main()
