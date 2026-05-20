#!/usr/bin/env python3
"""
analyze_glider_220.py

Analyze the champion rule found in iter_220:
- Run for 1000 steps
- Measure CoM coordinate history, speed, and bit count conservation
- Analyze the period of oscillation (if periodic) and stability
"""

import json
import math
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_rule.json"
GRID_SIZE = 128
STEPS = 1000

def main():
    if not CHAMPION_JSON.exists():
        print(f"Error: {CHAMPION_JSON} does not exist.")
        sys.exit(1)

    with open(CHAMPION_JSON) as f:
        champ = json.load(f)
    
    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)

    # Initialize grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    grid[63, 63] = 1
    grid[64, 63] = 1
    grid[64, 64] = 1

    def get_com_and_bits(g):
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return (0.0, 0.0), 0
        return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

    c0, b0 = get_com_and_bits(grid)
    history = [{"step": 0, "com": c0, "bit_count": b0}]

    print("Step | CoM (row, col) | Bit Count | dx from start | dy from start")
    print("-" * 65)
    print(f"{0:4d} | ({c0[0]:.2f}, {c0[1]:.2f}) | {b0:9d} | {0.0:.2f} | {0.0:.2f}")

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        c, b = get_com_and_bits(grid)
        history.append({"step": t, "com": c, "bit_count": b})
        if t <= 10 or t % 50 == 0 or t == STEPS:
            dx = c[0] - c0[0]
            dy = c[1] - c0[1]
            print(f"{t:4d} | ({c[0]:.2f}, {c[1]:.2f}) | {b:9d} | {dx:.2f} | {dy:.2f}")

    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)

    # Calculate overall metrics
    initial_bits = history[0]["bit_count"]
    final_bits = history[-1]["bit_count"]
    bit_counts = [h["bit_count"] for h in history]
    is_bit_conserving = all(b == initial_bits for b in bit_counts)
    min_bits = min(bit_counts)
    max_bits = max(bit_counts)

    print(f"Initial bits: {initial_bits}")
    print(f"Final bits: {final_bits}")
    print(f"Bit count range: [{min_bits}, {max_bits}]")
    print(f"Perfect bit-conservation over 1000 steps: {is_bit_conserving}")

    # Velocity and speed
    # Average velocity over different intervals
    com_0 = history[0]["com"]
    com_500 = history[500]["com"]
    com_1000 = history[1000]["com"]

    dx_500 = com_500[0] - com_0[0]
    dy_500 = com_500[1] - com_0[1]
    speed_500 = math.sqrt(dx_500**2 + dy_500**2) / 500

    dx_1000 = com_1000[0] - com_0[0]
    dy_1000 = com_1000[1] - com_0[1]
    speed_1000 = math.sqrt(dx_1000**2 + dy_1000**2) / 1000

    print(f"Displacement @ 500 steps: ({dx_500:.4f}, {dy_500:.4f}) -> net speed: {speed_500:.6f} cells/step")
    print(f"Displacement @ 1000 steps: ({dx_1000:.4f}, {dy_1000:.4f}) -> net speed: {speed_1000:.6f} cells/step")

    # Let's detect the periodicity (phase) and exact speed
    # Find any repeat of the relative offset / shape of the glider
    # We can represent the active cells relative to CoM or as an offset
    # Let's see if the configuration of cells (relative to top-left of bounding box) repeats.
    # We'll run a quick simulation to find the period of state repeats.
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    grid[63, 63] = 1
    grid[64, 63] = 1
    grid[64, 64] = 1

    states = []
    def get_relative_state(g):
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return None
        min_r, min_c = np.min(rows), np.min(cols)
        relative_cells = sorted([(int(r - min_r), int(c - min_c)) for r, c in zip(rows, cols)])
        return tuple(relative_cells)

    states.append(get_relative_state(grid))
    
    period = None
    offset = None
    for t in range(1, 200):
        grid = step_grid(grid, lut)
        curr_state = get_relative_state(grid)
        if curr_state is None:
            break
        
        # Check if this state has appeared before
        for prev_t, prev_state in enumerate(states):
            if curr_state == prev_state:
                period = t - prev_t
                offset = prev_t
                break
        if period is not None:
            break
        states.append(curr_state)

    if period is not None:
        print(f"Detected exact periodicity:")
        print(f"  Transient (offset) steps: {offset}")
        print(f"  Period (cycle length): {period}")
        # Let's find displacement per period
        com_start = history[offset]["com"]
        com_end = history[offset + period]["com"]
        p_dx = com_end[0] - com_start[0]
        p_dy = com_end[1] - com_start[1]
        p_dist = math.sqrt(p_dx**2 + p_dy**2)
        print(f"  Displacement per cycle: ({p_dx:.4f}, {p_dy:.4f})")
        print(f"  Distance per cycle: {p_dist:.4f}")
        print(f"  Theoretical velocity: {p_dist / period:.6f} cells/step")
    else:
        print("No exact period detected within 200 steps.")

if __name__ == "__main__":
    main()
