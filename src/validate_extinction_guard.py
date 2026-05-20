#!/usr/bin/env python3
"""
validate_extinction_guard.py

Re-simulate the iter_221 champion rule (perfect unwrapped CoM) and evaluate it
with the *modified* DisplacementConsistencyFitness from src/new_fitness.py.

Goal: Verify that the computed fitness is **exactly 0.0**.

The "extinction guard" modification in new_fitness.py adds a minimum-velocity
gate:  if the mean velocity magnitude across all windows falls below
``min_velocity`` (default 0.05), the fitness is forced to 0.0 regardless
of other metrics.  This eliminates "tiny drifter" rules that score a
fractional point by moving *too slowly* to be useful gliders.

The old champion from iter_221 (fitness=0.000615) moves slowly enough to
cross this new threshold — confirming the extinction guard works.
"""

from __future__ import annotations

import json
import sys
import math
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Project setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from new_fitness import DisplacementConsistencyFitness   # noqa: E402
from evolution import rule_dict_to_lut, step_grid        # noqa: E402

# ---------------------------------------------------------------------------
# Constants (must match those used during iter 221)
# ---------------------------------------------------------------------------
GRID_SIZE       = 128
STEPS           = 500
NUM_WINDOWS     = 5
MAX_BIT_THRESHOLD = 12
MAX_VEL_THRESHOLD = 0.9
MIN_VEL         = 0.05

SEED_CELLS = [(63, 63), (64, 63), (64, 64)]

# ---------------------------------------------------------------------------
# Path to the old champion rule
# ---------------------------------------------------------------------------
CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule_perfect.json"
OUTPUT_DIR    = PROJECT_ROOT / "archive" / "iter_222" / "results"


# ---------------------------------------------------------------------------
# Simulation helpers (mirrors run_evolution_exp_221_perfect.py)
# ---------------------------------------------------------------------------

def _unwrap_com(prev_com: tuple[float, float], raw_com: tuple[float, float],
                grid_size: int = GRID_SIZE) -> tuple[float, float]:
    """Unwrap one raw CoM step relative to the previous raw CoM."""
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


