#!/usr/bin/env python3
"""
characterize_glider_200.py
Characterize the champion v<c rule from iter_200 results.
"""

import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from evolution import rule_dict_to_lut, step_grid

GRID_SIZE = 256
STEPS = 2000


def center_of_mass(grid):
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0)
    return (float(np.mean(rows)), float(np.mean(cols)))


def unwrap_com(raw_com, prev_unwrapped, grid_size):
    """Unwrap CoM using shortest-path correction relative to previous unwrapped position."""
    r, c = raw_com
    pr, pc = prev_unwrapped
    # Difference in wrapped space
    dr = r - (pr % grid_size)
    dc = c - (pc % grid_size)
    # Correct for wraparound
    if dr > grid_size / 2:
        dr -= grid_size
    elif dr < -grid_size / 2:
        dr += grid_size
    if dc > grid_size / 2:
        dc -= grid_size
    elif dc < -grid_size / 2:
        dc += grid_size
    return (pr + dr, pc + dc)


def get_shape(grid):
    """Return shape as frozenset of (row, col) offsets from min corner."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return frozenset()
    min_r = int(rows.min())
    min_c = int(cols.min())
    return frozenset((int(r) - min_r, int(c) - min_c) for r, c in zip(rows, cols))


def detect_period(shapes, start=1000, max_period=200, confirm_cycles=5):
    """Find smallest period p such that shapes[start+k*p] == shapes[start] for confirm_cycles."""
    ref = shapes[start]
    for p in range(1, max_period + 1):
        ok = True
        for k in range(1, confirm_cycles + 1):
            idx = start + k * p
            if idx >= len(shapes):
                break
            if shapes[idx] != ref:
                ok = False
                break
        if ok:
            return p
    return -1


def main():
    # Load rule
    results_dir = Path(__file__).parent.parent / "archive" / "iter_200" / "results"
    rule_path = results_dir / "champion_vc_rule.json"
    print(f"Loading rule from: {rule_path}")
    with open(rule_path) as f:
        rule_data = json.load(f)

    rule_dict = rule_data["rule_dict"]
    seed_particle = rule_data.get("seed_particle", [[0, 0], [0, 1], [1, 1]])
    print(f"Rule has {len(rule_dict)} explicit mappings")
    print(f"Seed particle: {seed_particle}")

    # Build initial grid - 3-bit L-tromino centered on the grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    center = GRID_SIZE // 2
    for dr, dc in seed_particle:
        grid[(center + dr) % GRID_SIZE, (center + dc) % GRID_SIZE] = 1

    lut = rule_dict_to_lut(rule_dict)
    initial_bits = int(grid.sum())
    print(f"Initial bits: {initial_bits}")

    # Run simulation, tracking CoM and shapes
    raw_com0 = center_of_mass(grid)
    unwrapped_r = [raw_com0[0]]
    unwrapped_c = [raw_com0[1]]
    prev_unwrapped = raw_com0
    bit_counts = [initial_bits]
    shapes = [get_shape(grid)]

    for step in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        bits = int(grid.sum())
        bit_counts.append(bits)

        raw_com = center_of_mass(grid)
        uw = unwrap_com(raw_com, prev_unwrapped, GRID_SIZE)
        unwrapped_r.append(uw[0])
        unwrapped_c.append(uw[1])
        prev_unwrapped = uw

        shapes.append(get_shape(grid))

        if step % 500 == 0:
            print(f"  Step {step:4d}: bits={bits}, "
                  f"com=({uw[0]:.2f}, {uw[1]:.2f})")

    # Velocity: Euclidean displacement from step 1000 to 2000, per step
    dr_total = unwrapped_r[2000] - unwrapped_r[1000]
    dc_total = unwrapped_c[2000] - unwrapped_c[1000]
    displacement = float(np.sqrt(dr_total**2 + dc_total**2))
    velocity_vc = displacement / 1000.0
    print(f"\nDisplacement (steps 1000-2000): dr={dr_total:.3f}, dc={dc_total:.3f}")
    print(f"Euclidean displacement: {displacement:.4f}")
    print(f"Velocity (fraction of c): {velocity_vc:.6f}")

    # Stability: bit count constant across all steps
    is_stable = all(b == initial_bits for b in bit_counts)
    print(f"Stable (constant bit count): {is_stable}")
    if not is_stable:
        changed = [(i, b) for i, b in enumerate(bit_counts) if b != initial_bits]
        print(f"  First change: step={changed[0][0]}, bits={changed[0][1]}")

    # Period detection using shapes from step 1000+
    period = detect_period(shapes, start=1000, max_period=300, confirm_cycles=5)
    print(f"Detected period: {period}")

    # Save JSON output
    output = {
        "velocity_vc": float(velocity_vc),
        "period": int(period),
        "is_stable": bool(is_stable),
    }
    out_json = results_dir / "glider_properties.json"
    with open(out_json, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved: {out_json}")

    # Plot CoM trajectory
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    steps_range = list(range(STEPS + 1))

    ax1.plot(steps_range, unwrapped_r, label='Row CoM', color='blue', linewidth=0.8)
    ax1.plot(steps_range, unwrapped_c, label='Col CoM', color='red', linewidth=0.8)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Center of Mass (unwrapped)')
    ax1.set_title(f'CoM Trajectory  |  velocity={velocity_vc:.4f}c  |  period={period}')
    ax1.legend()
    ax1.grid(True, alpha=0.4)

    ax2.plot(steps_range, bit_counts, label='Bit Count', color='green', linewidth=0.8)
    ax2.axhline(y=initial_bits, color='black', linestyle='--', linewidth=0.8, label=f'Initial ({initial_bits})')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Bit Count')
    ax2.set_title(f'Bit Count vs Time  |  stable={is_stable}')
    ax2.legend()
    ax2.grid(True, alpha=0.4)

    plt.tight_layout()
    out_png = results_dir / "trajectory.png"
    plt.savefig(out_png, dpi=100)
    plt.close()
    print(f"Saved: {out_png}")

    print("\nDone.")
    return output


if __name__ == "__main__":
    main()
