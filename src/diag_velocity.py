#!/usr/bin/env python3
"""
diag_velocity.py — Diagnostic script for DisplacementConsistencyFitness.

1. Load champion_rule.json from archive/iter_221/results/
2. Run a simulation for 500 steps with the L-tromino seed.
3. Capture a full simulation history (step, com, bit_count).
4. Instantiate DisplacementConsistencyFitness with:
     num_windows=5, max_bit_threshold=12, max_velocity_threshold=0.9
5. Evaluate the simulation history and print ALL internal variables
   computed inside __call__ (window velocities, magnitudes, means, std dev,
   conservation scores, etc.).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).parent))

from new_fitness import DisplacementConsistencyFitness
from engine import build_lut


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule.json"
SIM_STEPS    = 500
GRID_SIZE    = 128
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS = len(LTROMINO_CELLS)  # 3
BITS_PER_CELL = 1  # champion is a 1-bit rule


# ─────────────────────────────────────────────────────────────────────────────
# Simulation helpers
# ─────────────────────────────────────────────────────────────────────────────

def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Advance a 2D binary grid by one CA step using the 128-entry LUT."""
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,     1, axis=1)
    nw = np.roll(w,    -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def unwrap_com(prev_com: tuple, curr_com: tuple, size: int = GRID_SIZE) -> tuple:
    """Adjust curr_com for torus wrapping relative to prev_com."""
    pr, pc = prev_com
    cr, cc = curr_com
    half = size / 2.0
    dr = cr - pr
    if dr > half:
        cr -= size
    elif dr < -half:
        cr += size
    dc = cc - pc
    if dc > half:
        cc -= size
    elif dc < -half:
        cc += size
    return (cr, cc)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── 1. Load champion rule ────────────────────────────────────────────
    print("=" * 70)
    print("  Loading champion rule from", CHAMP_PATH)
    print("=" * 70)
    with open(CHAMP_PATH) as f:
        champ = json.load(f)

    rule_dict = champ["rule_dict"]
    chromosome = champ["chromosome"]
    print(f"  fitness_function : {champ.get('fitness_function', 'N/A')}")
    print(f"  fitness          : {champ['fitness']:.6f}")
    print(f"  rule_dict entries : {len(rule_dict)}")
    print(f"  chromosome length : {len(chromosome)}")
    print(f"  seed_particle     : {champ.get('seed_particle', 'N/A')}")
    print(f"  seed_cells        : {champ.get('seed_cells', 'N/A')}")
    print()

    # Build LUT
    lut = np.asarray(chromosome, dtype=np.uint8)
    print(f"  LUT non-zero entries: {int(lut.sum())}/{len(lut)}")
    print()

    # ── 2. Run simulation ────────────────────────────────────────────────
    print("=" * 70)
    print("  Running simulation for", SIM_STEPS, "steps")
    print("=" * 70)

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1

    initial_com = center_of_mass(grid)
    prev_raw    = initial_com
    unwrapped   = initial_com

    sim_history: list[dict] = [
        {"step": 0, "com": (float(initial_com[0]), float(initial_com[1])), "bit_count": INITIAL_BITS}
    ]

    for step in range(1, SIM_STEPS + 1):
        grid    = step_grid(grid, lut)
        raw_com = center_of_mass(grid)

        adj      = unwrap_com(prev_raw, raw_com)
        dr       = adj[0] - prev_raw[0]
        dc       = adj[1] - prev_raw[1]
        unwrapped = (unwrapped[0] + dr, unwrapped[1] + dc)
        prev_raw  = raw_com

        bc = int(grid.sum())

        sim_history.append({
            "step":      step,
            "com":       (float(unwrapped[0]), float(unwrapped[1])),
            "bit_count": bc,
        })

        if step % 100 == 0:
            ddx = unwrapped[0] - initial_com[0]
            ddy = unwrapped[1] - initial_com[1]
            disp = math.sqrt(ddx * ddx + ddy * ddy)
            print(f"  step {step:>4}  bit_count={bc:>3}  unwrapped_com=({unwrapped[0]:10.2f}, {unwrapped[1]:10.2f})  "
                  f"displacement={disp:8.3f}")

    final_bc = int(grid.sum())
    total_disp = math.sqrt(
        (unwrapped[0] - initial_com[0]) ** 2 +
        (unwrapped[1] - initial_com[1]) ** 2
    )
    print(f"\n  Final bit count    : {final_bc}")
    print(f"  Total displacement : {total_disp:.4f} cells")
    print(f"  Displacement/step  : {total_disp / SIM_STEPS:.4f}")
    print()

    # ── 3. Instantiate fitness function ──────────────────────────────────
    fitness_fn = DisplacementConsistencyFitness(
        num_windows=5,
        bits_per_cell=BITS_PER_CELL,
        strict_conservation=False,
        max_bit_threshold=12,
        max_velocity_threshold=0.9,
    )

    print("=" * 70)
    print("  Fitness parameters")
    print("=" * 70)
    print(f"  num_windows            : {fitness_fn.num_windows}")
    print(f"  bits_per_cell          : {fitness_fn.bits_per_cell}")
    print(f"  strict_conservation    : {fitness_fn.strict_conservation}")
    print(f"  max_bit_threshold      : {fitness_fn.max_bit_threshold}")
    print(f"  max_velocity_threshold : {fitness_fn.max_velocity_threshold}")
    print(f"  min_velocity           : {fitness_fn.min_velocity}")
    print()

    # ── 4. Run __call__ and intercept internal variables ─────────────────
    # We'll manually execute the __call__ body to capture every variable.
    print("=" * 70)
    print("  Executing DisplacementConsistencyFitness.__call__ internals")
    print("=" * 70)
    print()

    sim_history_copy = list(sim_history)

    # --- Step 1: sort ---
    sorted_history = sorted(sim_history_copy, key=lambda e: e["step"])

    # --- Step 1.5: COM unwrapping ---
    unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
    for i in range(1, len(sorted_history)):
        prev_com = sorted_history[i - 1]["com"]
        cur_com = sorted_history[i]["com"]
        dx = cur_com[0] - prev_com[0]
        dy = cur_com[1] - prev_com[1]
        if dx > 64:
            dx -= 128.0
        elif dx < -64:
            dx += 128.0
        if dy > 64:
            dy -= 128.0
        elif dy < -64:
            dy += 128.0
        unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))

    unwrapped_history: list[dict] = []
    for i, entry in enumerate(sorted_history):
        unwrapped_entry = dict(entry)
        unwrapped_entry["com"] = unwrapped_coms[i]
        unwrapped_history.append(unwrapped_entry)
    sorted_history = unwrapped_history

    print("--- Step 1: Sorting & COM unwrapping ---")
    print(f"  len(sorted_history) = {len(sorted_history)}")
    print(f"  sorted_history[0]   = {sorted_history[0]}")
    print(f"  sorted_history[-1]  = {sorted_history[-1]}")
    print()

    # --- Step 1.7: max_bit_threshold check ---
    if fitness_fn.max_bit_threshold is not None:
        exceeded = [e for e in sorted_history if e["bit_count"] > fitness_fn.max_bit_threshold]
        print(f"--- Step 1.5: max_bit_threshold check ---")
        print(f"  max_bit_threshold         = {fitness_fn.max_bit_threshold}")
        print(f"  entries exceeding threshold = {len(exceeded)}")
        if exceeded:
            for e in exceeded[:5]:
                print(f"    step={e['step']}  bit_count={e['bit_count']}")
        print()

    # --- Step 1.8: strict_conservation check ---
    if fitness_fn.strict_conservation:
        initial_bits = sorted_history[0]["bit_count"]
        non_conserving = [e for e in sorted_history if e["bit_count"] != initial_bits]
        print(f"--- Step 1.6: strict_conservation check ---")
        print(f"  entries violating conservation = {len(non_conserving)}")
        print()

    initial_step = float(sorted_history[0]["step"])
    final_step = float(sorted_history[-1]["step"])
    total_steps = final_step - initial_step

    print(f"--- Step 2: Total time range ---")
    print(f"  initial_step = {initial_step}")
    print(f"  final_step   = {final_step}")
    print(f"  total_steps  = {total_steps}")
    print()

    # --- Step 2: Window velocity computation ---
    steps_per_window = total_steps / fitness_fn.num_windows

    print(f"--- Step 2: Per-window velocity computation ---")
    print(f"  steps_per_window = {steps_per_window}")
    print()

    window_velocities: list[tuple[float, float]] = []
    window_velocity_mags: list[float] = []
    window_velocity_vectors: list[tuple[float, float]] = []

    for w in range(fitness_fn.num_windows):
        window_start = initial_step + w * steps_per_window
        window_end = window_start + steps_per_window

        first_entry = None
        last_entry = None

        for entry in sorted_history:
            s = float(entry["step"])
            if s < window_start:
                continue
            effective_window_end = window_end
            if w == fitness_fn.num_windows - 1:
                effective_window_end = final_step
            if s > effective_window_end:
                break
            if first_entry is None:
                first_entry = entry
            last_entry = entry

        if first_entry is None or last_entry is None:
            window_velocity_mags.append(0.0)
            window_velocity_vectors.append((0.0, 0.0))
            window_velocities.append((0.0, 0.0, 0.0))
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
        window_velocities.append((dx, dy, velocity_mag))

        w_start_step = first_entry["step"]
        w_end_step   = last_entry["step"]
        print(f"  Window {w}: steps [{w_start_step}, {w_end_step}] "
              f"dx={dx:.6f}  dy={dy:.6f}  mag={velocity_mag:.6f}")

    print()

    # --- Step 3: mean velocity vector ---
    mean_dx = sum(v[0] for v in window_velocity_vectors) / fitness_fn.num_windows
    mean_dy = sum(v[1] for v in window_velocity_vectors) / fitness_fn.num_windows
    mean_velocity_magnitude = math.sqrt(mean_dx * mean_dx + mean_dy * mean_dy)

    print("--- Step 3: Mean velocity vector (directional drift) ---")
    print(f"  mean_dx                = {mean_dx}")
    print(f"  mean_dy                = {mean_dy}")
    print(f"  mean_velocity_magnitude= {mean_velocity_magnitude}")
    print()

    # --- max_velocity_threshold check ---
    if fitness_fn.max_velocity_threshold is not None:
        print(f"--- Velocity threshold check ---")
        print(f"  max_velocity_threshold = {fitness_fn.max_velocity_threshold}")
        print(f"  mean_velocity_magnitude>= threshold? {mean_velocity_magnitude >= fitness_fn.max_velocity_threshold}")
        if mean_velocity_magnitude >= fitness_fn.max_velocity_threshold:
            print("  -> Would return 0.0 (velocity too high)")
        print()

    # --- min_velocity check ---
    if fitness_fn.min_velocity is not None:
        print(f"--- Min velocity check ---")
        print(f"  min_velocity           = {fitness_fn.min_velocity}")
        print(f"  mean_velocity_magnitude< min? {mean_velocity_magnitude < fitness_fn.min_velocity}")
        if mean_velocity_magnitude < fitness_fn.min_velocity:
            print("  -> Would return 0.0 (velocity too low)")
        print()

    # --- Step 4: std dev of velocity magnitudes ---
    velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
    std_dev_velocity_magnitudes = float(np.std(velocity_magnitudes))

    print("--- Step 4: Standard deviation of velocity magnitudes ---")
    print(f"  velocity_magnitudes (array) = {velocity_magnitudes.tolist()}")
    print(f"  mean(mag)                   = {float(np.mean(velocity_magnitudes))}")
    print(f"  std(mag)                    = {std_dev_velocity_magnitudes}")
    print()

    # --- Step 5: Core fitness formula ---
    if mean_velocity_magnitude == 0.0:
        base_fitness = 0.0
    else:
        base_fitness = mean_velocity_magnitude / (1.0 + std_dev_velocity_magnitudes)

    print("--- Step 5: Core fitness formula ---")
    print(f"  base_fitness = mean_velocity_magnitude / (1 + std_dev)")
    print(f"             = {mean_velocity_magnitude} / (1 + {std_dev_velocity_magnitudes})")
    print(f"             = {base_fitness}")
    print()

    # --- Step 6: Conservation score ---
    total_conservation_score = fitness_fn._compute_conservation_score(sorted_history)

    print("--- Step 6: Leaky conservation score ---")
    print(f"  total_conservation_score = {total_conservation_score}")

    # Print per-step conservation factors for detail
    initial_bits = sorted_history[0]["bit_count"]
    print(f"  initial_bits = {initial_bits}")
    factors = []
    for entry in sorted_history:
        bc = entry["bit_count"]
        if bc == initial_bits:
            cf = 1.0
        else:
            cf = min(bc, initial_bits) / max(bc, initial_bits)
        factors.append(cf)
    print(f"  mean conservation factor = {sum(factors)/len(factors):.6f}")
    print()

    # --- Step 7: Final fitness ---
    fitness = base_fitness * total_conservation_score

    print("--- Step 7: Final fitness ---")
    print(f"  fitness = base_fitness * total_conservation_score")
    print(f"          = {base_fitness} * {total_conservation_score}")
    print(f"          = {fitness}")
    print()

    # ── 5. Verify by calling __call__ directly ───────────────────────────
    print("=" * 70)
    print("  Direct __call__ result")
    print("=" * 70)
    direct_result = fitness_fn(sim_history)
    print(f"  fitness_fn(sim_history) = {direct_result}")
    print(f"  matches computed result? {abs(direct_result - fitness) < 1e-12}")
    print()


if __name__ == "__main__":
    main()
