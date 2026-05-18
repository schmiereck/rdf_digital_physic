#!/usr/bin/env python3
"""
run_evolution_202_4.py  —  Evolve and validate a v<c glider using
RobustCumulativeDisplacementFitness, then save champion + GIF + report.
"""

import sys
import os
import json
import math
import numpy as np
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.main_v2 import (
        run_evolution, chromosome_to_rule_dict,
        L_TROMINO, POPULATION_SIZE, ELITE_FRACTION,
    )
    from src.fitness_v2 import RobustCumulativeDisplacementFitness
    from src.evolution import rule_dict_to_lut, step_grid, center_of_mass
except ImportError:
    from main_v2 import (
        run_evolution, chromosome_to_rule_dict,
        L_TROMINO, POPULATION_SIZE, ELITE_FRACTION,
    )
    from fitness_v2 import RobustCumulativeDisplacementFitness
    from evolution import rule_dict_to_lut, step_grid, center_of_mass


def _make_particle_grid(
    particle: list,
    grid_size: int = 128,
) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in particle:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid


def render_gif(frames: list, path: str, duration: int = 100) -> None:
    """Save a list of np.uint8 grids as an animated GIF using PIL."""
    from PIL import Image
    pil_frames = []
    for grid in frames:
        # Scale 0/1 grid to 0/255 and convert to RGB for visibility
        img_arr = (grid * 255).astype(np.uint8)
        img = Image.fromarray(img_arr, mode="L").convert("P")
        pil_frames.append(img)
    if pil_frames:
        pil_frames[0].save(
            path,
            save_all=True,
            append_images=pil_frames[1:],
            loop=0,
            duration=duration,
        )


