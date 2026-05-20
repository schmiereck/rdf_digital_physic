#!/usr/bin/env python3
"""
diag_perfect_champion.py

Loads archive/iter_221/results/champion_rule_perfect.json, runs a 500-step
simulation with the same *perfect continuous unwrapped COM tracking* that
was used during evolution (from run_evolution_exp_221_perfect.py), and then
prints out every intermediate variable that DisplacementConsistencyFitness
computes so we can see exactly why the fitness is 0.0006154.

Output sections:
  1. Rule summary (rule_dict, fitness params)
  2. Full 501-step trajectory  (step, COM_raw, COM_unwrapped, bit_count)
  3. Windowed velocity analysis (per-window start/end step, first/last entry,
     dx, dy, window_steps, velocity_mag, velocity_vector)
  4. Global statistics (mean_velocity_magnitude, std_dev, etc.)
  5. Conservation score per-step and overall
  6. Final breakdown of the fitness formula
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

# -- Constants (must match run_evolution_exp_221_perfect.py) -----------------

GRID_SIZE       = 128
STEPS           = 500
LUT_SIZE        = 128
SEED_CELLS      = [[63, 63], [64, 63], [64, 64]]

CHAMPION_PATH = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule_perfect.json"


# -- Helpers ------------------------------------------------------------------

def com_and_bits(grid):
    """Return raw toroidal COM and bit count."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())


def _unwrap_com(prev_com, raw_com, grid_size=GRID_SIZE):
    """Unwrap one raw COM step relative to the previous raw COM."""
    pr, pc = prev_com
    cr, cc = raw_com
    half   = grid_size / 2.0

    dr = cr - pr
    dc = cc - pc

    if dr > half:
        cr -= grid_size
    elif dr < -half:
        cr += grid_size

    if dc > half:
        cc -= grid_size
    elif dc < -half:
        cc += grid_size

    return (cr, cc)


def simulate_with_history(rule_dict):
    """Run CA simulation, return history with perfectly unwrapped COM."""
    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1

    raw_c0, b0 = com_and_bits(grid)
    prev_raw = (raw_c0[0], raw_c0[1])
    hist = [{"step": 0, "com": prev_raw, "bit_count": b0}]

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = com_and_bits(grid)
        unwrapped = _unwrap_com(prev_raw, raw_c)
        prev_raw  = raw_c
        hist.append({"step": t, "com": unwrapped, "bit_count": bc})

    return hist


def unwrap_history_com(sorted_history, grid_size=GRID_SIZE):
    """
    Defensive COM unwrapping performed by DisplacementConsistencyFitness.
    This wraps the *already-unwrapped* history from simulate_with_history
    to see the double-unwrap effect.
    """
    unwrapped_coms = [sorted_history[0]["com"]]
    for i in range(1, len(sorted_history)):
        prev_com = sorted_history[i - 1]["com"]
        cur_com  = sorted_history[i]["com"]
        dx = cur_com[0] - prev_com[0]
        dy = cur_com[1] - prev_com[1]
        if dx > grid_size / 2:
            dx -= grid_size
        elif dx < -grid_size / 2:
            dx += grid_size
        if dy > grid_size / 2:
            dy -= grid_size
        elif dy < -grid_size / 2:
            dy += grid_size
        unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))
    return unwrapped_coms


def compute_conservation_factors(sorted_history):
    """Leaky bit-conservation score per-step."""
    if not sorted_history:
        return []
    initial_bits = sorted_history[0]["bit_count"]
    if initial_bits == 0:
        return [1.0] * len(sorted_history)
    factors = []
    for entry in sorted_history:
        bc = entry["bit_count"]
        if bc == initial_bits:
            factors.append(1.0)
        else:
            factors.append(min(bc, initial_bits) / max(bc, initial_bits))
    return factors


# -- Main ---------------------------------------------------------------------