def com_and_bits(grid: np.ndarray, grid_size: int = GRID_SIZE):
    """Return the *raw toroidal* centre of mass and bit count for a grid."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())


def simulate_with_history(rule_dict: dict) -> list:
    """Run a CA simulation and return a history with perfectly unwrapped CoM."""
    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1

    # --- Continuous unwrapped CoM tracking ---
    raw_c0, b0 = com_and_bits(grid)
    prev_raw   = (raw_c0[0], raw_c0[1])
    hist = [{"step": 0, "com": prev_raw, "bit_count": b0}]

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = com_and_bits(grid)

        unwrapped = _unwrap_com(prev_raw, raw_c)
        prev_raw  = raw_c

        hist.append({"step": t, "com": unwrapped, "bit_count": bc})

    return hist


# ---------------------------------------------------------------------------
# Diagnostic output helpers
# ---------------------------------------------------------------------------

def print_sim_summary(history: list[dict]) -> None:
    """Print a diagnostic summary of the simulation history."""
    print(f"  Steps recorded    : {len(history)}")
    print(f"  Initial CoM       : {history[0]['com']}")
    print(f"  Final CoM         : {history[-1]['com']}")
    print(f"  Initial bit count : {history[0]['bit_count']}")
    print(f"  Final bit count   : {history[-1]['bit_count']}")

    # Per-window velocity analysis
    total_steps = float(history[-1]["step"] - history[0]["step"])
    steps_per_window = total_steps / NUM_WINDOWS

    print(f"\n  Per-window velocity analysis:")
    print(f"  {'Window':>8s} | {'Start':>6s} | {'End':>6s} | {'dx':>10s} | {'dy':>10s} | {'mag':>10s}")
    print(f"  {'-'*8}+-{'-'*6}+-{'-'*6}+-{'-'*10}+-{'-'*10}+-{'-'*10}")

    for w in range(NUM_WINDOWS):
        window_start = history[0]["step"] + int(w * steps_per_window)
        if w == NUM_WINDOWS - 1:
            window_end = STEPS
        else:
            window_end = int((w + 1) * steps_per_window)

        first = history[window_start]
        last  = history[window_end]
        dx = last["com"][0] - first["com"][0]
        dy = last["com"][1] - first["com"][1]
        window_steps = last["step"] - first["step"]
        mag = math.sqrt(dx*dx + dy*dy) / window_steps if window_steps > 0 else 0.0
        print(f"  {w:>8d} | {first['step']:>6d} | {last['step']:>6d} | {dx:>+10.4f} | {dy:>+10.4f} | {mag:>10.6f}")

    # Overall mean velocity
    total_dx = history[-1]["com"][0] - history[0]["com"][0]
    total_dy = history[-1]["com"][1] - history[0]["com"][1]
    overall_vel = math.sqrt(total_dx*total_dx + total_dy*total_dy) / STEPS
    print(f"\n  Overall mean velocity magnitude: {overall_vel:.6f} cells/step")
    print(f"  min_velocity threshold: {MIN_VEL}")
    if overall_vel < MIN_VEL:
        print(f"  *** MEANS VELOCITY BELOW MIN_VEL THRESHOLD -> fitness forced to 0.0 ***")
    else:
        print(f"  Mean velocity >= min_velocity -> no velocity-based extinction")

    # Bit conservation check
    initial_bits = history[0]["bit_count"]
    violations = [h for h in history if h["bit_count"] != initial_bits]
    print(f"\n  Bit conservation:")
    print(f"  Initial bits: {initial_bits}")
    print(f"  Steps with bit changes: {len(violations)}")
    if violations:
        for v in violations[:5]:
            print(f"    Step {v['step']}: bit_count={v['bit_count']}")
        if len(violations) > 5:
            print(f"    ... and {len(violations)-5} more")

    # Conservation score
    factors = []
    for entry in history:
        bc = entry["bit_count"]
        if bc == initial_bits:
            factors.append(1.0)
        else:
            factors.append(min(bc, initial_bits) / max(bc, initial_bits))
    conservation = sum(factors) / len(factors)
    print(f"  Conservation score (leaky): {conservation:.6f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("EXTINCTION GUARD VALIDATION")
    print("=" * 70)
    print(f"\n  Champion JSON : {CHAMPION_JSON}")
    print(f"  Fitness class : DisplacementConsistencyFitness")
    print(f"  Params        : num_windows={NUM_WINDOWS}, "
          f"max_bit_threshold={MAX_BIT_THRESHOLD}, "
          f"max_velocity_threshold={MAX_VEL_THRESHOLD}, "
          f"min_velocity={MIN_VEL}")
    print()

    # 1. Load the old champion rule
    with open(CHAMPION_JSON) as f:
        champion_data = json.load(f)

    original_fitness = champion_data["fitness"]
    rule_dict_raw    = {int(k): int(v) for k, v in champion_data["rule_dict"].items()}

    print(f"  Original recorded fitness : {original_fitness}")
    print(f"  Rule entries              : {len(rule_dict_raw)}")
    print()

    # 2. Re-simulate with the perfect-unwrapped CoM tracker
    print("  --- Re-simulating champion rule ---")
    history = simulate_with_history(rule_dict_raw)
    print_sim_summary(history)
    print()

    # 3. Evaluate with the modified DisplacementConsistencyFitness
    fitness_fn = DisplacementConsistencyFitness(
        num_windows=NUM_WINDOWS,
        max_bit_threshold=MAX_BIT_THRESHOLD,
        max_velocity_threshold=MAX_VEL_THRESHOLD,
        min_velocity=MIN_VEL,
    )

    computed_fitness = fitness_fn(history)
    print(f"  Computed fitness (DisplacementConsistencyFitness) : {computed_fitness}")
    print()

    # 4. Verification
    fitness_is_zero = computed_fitness == 0.0

    if fitness_is_zero:
        print("  *** VERIFIED: fitness is exactly 0.0 ***")
        verdict = "PASS"
    else:
        print(f"  *** NOT zero: fitness = {computed_fitness} ***")
        verdict = "FAIL"

    print()
    print("=" * 70)

    # 5. Write summary to archive/iter_222/results/extinction_verification.json
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "task": "extinction_guard_verification",
        "verdict": verdict,
        "champion_rule_source": str(CHAMPION_JSON),
        "original_recorded_fitness": original_fitness,
        "computed_fitness": float(computed_fitness),
        "fitness_is_exactly_zero": bool(computed_fitness == 0.0),
        "fitness_class": "DisplacementConsistencyFitness",
        "fitness_params": {
            "num_windows": NUM_WINDOWS,
            "max_bit_threshold": MAX_BIT_THRESHOLD,
            "max_velocity_threshold": MAX_VEL_THRESHOLD,
            "min_velocity": MIN_VEL,
        },
        "simulation_config": {
            "grid_size": GRID_SIZE,
            "steps": STEPS,
            "seed_cells": [list(c) for c in SEED_CELLS],
            "unwrapped_com": "perfect_continuous",
        },
        "sim_history_summary": {
            "steps_recorded": len(history),
            "initial_com": list(history[0]["com"]),
            "final_com": list(history[-1]["com"]),
            "initial_bit_count": history[0]["bit_count"],
            "final_bit_count": history[-1]["bit_count"],
            "total_dx": float(history[-1]["com"][0] - history[0]["com"][0]),
            "total_dy": float(history[-1]["com"][1] - history[0]["com"][1]),
            "overall_mean_velocity": float(
                math.sqrt(
                    (history[-1]["com"][0] - history[0]["com"][0]) ** 2
                    + (history[-1]["com"][1] - history[0]["com"][1]) ** 2
                ) / STEPS
            ),
        },
        "per_window_velocities": [],
        "reason_for_zero_fitness": _explain_zero_fitness(computed_fitness, fitness_fn, history),
    }

    # Add per-window velocity details
    total_steps = float(history[-1]["step"] - history[0]["step"])
    steps_per_window = total_steps / NUM_WINDOWS
    for w in range(NUM_WINDOWS):
        ws = history[0]["step"] + int(w * steps_per_window)
        we = history[-1]["step"] if w == NUM_WINDOWS - 1 else int((w + 1) * steps_per_window)
        first = history[ws]
        last = history[we]
        dx = last["com"][0] - first["com"][0]
        dy = last["com"][1] - first["com"][1]
        window_steps = last["step"] - first["step"]
        mag = math.sqrt(dx*dx + dy*dy) / window_steps if window_steps > 0 else 0.0
        summary["per_window_velocities"].append({
            "window": w,
            "start_step": first["step"],
            "end_step": last["step"],
            "dx": float(dx),
            "dy": float(dy),
            "velocity_magnitude": float(mag),
        })

    output_path = OUTPUT_DIR / "extinction_verification.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to: {output_path}")

    return 0 if fitness_is_zero else 1


def _explain_zero_fitness(
    fitness: float,
    fitness_fn: DisplacementConsistencyFitness,
    history: list[dict],
) -> str:
    """Determine and return the reason why the fitness is 0.0."""
    if fitness != 0.0:
        return "N/A (fitness is not 0.0)"

    reasons = []

    # Check empty history
    if not history:
        reasons.append("Empty simulation history")
        return " and ".join(reasons)

    sorted_history = sorted(history, key=lambda e: e["step"])

    # Check bit_count = 0
    if any(entry["bit_count"] == 0 for entry in sorted_history):
        reasons.append("Bit count reached 0 (annihilation)")

    # Check max_bit_threshold
    if fitness_fn.max_bit_threshold is not None:
        if any(entry["bit_count"] > fitness_fn.max_bit_threshold for entry in sorted_history):
            reasons.append(
                f"Bit count exceeded max_bit_threshold ({fitness_fn.max_bit_threshold})"
            )

    # Check strict conservation
    if fitness_fn.strict_conservation:
        initial_bits = sorted_history[0]["bit_count"]
        if any(entry["bit_count"] != initial_bits for entry in sorted_history):
            reasons.append("Strict conservation violated")

    # Compute overall mean velocity
    initial_step = float(sorted_history[0]["step"])
    final_step = float(sorted_history[-1]["step"])
    total_steps = final_step - initial_step

    if total_steps <= 0:
        reasons.append("Total steps <= 0")
        return " and ".join(reasons) if reasons else "Unknown"

    # Simulate per-window analysis to check min_velocity and max_velocity_threshold
    steps_per_window = total_steps / fitness_fn.num_windows
    window_velocity_mags: list[float] = []
    window_velocity_vectors: list[tuple[float, float]] = []

    for w in range(fitness_fn.num_windows):
        window_start = initial_step + w * steps_per_window
        window_end = window_start + steps_per_window
        effective_window_end = window_end
        if w == fitness_fn.num_windows - 1:
            effective_window_end = final_step

        first_entry = None
        last_entry = None
        for entry in sorted_history:
            s = float(entry["step"])
            if s < window_start:
                continue
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

    mean_dx = sum(v[0] for v in window_velocity_vectors) / fitness_fn.num_windows
    mean_dy = sum(v[1] for v in window_velocity_vectors) / fitness_fn.num_windows
    mean_velocity_magnitude = math.sqrt(mean_dx * mean_dx + mean_dy * mean_dy)

    # Check max_velocity_threshold
    if fitness_fn.max_velocity_threshold is not None:
        if mean_velocity_magnitude >= fitness_fn.max_velocity_threshold:
            reasons.append(
                f"Mean velocity ({mean_velocity_magnitude:.6f}) >= "
                f"max_velocity_threshold ({fitness_fn.max_velocity_threshold})"
            )

    # Check min_velocity
    if fitness_fn.min_velocity is not None:
        if mean_velocity_magnitude < fitness_fn.min_velocity:
            reasons.append(
                f"Mean velocity ({mean_velocity_magnitude:.6f}) < "
                f"min_velocity ({fitness_fn.min_velocity})  <-- extinction guard triggered"
            )

    # Check no net displacement
    if mean_velocity_magnitude == 0.0 and not reasons:
        reasons.append("No net directional displacement")

    # Check base_fitness == 0
    if not reasons:
        velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
        std_dev = float(np.std(velocity_magnitudes))
        if mean_velocity_magnitude > 0:
            base_fitness = mean_velocity_magnitude / (1.0 + std_dev)
        else:
            base_fitness = 0.0

        total_conservation_score = _compute_conservation_score(sorted_history)
        final_fitness = base_fitness * total_conservation_score

        if base_fitness == 0.0:
            reasons.append("base_fitness == 0 (mean_velocity == 0)")
        elif total_conservation_score == 0.0:
            reasons.append("conservation_score == 0")

    return " and ".join(reasons) if reasons else "Unknown reason"


def _compute_conservation_score(sim_history: list[dict]) -> float:
    """Compute the leaky bit-conservation score."""
    if not sim_history:
        return 1.0

    initial_bits = sim_history[0]["bit_count"]
    if initial_bits == 0:
        return 1.0

    conservation_factors: list[float] = []
    for entry in sim_history:
        bit_count = entry["bit_count"]
        if bit_count == initial_bits:
            conservation_factors.append(1.0)
        else:
            conservation_factors.append(
                min(bit_count, initial_bits) / max(bit_count, initial_bits)
            )

    return sum(conservation_factors) / len(conservation_factors)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
