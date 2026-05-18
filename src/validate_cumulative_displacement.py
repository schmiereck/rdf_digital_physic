#!/usr/bin/env python3
"""
validate_cumulative_displacement.py

Validates that the CumulativeDisplacementFitness fitness function
correctly penalises the "bad" stationary-oscillator rule from iter_200.
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from evolution import make_ltromino_grid, rule_dict_to_lut, step_grid, center_of_mass
from fitness_v2 import CumulativeDisplacementFitness

PROJECT_ROOT = Path(__file__).parent.parent
CAMPION_PATH = PROJECT_ROOT / "archive" / "iter_200" / "results" / "champion_vc_rule.json"
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_202" / "iter_001" / "results"


def main() -> None:
    # ── 1. Load the champion rule from iter_200 ──────────────────────────
    print("=" * 60)
    print("Validation: CumulativeDisplacementFitness on iter_200 champion")
    print("=" * 60)

    with open(CAMPION_PATH) as f:
        champ_data = json.load(f)

    rule_dict = champ_data["rule_dict"]
    print(f"\nChampion rule from iter_200 loaded:")
    print(f"  rule entries : {len(rule_dict)}")

    # ── 2. Use the L-tromino seed ───────────────────────────────────────
    # The iter_200 seed was: [[0,0],[0,1],[1,1]] (a 3-cell L-tromino)
    # but the CumulativeDisplacementFitness uses T_TROMINO by default.
    # For a fair comparison, we use the L-tromino seed the task requests.

    # Use L-tromino seed (same shape as iter_200 champion's seed)
    L_TROMINO = [(0, 0), (0, 1), (1, 1)]

    grid_size = 128
    sim_steps = 250  # match iter_200's simulation_steps

    # Create fitness function with L-tromino particle
    cdf = CumulativeDisplacementFitness(
        grid_size=grid_size,
        simulation_steps=sim_steps,
        particle=L_TROMINO,
    )

    # ── 3. Evaluate the champion rule ────────────────────────────────────
    fitness, metrics = cdf(rule_dict)

    print(f"\n--- CumulativeDisplacementFitness Results ---")
    print(f"  Fitness              : {fitness:.8f}")
    print(f"  Displacement (CoM)   : {metrics['displacement']:.6f}")
    print(f"  Initial CoM          : ({metrics['initial_com'][0]:.4f}, {metrics['initial_com'][1]:.4f})")
    print(f"  Final CoM            : ({metrics['final_com'][0]:.4f}, {metrics['final_com'][1]:.4f})")
    print(f"  Initial bits         : {metrics['initial_bits']}")
    print(f"  Final bits           : {metrics['final_bits']}")

    # ── 4. Also evaluate with SparseGliderFitness for comparison ─────────
    from fitness_v2 import SparseGliderFitness
    sgf = SparseGliderFitness(
        grid_size=grid_size,
        simulation_steps=sim_steps,
        checkpoint_every=50,
        particle=L_TROMINO,
    )
    sg_fitness, sg_metrics = sgf(rule_dict)
    print(f"\n--- SparseGliderFitness (for comparison) ---")
    print(f"  Fitness              : {sg_fitness:.8f}")
    print(f"  Total displacement   : {sg_metrics['total_displacement']:.6f}")
    print(f"  Displacements per checkpoint: {sg_metrics['displacements']}")
    print(f"  Mean sparsity        : {sg_metrics['mean_sparsity']:.6f}")
    print(f"  Reason               : {sg_metrics.get('reason', 'N/A')}")

    # ── 5. Check success criterion ───────────────────────────────────────
    SUCCESS_THRESHOLD = 0.1
    passed = fitness < SUCCESS_THRESHOLD

    print(f"\n{'=' * 60}")
    print(f"  Success Criterion: fitness < {SUCCESS_THRESHOLD}")
    print(f"  Achieved fitness  : {fitness:.8f}")
    print(f"  PASSED: {'YES ✓' if passed else 'NO ✗'}")
    print(f"{'=' * 60}")

    # ── 6. Write validation report ───────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "validation_report.txt"

    report_lines = [
        "Validation Report: CumulativeDisplacementFitness",
        "=" * 50,
        "",
        f"Test Date: (auto-generated)",
        f"Champion Rule Source: archive/iter_200/results/champion_vc_rule.json",
        f"Seed Particle: L-tromino (3 cells)",
        f"Grid Size: {grid_size}",
        f"Simulation Steps: {sim_steps}",
        "",
        "--- CumulativeDisplacementFitness Results ---",
        f"Fitness: {fitness:.8f}",
        f"Displacement (CoM): {metrics['displacement']:.6f}",
        f"Initial CoM: ({metrics['initial_com'][0]:.4f}, {metrics['initial_com'][1]:.4f})",
        f"Final CoM: ({metrics['final_com'][0]:.4f}, {metrics['final_com'][1]:.4f})",
        f"Initial bits: {metrics['initial_bits']}",
        f"Final bits: {metrics['final_bits']}",
        "",
        "--- SparseGliderFitness (for comparison) ---",
        f"Fitness: {sg_fitness:.8f}",
        f"Total displacement: {sg_metrics['total_displacement']:.6f}",
        f"Displacements per checkpoint: {sg_metrics['displacements']}",
        f"Mean sparsity: {sg_metrics['mean_sparsity']:.6f}",
        f"Reason: {sg_metrics.get('reason', 'N/A')}",
        "",
        "--- Success Criterion ---",
        f"Threshold: fitness < {SUCCESS_THRESHOLD}",
        f"Result: {'PASSED' if passed else 'FAILED'}",
        "",
        "--- Interpretation ---",
    ]

    if passed:
        report_lines.append(
            "The CumulativeDisplacementFitness correctly identifies this rule "
            "as a stationary oscillator exploit. The net displacement from "
            "t=0 to t=max_steps is small (the oscillator moved once then "
            "oscillated in place, cancelling its CoM position over the full "
            "run). This confirms the fix for the phase-sampling exploit "
            "observed in iter_201."
        )
    else:
        report_lines.append(
            "WARNING: The fitness is above the threshold. The oscillator "
            "rule may still be scoring too high."
        )

    report_text = "\n".join(report_lines) + "\n"

    with open(report_path, "w") as f:
        f.write(report_text)

    print(f"\nValidation report written to: {report_path}")

    # Return 0 on success, 1 on failure
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
