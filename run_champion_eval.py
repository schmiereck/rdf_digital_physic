#!/usr/bin/env python3
"""
Evaluate the champion_vc_rule from iter_221 using DisplacementConsistencyFitness.

Steps:
  1. Load the champion rule JSON.
  2. Simulate the L-tromino seed on a 128x128 grid for 500 steps, recording
     centre-of-mass and bit-count at each step.
  3. Instantiate DisplacementConsistencyFitness(num_windows=5,
     max_bit_threshold=12, max_velocity_threshold=0.9).
  4. Evaluate and print the exact intermediate calculations.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from new_fitness import DisplacementConsistencyFitness
from evolution import rule_dict_to_lut, step_grid, make_ltromino_grid, center_of_mass, GRID_SIZE, LTROMINO_CELLS


def simulate_with_history(rule_dict: dict, steps: int, grid_size: int) -> list[dict]:
    """Run a CA simulation and return the step-by-step history."""
    lut = rule_dict_to_lut(rule_dict)
    grid = make_ltromino_grid(grid_size, LTROMINO_CELLS)

    def com_and_bits(g: np.ndarray) -> tuple:
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return (0.0, 0.0), 0
        return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

    c0, b0 = com_and_bits(grid)
    history = [{"step": 0, "com": c0, "bit_count": b0}]

    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        c, b = com_and_bits(grid)
        history.append({"step": t, "com": c, "bit_count": b})

    return history


def main() -> None:
    # ── 1. Load the champion rule ─────────────────────────────────────────
    champion_path = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_vc_rule.json"
    with open(champion_path) as f:
        champion = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champion["rule_dict"].items()}
    seed_cells = champion["seed_cells"]

    print("=" * 70)
    print("Champion Rule (iter_221) Evaluation")
    print("=" * 70)
    print(f"  rule_dict : {rule_dict}")
    print(f"  seed_cells: {seed_cells}")
    print(f"  reported_fitness: {champion['fitness']}")
    print(f"  fitness_function  : {champion['fitness_function']}")
    print()

    # ── 2. Simulate ───────────────────────────────────────────────────────
    steps = 500
    grid_size = 128

    print(f"Simulating L-tromino seed on a {grid_size}x{grid_size} grid for {steps} steps ...")
    history = simulate_with_history(rule_dict, steps, grid_size)

    print(f"  Recorded {len(history)} history entries (step 0 .. {steps})")
    print(f"  Initial COM : {history[0]['com']}, bit_count: {history[0]['bit_count']}")
    print(f"  Final   COM : {history[-1]['com']}, bit_count: {history[-1]['bit_count']}")
    print()

    # ── 3. Instantiate DisplacementConsistencyFitness ──────────────────────
    fitness_fn = DisplacementConsistencyFitness(
        num_windows=5,
        bits_per_cell=1,
        strict_conservation=False,
        max_bit_threshold=12,
        max_velocity_threshold=0.9,
    )
    print(f"DisplacementConsistencyFitness instance:")
    print(f"  num_windows          : {fitness_fn.num_windows}")
    print(f"  bits_per_cell        : {fitness_fn.bits_per_cell}")
    print(f"  strict_conservation  : {fitness_fn.strict_conservation}")
    print(f"  max_bit_threshold    : {fitness_fn.max_bit_threshold}")
    print(f"  max_velocity_threshold: {fitness_fn.max_velocity_threshold}")
    print()

    # ── 4. Manual intermediate calculations (reproducing the logic) ────────
    sorted_history = sorted(history, key=lambda e: e["step"])
    num_windows = fitness_fn.num_windows
    initial_step = float(sorted_history[0]["step"])
    final_step = float(sorted_history[-1]["step"])
    total_steps = final_step - initial_step
    steps_per_window = total_steps / num_windows

    print("-" * 70)
    print("Step-by-step intermediate calculations:")
    print("-" * 70)
    print(f"  total_steps        : {total_steps}")
    print(f"  steps_per_window   : {steps_per_window}")
    print()

    window_velocity_mags: list[float] = []
    window_velocity_vectors: list[tuple[float, float]] = []

    for w in range(num_windows):
        window_start = initial_step + w * steps_per_window
        window_end = window_start + steps_per_window

        first_entry = None
        last_entry = None

        for entry in sorted_history:
            s = float(entry["step"])
            if s < window_start:
                continue
            effective_window_end = window_end
            if w == num_windows - 1:
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

        window_steps = last_entry["step"] - first_entry["step"]
        dx = last_entry["com"][0] - first_entry["com"][0]
        dy = last_entry["com"][1] - first_entry["com"][1]
        velocity_mag = math.sqrt(dx * dx + dy * dy)

        if window_steps > 0:
            velocity_mag = velocity_mag / window_steps
            dx = dx / window_steps
            dy = dy / window_steps
        else:
            velocity_mag = 0.0
            dx = 0.0
            dy = 0.0

        window_velocity_mags.append(velocity_mag)
        window_velocity_vectors.append((dx, dy))

        print(f"  Window {w}:")
        print(f"    time range  : [{window_start:.1f}, {effective_window_end:.1f}]")
        print(f"    first_entry : step={first_entry['step']}, COM={first_entry['com']}, bits={first_entry['bit_count']}")
        print(f"    last_entry  : step={last_entry['step']}, COM={last_entry['com']}, bits={last_entry['bit_count']}")
        print(f"    window_steps: {window_steps}")
        print(f"    dx, dy      : {dx:.8f}, {dy:.8f}")
        print(f"    velocity_mag: {velocity_mag:.8f}")
        print()

    # Mean of velocity vectors
    mean_dx = sum(v[0] for v in window_velocity_vectors) / num_windows
    mean_dy = sum(v[1] for v in window_velocity_vectors) / num_windows
    mean_velocity_magnitude = math.sqrt(mean_dx * mean_dx + mean_dy * mean_dy)

    print("-" * 70)
    print("  mean_velocity_magnitude (magnitude of mean velocity vector):")
    print(f"    mean_dx  = {mean_dx:.8f}")
    print(f"    mean_dy  = {mean_dy:.8f}")
    print(f"    mean_velocity_magnitude = sqrt({mean_dx:.8f}^2 + {mean_dy:.8f}^2) = {mean_velocity_magnitude:.8f}")
    print()

    # Std dev of velocity magnitudes
    velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
    std_dev_velocity_magnitudes = float(np.std(velocity_magnitudes))

    print("-" * 70)
    print("  std_dev_velocity_magnitudes:")
    print(f"    window_velocity_mags = {window_velocity_mags}")
    print(f"    mean of mags = {float(np.mean(velocity_magnitudes)):.8f}")
    print(f"    std_dev (population) = {std_dev_velocity_magnitudes:.8f}")
    print()

    # Base fitness
    if mean_velocity_magnitude == 0.0:
        base_fitness = 0.0
    else:
        base_fitness = mean_velocity_magnitude / (1.0 + std_dev_velocity_magnitudes)

    print("-" * 70)
    print("  base_fitness = mean_velocity_magnitude / (1 + std_dev)")
    print(f"    = {mean_velocity_magnitude:.8f} / (1 + {std_dev_velocity_magnitudes:.8f})")
    print(f"    = {mean_velocity_magnitude:.8f} / {1.0 + std_dev_velocity_magnitudes:.8f}")
    print(f"    = {base_fitness:.8f}")
    print()

    # Conservation score
    initial_bits = sorted_history[0]["bit_count"]
    print("-" * 70)
    print(f"  Leaky bit conservation score (initial_bits = {initial_bits}):")
    conservation_factors: list[float] = []
    for i, entry in enumerate(sorted_history):
        bit_count = entry["bit_count"]
        if bit_count == initial_bits:
            cf = 1.0
        else:
            cf = min(bit_count, initial_bits) / max(bit_count, initial_bits)
        conservation_factors.append(cf)

    total_conservation_score = sum(conservation_factors) / len(conservation_factors)
    print(f"    conservation_factors count: {len(conservation_factors)}")
    print(f"    count of factor == 1.0    : {conservation_factors.count(1.0)}")
    non_one = [c for c in conservation_factors if c != 1.0]
    if non_one:
        print(f"    non-1.0 factors          : {non_one}")
    print(f"    total_conservation_score = {total_conservation_score:.8f}")
    print()

    # Final fitness
    fitness = base_fitness * total_conservation_score

    print("=" * 70)
    print("  FINAL RESULTS:")
    print("=" * 70)
    print(f"  mean_velocity_magnitude      : {mean_velocity_magnitude:.8f}")
    print(f"  std_dev_velocity_magnitudes  : {std_dev_velocity_magnitudes:.8f}")
    print(f"  leaky_bit_conservation_score : {total_conservation_score:.8f}")
    print(f"  base_fitness                 : {base_fitness:.8f}")
    print(f"  final_fitness                : {fitness:.8f}")
    print("=" * 70)

    # Also run the actual __call__ for verification
    actual_fitness = fitness_fn(history)
    print()
    print(f"  fitness_fn(history) = {actual_fitness:.8f}")
    assert math.isclose(fitness, actual_fitness, rel_tol=1e-12), "Manual and __call__ results differ!"


if __name__ == "__main__":
    main()
