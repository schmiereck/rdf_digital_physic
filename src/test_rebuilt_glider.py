#!/usr/bin/env python3
"""
Test: Load original rule 179 champion rule, rebuild via 14 generator pairs,
simulate both for 200 steps from the L-tromino seed, and verify 100 % identity
of centre-of-mass and active cells at every step.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

# Ensure imports from src/ work
sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule, _rotate_c2, rule_dict_to_lut, step_grid, center_of_mass, make_ltromino_grid


# ── Helper ──────────────────────────────────────────────────────────────────────

def extract_generator_pairs(rule_dict: dict) -> list:
    """Extract the minimal set of generator pairs from a C2-symmetric rule_dict."""
    remaining = {(int(k), v) for k, v in rule_dict.items()}
    pairs = []
    while remaining:
        a, b = next(iter(remaining))
        rot_a = _rotate_c2(a)
        rot_b = _rotate_c2(b)
        orbit_entries = [(a, b), (b, a), (rot_a, rot_b), (rot_b, rot_a)]
        for entry in orbit_entries:
            remaining.discard(entry)
        pairs.append((a, b))
    return pairs


def simulate(rule_dict: dict, steps: int = 200):
    """Return list of (center_of_mass, frozenset of active cells) for each step."""
    lut = rule_dict_to_lut(rule_dict)
    grid = make_ltromino_grid()
    history = []
    for t in range(steps + 1):
        xs, ys = np.where(grid > 0)
        if len(xs) == 0:
            com = (0.0, 0.0)
        else:
            com = (float(np.mean(xs)), float(np.mean(ys)))
        active = frozenset(zip(xs.tolist(), ys.tolist()))
        history.append((com, active))
        grid = step_grid(grid, lut)
    return history


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    PROJECT_ROOT = Path(__file__).parent.parent
    champion_path = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"

    # 1. Load original champion rule
    print("=" * 60)
    print("Step 1: Load original champion rule (iter 179)")
    print("=" * 60)
    with open(champion_path, "r") as f:
        champion = json.load(f)
    original_rule_dict = champion["rule_dict"]
    original_int = {int(k): int(v) for k, v in original_rule_dict.items()}
    print(f"  Loaded {len(original_rule_dict)} rule entries")
    print(f"  rule_id: {champion.get('rule_id', 'N/A')}")
    print(f"  fitness: {champion.get('fitness', 'N/A')}")

    # 2. Extract 14 generator pairs
    print("\n" + "=" * 60)
    print("Step 2: Extract generator pairs")
    print("=" * 60)
    pairs = extract_generator_pairs(original_rule_dict)
    print(f"  Extracted {len(pairs)} generator pairs:")
    for i, (a, b) in enumerate(pairs):
        print(f"    pair {i+1:2d}: ({a:3d} -> {b:3d})")

    # 3. Rebuild the rule
    print("\n" + "=" * 60)
    print("Step 3: Rebuild rule from generator pairs")
    print("=" * 60)
    rebuilt_rule_dict = _try_build_c2_rule(pairs)
    if rebuilt_rule_dict is None:
        print("  ERROR: Rebuild returned None!")
        return
    rebuilt_int = {int(k): int(v) for k, v in rebuilt_rule_dict.items()}
    print(f"  Rebuilt {len(rebuilt_rule_dict)} rule entries")

    # Check rebuilt rule dict identity
    keys_match = set(original_int.keys()) == set(rebuilt_int.keys())
    values_match = all(original_int[k] == rebuilt_int[k] for k in original_int) if keys_match else False
    dict_identical = keys_match and values_match
    print(f"  Rule dict identical: {dict_identical}")

    # 4. Simulate both for 200 steps
    print("\n" + "=" * 60)
    print("Step 4: Simulate both rules for 200 steps from L-tromino seed")
    print("=" * 60)
    steps = 200

    hist_orig = simulate(original_int, steps)
    hist_rebuilt = simulate(rebuilt_int, steps)

    print(f"  Simulated {steps} steps for both rules")

    # 5. Compare at every step
    print("\n" + "=" * 60)
    print("Step 5: Compare centre of mass and active cells at every step")
    print("=" * 60)

    all_match = True
    com_mismatch_steps = []
    active_mismatch_steps = []

    for t in range(steps + 1):
        com_o, active_o = hist_orig[t]
        com_r, active_r = hist_rebuilt[t]

        com_ok = (abs(com_o[0] - com_r[0]) < 1e-12 and abs(com_o[1] - com_r[1]) < 1e-12)
        active_ok = (active_o == active_r)

        if not com_ok:
            all_match = False
            com_mismatch_steps.append(t)
        if not active_ok:
            all_match = False
            active_mismatch_steps.append(t)

    # Print summary
    print(f"  Total steps checked: {steps + 1}  (t=0..{steps})")
    print(f"  Centre-of-mass mismatches: {len(com_mismatch_steps)} "
          f"{'at steps: ' + str(com_mismatch_steps) if com_mismatch_steps else ''}")
    print(f"  Active-cell mismatches:    {len(active_mismatch_steps)} "
          f"{'at steps: ' + str(active_mismatch_steps) if active_mismatch_steps else ''}")

    # Detailed comparison for first few steps
    print("\n  Step-by-step summary (first 10 and last 5):")
    for t in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + list(range(max(0, steps - 4), steps + 1)):
        if t > steps:
            break
        com_o, active_o = hist_orig[t]
        com_r, active_r = hist_rebuilt[t]
        com_same = (abs(com_o[0] - com_r[0]) < 1e-12 and abs(com_o[1] - com_r[1]) < 1e-12)
        active_same = (active_o == active_r)
        status = "OK" if (com_same and active_same) else "MISMATCH"
        print(f"    t={t:3d}: com_o=({com_o[0]:8.4f}, {com_o[1]:8.4f}) "
              f"com_r=({com_r[0]:8.4f}, {com_r[1]:8.4f}) "
              f"active_o={len(active_o)} active_r={len(active_r)}  [{status}]")

    # Final verdict
    print("\n" + "=" * 60)
    if all_match:
        print("RESULT: PASS — 100 % identical centre of mass and active cells at every step.")
    else:
        print("RESULT: FAIL — differences detected.")
        if com_mismatch_steps:
            print(f"  Centre-of-mass mismatches at steps: {com_mismatch_steps}")
        if active_mismatch_steps:
            print(f"  Active-cell mismatches at steps: {active_mismatch_steps}")
    print("=" * 60)

    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
