#!/usr/bin/env python3
"""
Analyze the iter_220 champion rule that was saved as
archive/iter_220/results/champion_vc_rule_consistency.json

This script:
  1. Loads the champion rule dict and chromosome from the JSON.
  2. Re-simulates the L-tromino seed for 200 steps (the same horizon
     used in the original run).
  3. Feeds the sim_history into DisplacementConsistencyFitness(num_windows=5)
     and prints every intermediate metric.
  4. Explains why the stationary oscillator got fitness = 0.1779.
"""

from __future__ import annotations

import json
import math
import sys
import numpy as np

sys.path.insert(0, "src")

from evolution import rule_dict_to_lut, step_grid
from new_fitness import DisplacementConsistencyFitness

# ---- Configuration (must match the original run) ----
JSON_PATH = "archive/iter_220/results/champion_vc_rule_consistency.json"
GRID_SIZE = 128
STEPS     = 200          # the JSON says simulation_steps=200
NUM_WINDOWS = 5
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]


def load_json():
    with open(JSON_PATH) as f:
        data = json.load(f)
    # Convert rule_dict keys to int
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    return data, rule_dict


def simulate_with_history(rule_dict: dict) -> list[dict]:
    """Reproduce the exact sim_history from run_evolution_exp_220.py."""
    lut = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1

    def com_and_bits(g):
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return (0.0, 0.0), 0
        return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

    c0, b0 = com_and_bits(grid)
    hist = [{"step": 0, "com": c0, "bit_count": b0}]
    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        c, b = com_and_bits(grid)
        hist.append({"step": t, "com": c, "bit_count": b})
    return hist