def evolve_and_validate():
    OUTPUT_DIR = os.path.join(
        os.path.dirname(__file__), "..", "archive", "iter_202", "results"
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    GENERATIONS = 20
    GRID_SIZE = 128
    VALIDATION_STEPS = 512
    SEED_PARTICLE = L_TROMINO

    print("--- Starting Evolutionary Search ---")
    print(f"Generations: {GENERATIONS}, Population: {POPULATION_SIZE}")
    print(f"Fitness Function: RobustCumulativeDisplacementFitness")

    # --- 1. Run Evolution ---
    try:
        result = run_evolution(
            fitness_cls=RobustCumulativeDisplacementFitness,
            generations=GENERATIONS,
        )
    except Exception as e:
        print(f"An error occurred during evolution: {e}")
        report = {
            "status": "experiment_failed",
            "artifacts": [],
            "metrics": {},
            "log_excerpt": f"Evolution failed with error: {e}",
            "experimenter_view": "The evolutionary search process failed unexpectedly.",
            "notes": "Failed during run_evolution call.",
        }
        with open("experiment_report.yaml", "w") as f:
            yaml.dump(report, f)
        sys.exit(1)

    # --- 2. Identify Champion ---
    best_chrom = result["best_chrom"]
    best_fitness = result["best_fitness"]
    best_generation = result["best_generation"]
    best_metrics = result["best_metrics"]

    print(f"Evolution complete. Champion initial fitness: {best_fitness:.6f} @ gen {best_generation}")

    champion_rule = chromosome_to_rule_dict(
        np.asarray(best_chrom, dtype=np.uint8)
    )

    # --- 3. Save Champion Rule ---
    champion_path = os.path.join(OUTPUT_DIR, "champion_rule.json")
    payload = {
        "fitness_fn": "RobustCumulativeDisplacementFitness",
        "fitness": best_fitness,
        "generation": best_generation,
        "generations_run": result["generations_completed"],
        "metrics": best_metrics,
        "rule": {str(k): int(v) for k, v in champion_rule.items()},
        "chromosome": list(map(int, best_chrom)),
    }
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Champion rule saved to {champion_path}")

    # --- 4. Validate Champion (run for VALIDATION_STEPS, collect CoM history) ---
    print(f"--- Validating Champion Rule for {VALIDATION_STEPS} steps ---")
    lut = rule_dict_to_lut(champion_rule)
    grid = _make_particle_grid(SEED_PARTICLE, GRID_SIZE)

    initial_com = center_of_mass(grid)
    initial_bits = int(grid.sum())
    com_history = [initial_com]

    gif_sample_every = max(1, VALIDATION_STEPS // 64)
    gif_frames = [grid.copy()]

    for step in range(1, VALIDATION_STEPS + 1):
        grid = step_grid(grid, lut)
        com_history.append(center_of_mass(grid))
        if step % gif_sample_every == 0:
            gif_frames.append(grid.copy())

    final_com = com_history[-1]
    final_bits = int(grid.sum())

    dx = final_com[0] - initial_com[0]
    dy = final_com[1] - initial_com[1]
    displacement = math.sqrt(dx * dx + dy * dy)

    # Compute fitness the same way as RobustCumulativeDisplacementFitness
    if final_bits != initial_bits:
        final_fitness = 0.0
        conserved = False
    else:
        final_fitness = displacement / (1.0 + float(final_bits))
        conserved = True

    print(f"Validation run final fitness: {final_fitness:.6f}")
    print(f"Displacement: {displacement:.4f}  initial_bits={initial_bits}  final_bits={final_bits}")

    # --- 5. Generate GIF ---
    gif_path = os.path.join(OUTPUT_DIR, "champion.gif")
    try:
        render_gif(gif_frames, gif_path, duration=100)
        print(f"Validation GIF saved to {gif_path}")
    except Exception as e:
        print(f"GIF generation failed: {e}")
        gif_path = None

    # --- 6. Summarize Results ---
    summary_path = os.path.join(OUTPUT_DIR, "evolution_summary.txt")

    qualitative_desc = "Analysis of champion behavior:\n"
    if final_bits == 0:
        qualitative_desc += "- Annihilation: The pattern disappeared.\n"
    elif not conserved:
        qualitative_desc += (
            f"- Bit non-conserving: Mass changed from {initial_bits} to {final_bits}.\n"
        )
    else:
        qualitative_desc += "- Bit-conserving: Mass remained stable.\n"

    if displacement > 2.0:
        qualitative_desc += (
            f"- Movement: The pattern displaced by {displacement:.2f} units, "
            "indicating glider-like behavior."
        )
    else:
        qualitative_desc += "- Static: The pattern did not show significant movement."

    summary_content = (
        f"Evolution Run Summary (iter 202.4)\n"
        f"========================================\n"
        f"Generations: {GENERATIONS}\n"
        f"Population Size: {POPULATION_SIZE}\n"
        f"Fitness Function: RobustCumulativeDisplacementFitness\n\n"
        f"Champion Evolution Fitness ({result['generations_completed']} gens): {best_fitness:.6f}\n"
        f"Champion Validation Fitness ({VALIDATION_STEPS} steps): {final_fitness:.6f}\n\n"
        f"{qualitative_desc}\n"
    )
    with open(summary_path, "w") as f:
        f.write(summary_content)
    print(f"Summary written to {summary_path}")

    # --- 7. Final Report ---
    artifacts = [champion_path, summary_path]
    if gif_path:
        artifacts.append(gif_path)

    report = {
        "status": "ok",
        "artifacts": artifacts,
        "metrics": {
            "evolution_fitness": float(best_fitness),
            "validation_fitness": float(final_fitness),
            "displacement": float(displacement),
            "initial_bits": int(initial_bits),
            "final_bits": int(final_bits),
            "best_generation": int(best_generation),
        },
        "log_excerpt": (
            f"Champion evolution fitness: {best_fitness:.6f}\n"
            f"Champion validation fitness: {final_fitness:.6f}\n"
            f"Displacement: {displacement:.4f}\n"
            f"Bit conservation: {conserved}\n"
            f"Best generation: {best_generation}/{GENERATIONS}"
        ),
        "experimenter_view": summary_content,
        "notes": "Evolution and validation process completed successfully.",
    }
    with open("experiment_report.yaml", "w") as f:
        yaml.dump(report, f, default_flow_style=False, allow_unicode=True)

    print("\n--- Task Complete ---")


if __name__ == "__main__":
    evolve_and_validate()
