#!/usr/bin/env python3
"""
Trajectory analysis of iter_220 champion rule.
Simulate for 500 steps with the 3-bit L-tromino seed and report:
  - Classification (MOVING, OSCILLATING, ANNIHILATING, etc.)
  - Average velocity v
  - Active cell count min, max, final
  - Period of shape oscillation
"""

from __future__ import annotations

import json
import math
import numpy as np
import sys

sys.path.insert(0, "src")
from evolution import rule_dict_to_lut, step_grid, center_of_mass

# ---- Configuration ----
JSON_PATH = "archive/iter_220/results/champion_vc_rule_consistency.json"
GRID_SIZE = 128
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]
STEPS = 500


def load_json():
    with open(JSON_PATH) as f:
        data = json.load(f)
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    return data, rule_dict


def normalize_pattern(grid):
    """Shift pattern to (0,0) origin for pattern matching."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return ()
    offset_r, offset_c = int(np.min(rows)), int(np.min(cols))
    shifted = []
    for r, c in zip(rows, cols):
        shifted.append((r - offset_r, c - offset_c))
    return tuple(sorted(shifted))


def find_period(patterns, max_period=200):
    """Find the smallest period p such that patterns repeat every p steps."""
    n = len(patterns)
    search_start = max(n // 4, 5)  # skip first quarter for transients

    for period in range(1, min(max_period, n // 3)):
        matches = 0
        total = 0
        for i in range(search_start + period, n):
            total += 1
            if patterns[i] == patterns[i - period]:
                matches += 1
        if total > 0 and matches / total >= 0.98:
            return period

    return None


def classify_dynamics(patterns, bit_counts, coms, steps):
    """Classify the dynamics of the object."""
    final_bits = bit_counts[-1]

    # Check annihilation
    if final_bits == 0:
        # Check if it was ever alive after seed
        alive_after_seed = any(b > 0 for b in bit_counts[1:])
        if alive_after_seed:
            return "TRANSIENT_DECAY"
        return "ANNIHILATING"

    # Calculate COM trajectory
    n = len(coms)
    if n < 2:
        return "UNKNOWN"

    total_dx = coms[-1][0] - coms[0][0]
    total_dy = coms[-1][1] - coms[0][1]
    total_disp = math.sqrt(total_dx ** 2 + total_dy ** 2)

    # Check if it's periodic (oscillating) or moving
    unique_patterns = set(patterns)
    n_unique = len(unique_patterns)

    # For oscillating objects, bit count should be stable
    stable_bits = len(set(bit_counts)) <= 2

    if total_disp < 0.05:
        return "OSCILLATING"
    
    # Check sustained motion: is COM moving consistently?
    mid = steps // 2
    half_disp = math.sqrt((coms[mid][0] - coms[0][0]) ** 2 + (coms[mid][1] - coms[0][1]) ** 2)
    second_half_disp = math.sqrt((coms[-1][0] - coms[mid][0]) ** 2 + (coms[-1][1] - coms[mid][1]) ** 2)

    if second_half_disp > 1.0 and second_half_disp > half_disp * 0.3:
        return "MOVING"
    elif total_disp > 0.05:
        return "DRIFTING"
    else:
        return "OSCILLATING"


def main():
    print("=" * 70)
    print("TRAJECTORY ANALYSIS - iter_220 champion rule (500 steps)")
    print("=" * 70)

    data, rule_dict = load_json()
    print(f"\nRule dict entries : {len(rule_dict)}")
    print(f"Rule dict         : {dict(rule_dict)}")
    print(f"Seed cells        : {SEED_CELLS}")
    print(f"Grid size         : {GRID_SIZE}x{GRID_SIZE} (toroidal)")
    print(f"Simulation steps  : {STEPS}")

    # ---- Simulate ----
    lut = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1

    history = []
    patterns = []
    bit_counts = []
    coms = []

    # Step 0
    rows, cols = np.where(grid > 0)
    com = (float(np.mean(rows)) if len(rows) > 0 else 0.0,
           float(np.mean(cols)) if len(cols) > 0 else 0.0)
    bits = int(grid.sum())
    pat = normalize_pattern(grid)

    history.append({"step": 0, "com": com, "bit_count": bits})
    patterns.append(pat)
    bit_counts.append(bits)
    coms.append(com)

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        rows, cols = np.where(grid > 0)
        com = (float(np.mean(rows)) if len(rows) > 0 else 0.0,
               float(np.mean(cols)) if len(cols) > 0 else 0.0)
        bits = int(grid.sum())
        pat = normalize_pattern(grid)

        history.append({"step": t, "com": com, "bit_count": bits})
        patterns.append(pat)
        bit_counts.append(bits)
        coms.append(com)

    # ---- Compute metrics ----
    initial_bits = bit_counts[0]
    min_bits = min(bit_counts)
    max_bits = max(bit_counts)
    final_bits = bit_counts[-1]

    initial_com = coms[0]
    final_com = coms[-1]

    # Total displacement
    dx_total = final_com[0] - initial_com[0]
    dy_total = final_com[1] - initial_com[1]
    total_displacement = math.sqrt(dx_total ** 2 + dy_total ** 2)
    avg_velocity = total_displacement / STEPS

    # Classification
    classification = classify_dynamics(patterns, bit_counts, coms, STEPS)

    # Find period
    period = find_period(patterns, max_period=STEPS // 4)

    # ---- Print results ----
    print()
    print("-" * 70)
    print("RESULTS")
    print("-" * 70)
    print()
    print(f"  Classification          : {classification}")
    print(f"  Average velocity v      : {avg_velocity:.6f} cells/step")
    print(f"  Total displacement      : {total_displacement:.6f} cells")
    print(f"  Net COM drift           : dx={dx_total:+.4f}, dy={dy_total:+.4f}")
    print()
    print("  Active cell count (bits):")
    print(f"    Min                   : {min_bits}")
    print(f"    Max                   : {max_bits}")
    print(f"    Final                 : {final_bits}")
    print(f"    Initial (seed)        : {initial_bits}")
    print()
    print(f"  Shape oscillation period: ", end="")
    if period is not None:
        print(f"{period} steps (CONFIRMED)")
    else:
        print("NOT FOUND (non-periodic or period > 100)")
    print(f"  Unique shapes observed  : {len(set(patterns))}")
    print()

    # Period verification
    if period is not None:
        print(f"  Period verification (showing first {min(period + 5, len(patterns))} patterns after transient):")
        sample_start = STEPS // 4
        print(f"  {'Step':>6}  {'Bits':>6}  {'COM':<30}  {'Pattern':<50}")
        for t in range(sample_start, min(sample_start + period + 3, STEPS + 1)):
            p = patterns[t]
            p_str = str(p)[:48] if p else "(empty)"
            print(f"  {t:6d}  {bit_counts[t]:6d}  ({coms[t][0]:.2f}, {coms[t][1]:.2f})  {p_str}")
        # Period check
        matches = 0
        checks = 0
        for t in range(sample_start + period, STEPS + 1):
            checks += 1
            if patterns[t] == patterns[t - period]:
                matches += 1
        print()
        print(f"  Period match: {matches}/{checks} pairs ({100*matches/checks:.1f}%)" if checks > 0 else "")
    print()

    # Bit count trace (sampled)
    print("  Bit count timeline (sampled):")
    print(f"  {'Step':>6}  {'Bit Count':>10}  {'COM':<30}  {'Pat Size':>8}")
    step_inc = max(1, STEPS // 25)
    for t in range(0, STEPS + 1, step_inc):
        p_size = len(patterns[t]) if patterns[t] else 0
        print(f"  {t:6d}  {bit_counts[t]:10d}  ({coms[t][0]:.2f}, {coms[t][1]:.2f})  {p_size:8d}")
    print()

    # Final grid
    rows, cols = np.where(grid > 0)
    if len(rows) > 0:
        print(f"  Final grid state:")
        print(f"    Active cells: [{int(np.min(rows))}, {int(np.max(rows))}] x [{int(np.min(cols))}, {int(np.max(cols))}]")
        print(f"    COM = ({final_com[0]:.4f}, {final_com[1]:.4f})")
    else:
        print("  Final grid: ALL CELLS DEAD")
    print()

    # ---- Summary ----
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    if classification == "MOVING":
        print("  [SUCCESS] SUB-LIGHT GLIDER DETECTED")
        print(f"    Velocity: v = {avg_velocity:.6f} cells/step")
        print("  The new search DID find a sub-light glider!")
    elif classification == "OSCILLATING":
        if period is not None:
            print(f"  [NO] This is a PERIODIC OSCILLATOR (period={period})")
        else:
            print("  [NO] This is a NON-PERIODIC OSCILLATOR")
        print("  NOT a glider - the object does not translate.")
        print("  The new search found the same type of oscillator as before.")
    elif classification == "ANNIHILATING":
        print("  [NO] The seed was completely destroyed.")
    elif classification == "DRIFTING":
        print("  [MAYBE] Small drift observed - possible slow drifter")
        print("  Not a coherent glider.")
    elif classification == "TRANSIENT_DECAY":
        print("  [NO] Object lived briefly then decayed to stable form.")
    print()
    print(f"  Fitness score from JSON : {data['fitness']}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