def main():
    print("=" * 72)
    print("  DIAGNOSTIC: champion_rule_perfect.json")
    print("  Why is fitness = 0.0006154?")
    print("=" * 72)

    # -- Load champion --------------------------------------------------------
    with open(CHAMPION_PATH) as f:
        data = json.load(f)

    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    fitness_params = data["fitness_params"]
    stored_fitness = data["fitness"]

    print(f"\nRule dict keys: {sorted(rule_dict.keys())}")
    print(f"Stored fitness: {stored_fitness:.10f}")
    print(f"Fitness params: {fitness_params}")

    # -- Run simulation with perfect unwrapped COM ----------------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 1: 501-step trajectory")
    print(f"{'=' * 72}")

    history = simulate_with_history(rule_dict)

    # Recompute raw COM history for side-by-side comparison
    lut = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1
    raw_hist = []
    raw_c, bc = com_and_bits(grid)
    raw_hist.append({"step": 0, "com": raw_c, "bit_count": bc})
    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = com_and_bits(grid)
        raw_hist.append({"step": t, "com": raw_c, "bit_count": bc})

    print(f"{'step':>5s}  {'raw_r':>10s}  {'raw_c':>10s}  "
          f"{'uw_r':>12s}  {'uw_c':>12s}  {'bits':>6s}")
    print("-" * 60)
    for i in range(len(history)):
        rh = raw_hist[i]
        uh = history[i]
        print(f"{rh['step']:>5d}  {rh['com'][0]:>10.4f}  {rh['com'][1]:>10.4f}  "
              f"{uh['com'][0]:>12.4f}  {uh['com'][1]:>12.4f}  {uh['bit_count']:>6d}")

    # -- Section 2: Defensive unwrapping (double-unwrap) ----------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 2: Defensive unwrapping (DisplacementConsistencyFitness)")
    print(f"{'=' * 72}")

    unwrapped_coms = unwrap_history_com(history)
    print(f"{'step':>5s}  {'double_unwrapped_r':>20s}  "
          f"{'double_unwrapped_c':>20s}  {'delta_from_0':>16s}")
    print("-" * 68)
    base_r, base_c = history[0]["com"]
    for i in range(len(history)):
        diff_r = unwrapped_coms[i][0] - base_r
        diff_c = unwrapped_coms[i][1] - base_c
        print(f"{history[i]['step']:>5d}  {unwrapped_coms[i][0]:>20.4f}  "
              f"{unwrapped_coms[i][1]:>20.4f}  ({diff_r:>+12.4f}, {diff_c:>+12.4f})")

    # -- Section 3: Windowed velocity analysis --------------------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 3: Per-window velocity analysis")
    print(f"{'=' * 72}")

    num_windows = fitness_params["num_windows"]  # 5
    initial_step = float(history[0]["step"])
    final_step = float(history[-1]["step"])
    total_steps = final_step - initial_step
    steps_per_window = total_steps / num_windows

    window_velocity_mags = []
    window_velocity_vectors = []

    for w in range(num_windows):
        window_start = initial_step + w * steps_per_window
        window_end = window_start + steps_per_window
        if w == num_windows - 1:
            effective_window_end = final_step
        else:
            effective_window_end = window_end

        first_entry = None
        last_entry = None
        for entry in history:
            s = float(entry["step"])
            if s < window_start:
                continue
            if s > effective_window_end:
                break
            if first_entry is None:
                first_entry = entry
            last_entry = entry

        if first_entry is None or last_entry is None:
            wdmag = 0.0
            wvec = (0.0, 0.0)
        else:
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
            wdmag = velocity_mag
            wvec = (dx, dy)

        window_velocity_mags.append(wdmag)
        window_velocity_vectors.append(wvec)

        print(f"\n  Window {w+1}/{num_windows}:")
        print(f"    Time range:  [{window_start:.1f}, {effective_window_end:.1f}]  "
              f"span={effective_window_end - window_start:.1f} steps")
        if first_entry is None or last_entry is None:
            print(f"    No data points in window -> zero velocity")
        else:
            print(f"    First entry: step={first_entry['step']}, "
                  f"com=({first_entry['com'][0]:.4f}, {first_entry['com'][1]:.4f}), "
                  f"bit_count={first_entry['bit_count']}")
            print(f"    Last  entry: step={last_entry['step']}, "
                  f"com=({last_entry['com'][0]:.4f}, {last_entry['com'][1]:.4f}), "
                  f"bit_count={last_entry['bit_count']}")
            raw_dx = last_entry["com"][0] - first_entry["com"][0]
            raw_dy = last_entry["com"][1] - first_entry["com"][1]
            raw_mag = math.sqrt(raw_dx*raw_dx + raw_dy*raw_dy)
            print(f"    Delta COM (raw):    ({raw_dx:>+12.4f}, {raw_dy:>+12.4f})  "
                  f"mag={raw_mag:.6f}")
            if window_steps > 0:
                print(f"    Delta COM / step:   ({dx:>+12.8f}, {dy:>+12.8f})  "
                      f"mag={wdmag:.10f}")
            else:
                print(f"    window_steps=0 -> velocity_mag=0.0")

    # -- Section 4: Global statistics -----------------------------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 4: Global statistics")
    print(f"{'=' * 72}")

    velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
    mean_dx = sum(v[0] for v in window_velocity_vectors) / num_windows
    mean_dy = sum(v[1] for v in window_velocity_vectors) / num_windows
    mean_velocity_magnitude = math.sqrt(mean_dx * mean_dx + mean_dy * mean_dy)
    std_dev = float(np.std(velocity_magnitudes))

    print(f"  window_velocity_mags:      {window_velocity_mags}")
    print(f"  window_velocity_vectors:   {window_velocity_vectors}")
    print(f"  mean_dx:                   {mean_dx:.10f}")
    print(f"  mean_dy:                   {mean_dy:.10f}")
    print(f"  mean_velocity_magnitude:   {mean_velocity_magnitude:.10f}")
    print(f"  std_dev (velocity mags):   {std_dev:.10f}")
    print(f"  np.array(mags):            {velocity_magnitudes}")
    print(f"  np.std(mags):              {float(np.std(velocity_magnitudes)):.10f}")

    # -- Check hard thresholds ------------------------------------------------
    print(f"\n  max_velocity_threshold: {fitness_params.get('max_velocity_threshold')}  ->  "
          f"{'FAIL (0.0)' if fitness_params.get('max_velocity_threshold') is not None and mean_velocity_magnitude >= fitness_params['max_velocity_threshold'] else 'OK'}")
    print(f"  min_velocity:           {fitness_params.get('min_velocity')}  ->  "
          f"{'FAIL (0.0)' if fitness_params.get('min_velocity') is not None and mean_velocity_magnitude < fitness_params['min_velocity'] else 'OK'}")
    print(f"  max_bit_threshold:      {fitness_params.get('max_bit_threshold')}")

    any_bit_exceed = any(e["bit_count"] > fitness_params.get("max_bit_threshold", 999) for e in history) if fitness_params.get("max_bit_threshold") else False
    print(f"  Any step exceeding bit threshold: {any_bit_exceed}")

    # -- Section 5: Conservation score ----------------------------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 5: Leaky bit-conservation score")
    print(f"{'=' * 72}")

    conservation_factors = compute_conservation_factors(history)
    total_conservation_score = sum(conservation_factors) / len(conservation_factors)

    print(f"  initial_bits (step 0): {history[0]['bit_count']}")
    print(f"  Total history entries: {len(conservation_factors)}")
    print(f"  Perfect matches (factor=1.0): "
          f"{sum(1 for f in conservation_factors if f == 1.0)}")
    print(f"  Imperfect matches: "
          f"{sum(1 for f in conservation_factors if f != 1.0)}")

    if any(f != 1.0 for f in conservation_factors):
        print(f"\n  Non-perfect steps (bit_count != 3):")
        for i, entry in enumerate(history):
            if conservation_factors[i] != 1.0:
                print(f"    step {entry['step']:>4d}: bit_count={entry['bit_count']:>4d}, "
                      f"factor={conservation_factors[i]:.6f}")

    print(f"\n  total_conservation_score: {total_conservation_score:.10f}")

    # -- Section 6: Final fitness calculation ---------------------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 6: Final fitness breakdown")
    print(f"{'=' * 72}")

    max_vel_thresh = fitness_params.get("max_velocity_threshold")
    min_vel = fitness_params.get("min_velocity")
    max_bit_thresh = fitness_params.get("max_bit_threshold")

    if any_bit_exceed:
        print(f"  [FAIL] Bit threshold {max_bit_thresh} exceeded -> fitness = 0.0")
        base_fitness = 0.0
    elif max_vel_thresh is not None and mean_velocity_magnitude >= max_vel_thresh:
        print(f"  [FAIL] mean_velocity ({mean_velocity_magnitude:.6f}) >= "
              f"max_velocity_threshold ({max_vel_thresh}) -> fitness = 0.0")
        base_fitness = 0.0
    elif min_vel is not None and mean_velocity_magnitude < min_vel:
        print(f"  [FAIL] mean_velocity ({mean_velocity_magnitude:.6f}) < "
              f"min_velocity ({min_vel}) -> fitness = 0.0")
        base_fitness = 0.0
    elif mean_velocity_magnitude == 0.0:
        print(f"  [FAIL] No net displacement -> base_fitness = 0.0")
        base_fitness = 0.0
    else:
        base_fitness = mean_velocity_magnitude / (1.0 + std_dev)
        print(f"  base_fitness = mean_velocity_magnitude / (1 + std_dev)")
        print(f"             = {mean_velocity_magnitude:.10f} / (1 + {std_dev:.10f})")
        print(f"             = {mean_velocity_magnitude:.10f} / {1.0 + std_dev:.10f}")
        print(f"             = {base_fitness:.10f}")

    fitness = base_fitness * total_conservation_score
    print(f"\n  final_fitness = base_fitness x total_conservation_score")
    print(f"              = {base_fitness:.10f} x {total_conservation_score:.10f}")
    print(f"              = {fitness:.10f}")
    print(f"\n  Stored fitness:  {stored_fitness:.10f}")
    print(f"  Computed fitness: {fitness:.10f}")
    print(f"  Match: {abs(fitness - stored_fitness) < 1e-12}")

    # -- Section 7: Diagnosis -------------------------------------------------
    print(f"\n{'=' * 72}")
    print("  SECTION 7: Diagnosis")
    print(f"{'=' * 72}")

    if std_dev > 0.5:
        print(f"  [!] HIGH std_dev ({std_dev:.6f}) dominates the denominator (1 + {std_dev:.4f})")
        print(f"      -> The glider's velocity magnitude fluctuates significantly")
        print(f"         between windows, indicating inconsistent motion.")

    if mean_velocity_magnitude < 0.1:
        print(f"  [!] LOW mean velocity ({mean_velocity_magnitude:.6f}): the object")
        print(f"      moves very slowly or barely moves at all.")

    if total_conservation_score < 0.99:
        print(f"  [!] Conservation score ({total_conservation_score:.6f}) below 1.0:")
        print(f"      The bit count changes during simulation, applying a multiplicative")
        print(f"      penalty of {total_conservation_score:.6f}.")

    if any_bit_exceed:
        print(f"  [!] max_bit_threshold ({max_bit_thresh}) exceeded -> immediate 0.0")

    if max_vel_thresh is not None and mean_velocity_magnitude >= max_vel_thresh:
        print(f"  [!] Speed-of-light: mean velocity {mean_velocity_magnitude:.4f} >= {max_vel_thresh}")
    elif max_vel_thresh is not None and mean_velocity_magnitude < max_vel_thresh:
        print(f"  [OK] Speed below light speed ({mean_velocity_magnitude:.6f} < {max_vel_thresh})")

    # Dominant penalty factor
    denominator = 1.0 + std_dev
    vel_component = mean_velocity_magnitude / denominator if denominator > 0 else 0.0
    print(f"\n  Dominant penalty breakdown:")
    print(f"    velocity component:  {mean_velocity_magnitude:.6f} / {denominator:.4f} "
          f"= {vel_component:.8f}")
    print(f"    conservation factor: {total_conservation_score:.6f}")
    print(f"    product:             {fitness:.10f}")

    # Window velocity range
    if len(window_velocity_mags) > 1:
        vrange = max(window_velocity_mags) - min(window_velocity_mags)
        print(f"\n  Window velocity range: {min(window_velocity_mags):.8f} - "
              f"{max(window_velocity_mags):.8f}  (range={vrange:.8f})")
        if vrange > 0.01:
            print(f"  [!] Large velocity swing between windows!")

    # Total displacement
    total_dx = unwrapped_coms[-1][0] - unwrapped_coms[0][0]
    total_dy = unwrapped_coms[-1][1] - unwrapped_coms[0][1]
    total_disp = math.sqrt(total_dx**2 + total_dy**2)
    print(f"\n  Total unwrapped displacement: ({total_dx:.4f}, {total_dy:.4f})  "
          f"= {total_disp:.4f} in {STEPS} steps")
    avg_speed = total_disp / STEPS if STEPS > 0 else 0.0
    print(f"  Average speed (total disp / steps): {avg_speed:.8f}")

    # Check if it's a speed-of-light glider (displacement ~= steps)
    if abs(avg_speed - 1.0) < 0.01:
        print(f"  [!] This is a speed-of-light (v=1c) glider!")
        print(f"      Fitness is 0.0 because mean_velocity ({avg_speed:.4f}) >= 0.9 threshold.")

    print(f"\n{'=' * 72}")
    print("  DONE")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    main()