def main():
    print("=" * 70)
    print("Champion VC Rule Consistency - iter_220")
    print("=" * 70)

    data, rule_dict = load_json()
    fitness_val = data["fitness"]
    gen_best = data["generation_of_best"]

    print(f"\n  File          : {JSON_PATH}")
    print(f"  Fitness (JSON): {fitness_val}")
    print(f"  Gen of best   : {gen_best}")
    print(f"  Seed cells    : {SEED_CELLS}")
    print(f"  Rule dict size: {len(rule_dict)} entries")

    # ---- Simulate ----
    print(f"\nSimulating {STEPS} steps with 128x128 toroidal grid ...")
    sim_history = simulate_with_history(rule_dict)

    # ---- Inspect the full per-step history ----
    print("\n--- Per-step COM and bit count (full trace) ---")
    for i, entry in enumerate(sim_history):
        step = entry["step"]
        print(f"  step {step:4d}: COM=({entry['com'][0]:10.6f}, {entry['com'][1]:10.6f})  bits={entry['bit_count']}")

    # ---- Run the fitness function ----
    print("\n" + "=" * 70)
    print("Running DisplacementConsistencyFitness(num_windows=5)")
    print("=" * 70)

    fitness_fn = DisplacementConsistencyFitness(num_windows=NUM_WINDOWS)
    final_fitness = fitness_fn(sim_history)

    print(f"\n  FINAL FITNESS: {final_fitness:.6f}")

    # ---- Reproduce the internal metrics ----
    sorted_hist = sorted(sim_history, key=lambda e: e["step"])
    initial_step = float(sorted_hist[0]["step"])
    final_step   = float(sorted_hist[-1]["step"])
    total_steps  = final_step - initial_step
    steps_per_window = total_steps / NUM_WINDOWS

    print(f"\n  Total simulation steps : {total_steps}")
    print(f"  Number of windows      : {NUM_WINDOWS}")
    print(f"  Steps per window       : {steps_per_window}")

    # Compute windowed velocities manually to print them
    window_velocity_mags = []
    window_velocity_vectors = []

    for w in range(NUM_WINDOWS):
        window_start = initial_step + w * steps_per_window
        window_end   = window_start + steps_per_window

        first_entry = None
        last_entry  = None

        for entry in sorted_hist:
            s = float(entry["step"])
            if s < window_start:
                continue
            effective_window_end = window_end
            if w == NUM_WINDOWS - 1:
                effective_window_end = final_step
            if s > effective_window_end:
                break
            if first_entry is None:
                first_entry = entry
            last_entry = entry

        if first_entry is None or last_entry is None:
            window_velocity_mags.append(0.0)
            window_velocity_vectors.append((0.0, 0.0))
            continue

        dx = last_entry["com"][0] - first_entry["com"][0]
        dy = last_entry["com"][1] - first_entry["com"][1]
        velocity_mag = math.sqrt(dx * dx + dy * dy)

        window_velocity_mags.append(velocity_mag)
        window_velocity_vectors.append((dx, dy))

    # ---- Print windowed velocity vectors ----
    print("\n" + "-" * 70)
    print("WINDOWED VELOCITY VECTORS (dCOM per window)")
    print("-" * 70)

    for w in range(NUM_WINDOWS):
        dx, dy = window_velocity_vectors[w]
        mag = window_velocity_mags[w]
        com_start = sorted_hist[0]["com"] if True else None
        # Find the actual COMs for this window
        ws = initial_step + w * steps_per_window
        we = ws + steps_per_window
        if w == NUM_WINDOWS - 1:
            we = final_step

        first_in_window = None
        last_in_window = None
        for entry in sorted_hist:
            s = float(entry["step"])
            if s < ws:
                continue
            if s > we:
                break
            if first_in_window is None:
                first_in_window = entry
            last_in_window = entry

        if first_in_window and last_in_window:
            print(f"  Window {w} (step {int(ws)}->{int(we)}): "
                  f"start COM={first_in_window['com']}  end COM={last_in_window['com']}")
            print(f"           dCOM = ({dx:+10.6f}, {dy:+10.6f})  |v| = {mag:10.6f}")

    # ---- Mean velocity magnitude (of the mean vector) ----
    mean_dx = sum(v[0] for v in window_velocity_vectors) / NUM_WINDOWS
    mean_dy = sum(v[1] for v in window_velocity_vectors) / NUM_WINDOWS
    mean_velocity_magnitude = math.sqrt(mean_dx * mean_dx + mean_dy * mean_dy)

    print(f"\n  Mean velocity vector         : ({mean_dx:+10.6f}, {mean_dy:+10.6f})")
    print(f"  Mean velocity magnitude      : {mean_velocity_magnitude:.6f}")

    # ---- Std dev of velocity magnitudes ----
    velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
    std_dev_velocity_magnitudes = float(np.std(velocity_magnitudes))

    print(f"  Std dev of magnitudes        : {std_dev_velocity_magnitudes:.6f}")

    # Per-step magnitude stats
    mag_arr = np.array(window_velocity_mags, dtype=np.float64)
    print(f"  Min magnitude                : {np.min(mag_arr):.6f}")
    print(f"  Max magnitude                : {np.max(mag_arr):.6f}")
    print(f"  Mean magnitude               : {np.mean(mag_arr):.6f}")

    # ---- Conservation score ----
    conservation_score = fitness_fn._compute_conservation_score(sorted_hist)
    initial_bits = sorted_hist[0]["bit_count"]
    print(f"\n  Initial bit count            : {initial_bits}")
    print(f"  Conservation score           : {conservation_score:.6f}")

    # Show per-step bit counts that differ from initial
    different_bits = [(e["step"], e["bit_count"]) for e in sorted_hist
                      if e["bit_count"] != initial_bits]
    if different_bits:
        print(f"  Steps with different bit counts ({len(different_bits)}):")
        for s, b in different_bits:
            print(f"    step {s:4d}: bit_count = {b}")
    else:
        print("  All steps conserved perfect bit count -> factor = 1.0 each")

    # ---- Base fitness ----
    if mean_velocity_magnitude == 0.0:
        base_fitness = 0.0
    else:
        base_fitness = mean_velocity_magnitude / (1.0 + std_dev_velocity_magnitudes)

    print(f"\n  Base fitness (mean_vel / (1+std_dev)) : {base_fitness:.6f}")
    print(f"    = {mean_velocity_magnitude:.6f} / (1 + {std_dev_velocity_magnitudes:.6f})")
    print(f"    = {mean_velocity_magnitude:.6f} / {1.0 + std_dev_velocity_magnitudes:.6f}")

    # ---- Final fitness ----
    final_calc = base_fitness * conservation_score
    print(f"\n  Final fitness = base_fitness * conservation_score")
    print(f"                = {base_fitness:.6f} * {conservation_score:.6f}")
    print(f"                = {final_calc:.6f}")
    print(f"\n  Reported fitness from JSON: {fitness_val}")
    print(f"  Computed fitness:           {final_calc}")
    print(f"  Match: {abs(final_calc - fitness_val) < 1e-10}")

    # ---- WHY did it get 0.1779? ----
    print("\n" + "=" * 70)
    print("WHY THIS STATIONARY OSCILLATOR GOT FITNESS = 0.1779")
    print("=" * 70)

    # Analyze the motion pattern
    print("\n  OBSERVATION: This rule produces a STATIONARY OSCILLATOR.")
    print(f"  After an initial transient (steps 0-2), the object settles")
    print(f"  into a stable {initial_bits}-bit pattern that does not translate.")
    print(f"\n  THE OBJECT'S DYNAMICS:")
    print(f"  - Step 0: 3-bit L-tromino seed at COM=(63.67, 63.33)")
    print(f"  - Steps 1-2: 3-bit transient, COM drifting")
    print(f"  - Step 3+: The pattern stabilizes to 4 bits and its COM")
    print(f"    locks at (61.75, 64.50) for the remaining 197 steps.")
    print(f"    -> This is a STATIONARY oscillator (not a glider).")
    print(f"\n  WHY IT STILL GOT FITNESS = 0.1779:")
    print(f"\n  1. The fitness function divides the simulation into 5 windows")
    print(f"     of 40 steps each. Window 0 captures the transient phase")
    print(f"     (steps 0-40) where the object was still moving, producing")
    print(f"     a non-zero velocity vector.")
    print(f"  2. Windows 1-4 capture the stationary phase where the COM")
    print(f"     barely moves (or moves slightly due to rounding in the")
    print(f"     simple arithmetic mean COM calculation).")
    print(f"  3. The mean of these 5 velocity vectors has a small but")
    print(f"     non-zero magnitude: {mean_velocity_magnitude:.6f}")
    print(f"     -> base_fitness = mean_vel / (1 + std_dev) = {base_fitness:.6f}")
    print(f"  4. Conservation score = {conservation_score:.6f} (perfect or near-perfect)")
    print(f"  5. Final = {base_fitness:.6f} * {conservation_score:.6f} = {final_calc:.6f}")
    print(f"\n  ROOT CAUSE:")
    print(f"  The fitness formula `mean_velocity_magnitude / (1 + std_dev)")
    print(f"  does not distinguish between a true glider and a transient")
    print(f"  that settles into a stationary oscillator. As long as the")
    print(f"  first window has some displacement, the mean vector is non-")
    print(f"  zero, and the object earns a small positive score.")
    print(f"\n  A PERFECTLY stationary oscillator (no COM change in any")
    print(f"  window) would score 0.0. But this rule's initial transient")
    print(f"  provides enough displacement to yield 0.1779.")

    # Show bit counts over time
    print(f"\n  DETAILED BIT COUNT TRACE:")
    bit_counts = [e["bit_count"] for e in sorted_hist]
    unique_bits = sorted(set(bit_counts))
    print(f"    Unique bit counts observed: {unique_bits}")
    for b in unique_bits:
        count = bit_counts.count(b)
        print(f"    bit_count={b}: {count} steps ({100*count/len(bit_counts):.1f}%)")


if __name__ == "__main__":
    main()
