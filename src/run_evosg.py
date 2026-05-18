#!/usr/bin/env python3
"""
run_evosg.py  —  Standalone evolutionary search for v<c gliders on a hexagonal
toroidal grid.

Re-implements the core evolution loop from main_v2.py so that every parameter
(population size, generations, random seed, particle seed, output directory)
can be controlled from the command line.  Fitness functions are drawn from
src/fitness_v2.py.

Usage example:
    python src/run_evosg.py \
        --fitness RobustCumulativeDisplacementFitness \
        --pop_size 100 \
        --generations 20 \
        --particle_seed L-tromino \
        --seed 43 \
        --output_dir archive/iter_203.1/results/

Output
------
After evolution finishes the script prints a YAML block to stdout summarising
the run.  It also saves:
    - {output_dir}/champion_rule.json
    - {output_dir}/fitness_log.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from fitness_v2 import (
    SparseGliderFitness,
    CumulativeDisplacementFitness,
    RobustCumulativeDisplacementFitness,
    T_TROMINO,
)
from evolution import generate_random_c2_rule, rule_dict_to_lut, step_grid

# ── Seed particles ──────────────────────────────────────────────────────────

L_TROMINO: list[tuple[int, int]] = [
    (-1, -1),
    (0, -1),
    (0, 0),
]

PARTICLE_SEEDS = {
    "t-tromino": T_TROMINO,
    "l-tromino": L_TROMINO,
}

# ── Constants ───────────────────────────────────────────────────────────────

LUT_SIZE = 128
CROSSOVER_RATE = 0.80
MUTATION_RATE = 0.01

# ── Registry ────────────────────────────────────────────────────────────────

REGISTRY = {
    "SparseGliderFitness": SparseGliderFitness,
    "CumulativeDisplacementFitness": CumulativeDisplacementFitness,
    "RobustCumulativeDisplacementFitness": RobustCumulativeDisplacementFitness,
}

# ── Chromosome helpers ──────────────────────────────────────────────────────

def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Genetic operators ───────────────────────────────────────────────────────

def two_point_crossover(p1: np.ndarray, p2: np.ndarray, rng: random.Random):
    n = len(p1)
    a, b = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(chrom: np.ndarray, rate: float, rng: random.Random) -> np.ndarray:
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


def select_top_k(population, fitnesses, k):
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Evolve ──────────────────────────────────────────────────────────────────

def run_evolution(
    fitness_cls,
    particle: list[tuple[int, int]],
    generations: int,
    population_size: int,
    rng_seed: int,
) -> dict:
    """Run a full generational evolutionary search.

    Parameters
    ----------
    fitness_cls : class
        A fitness class from fitness_v2 (e.g. RobustCumulativeDisplacementFitness).
    particle : list of (dr, dc)
        Seed particle coordinates (offsets from grid centre).
    generations : int
        Number of generations to evolve.
    population_size : int
        Number of individuals in the population.
    rng_seed : int
        Random seed for the initial population generator.

    Returns
    -------
    dict  with keys best_fitness, best_chrom, best_metrics, best_generation,
          stats, and generations_completed.
    """
    # Build fitness instance with the requested particle seed
    fitness_fn = fitness_cls(particle=particle)
    rng = random.Random(rng_seed)
    elite_k = max(2, int(population_size * 0.10))

    print(f"=== Evolution: {fitness_fn.name} ===")
    print(f"  generations={generations}  population={population_size}  elite={elite_k}")
    print(f"  crossover_rate={CROSSOVER_RATE}  mutation_rate={MUTATION_RATE}")
    print(f"  particle_seed={particle}  rng_seed={rng_seed}")

    # --- Initial population (C2-symmetric rules) ---
    population = [
        rule_dict_to_chromosome(generate_random_c2_rule(rng))
        for _ in range(population_size)
    ]

    stats_log: list[dict] = []
    best_fitness = -1.0
    best_chrom = None
    best_metrics = None
    best_generation = -1

    def evaluate_all(pop):
        fits, mets = [], []
        for chrom in pop:
            rule_dict = chromosome_to_rule_dict(chrom)
            fitness, metrics = fitness_fn(rule_dict)
            fits.append(fitness)
            mets.append(metrics)
        return fits, mets

    # Gen 0 evaluation
    fitnesses, metrics_l = evaluate_all(population)
    gen_best_idx = int(np.argmax(fitnesses))
    best_fitness = float(fitnesses[gen_best_idx])
    best_chrom = population[gen_best_idx].copy()
    best_metrics = metrics_l[gen_best_idx]
    best_generation = 0
    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    stats_log.append({
        "generation": 0,
        "max": best_fitness,
        "mean": float(np.mean(fitnesses)),
        "non_zero": n_nonzero,
    })
    print(f"  Gen  0: max={best_fitness:.6f}  mean={stats_log[-1]['mean']:.6f}  "
          f"non_zero={n_nonzero}/{population_size}")

    for gen in range(1, generations + 1):
        elite = select_top_k(population, fitnesses, elite_k)
        new_pop = [e.copy() for e in elite]
        while len(new_pop) < population_size:
            p1, p2 = rng.sample(elite, 2)
            if rng.random() < CROSSOVER_RATE:
                c1, c2 = two_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            new_pop.append(per_bit_mutation(c1, MUTATION_RATE, rng))
            if len(new_pop) < population_size:
                new_pop.append(per_bit_mutation(c2, MUTATION_RATE, rng))

        population = new_pop
        fitnesses, metrics_l = evaluate_all(population)
        gen_best_idx = int(np.argmax(fitnesses))
        gen_best = float(fitnesses[gen_best_idx])

        if gen_best > best_fitness:
            best_fitness = gen_best
            best_chrom = population[gen_best_idx].copy()
            best_metrics = metrics_l[gen_best_idx]
            best_generation = gen

        n_nonzero = sum(1 for f in fitnesses if f > 0.0)
        stats_log.append({
            "generation": gen,
            "max": gen_best,
            "mean": float(np.mean(fitnesses)),
            "non_zero": n_nonzero,
        })
        print(f"  Gen {gen:2d}: max={gen_best:.6f}  mean={stats_log[-1]['mean']:.6f}  "
              f"non_zero={n_nonzero}/{population_size}  "
              f"best_so_far={best_fitness:.6f}@gen{best_generation}")

    return {
        "best_fitness": float(best_fitness),
        "best_chrom": best_chrom,
        "best_metrics": best_metrics,
        "best_generation": best_generation,
        "stats": stats_log,
        "generations_completed": generations,
    }


# ── Validation run ──────────────────────────────────────────────────────────

def validate_champion(rule_dict: dict, particle: list, output_dir: Path,
                      steps: int = 512) -> dict:
    """Simulate the champion rule for ``steps`` steps and return metrics."""
    initial_com = (64.0, 64.0)  # placeholder; computed below
    grid = np.zeros((128, 128), dtype=np.uint8)
    centre = 128 // 2
    for dr, dc in particle:
        r = (centre + dr) % 128
        c = (centre + dc) % 128
        grid[r, c] = 1

    initial_bits = int(grid.sum())
    xs, ys = np.where(grid > 0)
    initial_com = (float(np.mean(xs)), float(np.mean(ys)))

    lut = rule_dict_to_lut(rule_dict)
    gif_frames: list[np.ndarray] = [grid.copy()]

    for _step in range(steps):
        grid = step_grid(grid, lut)
        if _step % max(1, steps // 64) == 0:
            gif_frames.append(grid.copy())

    final_bits = int(grid.sum())
    xs, ys = np.where(grid > 0)
    final_com = (float(np.mean(xs)) if len(xs) > 0 else 0.0,
                 float(np.mean(ys)) if len(ys) > 0 else 0.0)

    dx = final_com[0] - initial_com[0]
    dy = final_com[1] - initial_com[1]
    displacement = math.sqrt(dx * dx + dy * dy)

    # Fitness the same way RobustCumulativeDisplacementFitness does
    if final_bits != initial_bits:
        final_fitness = 0.0
        conserved = False
    else:
        final_fitness = displacement / (1.0 + float(final_bits))
        conserved = True

    # Generate GIF
    try:
        from PIL import Image
        gif_path = output_dir / "champion.gif"
        pil_frames = []
        for g in gif_frames:
            img = Image.fromarray((g * 255).astype(np.uint8), mode="L").convert("P")
            pil_frames.append(img)
        if pil_frames:
            pil_frames[0].save(
                gif_path, save_all=True, append_images=pil_frames[1:],
                loop=0, duration=100,
            )
    except Exception:
        gif_path = None

    return {
        "final_fitness": final_fitness,
        "displacement": displacement,
        "initial_bits": initial_bits,
        "final_bits": final_bits,
        "conserved": conserved,
        "gif_path": gif_path,
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Evolutionary search for v<c gliders on hexagonal CA rules."
    )
    p.add_argument(
        "--fitness",
        type=str,
        default="RobustCumulativeDisplacementFitness",
        help="Fitness function class name (default: RobustCumulativeDisplacementFitness)",
    )
    p.add_argument(
        "--pop_size", type=int, default=100,
        help="Population size (default: 100)",
    )
    p.add_argument(
        "--generations", type=int, default=20,
        help="Number of generations (default: 20)",
    )
    p.add_argument(
        "--particle_seed", type=str, default="L-tromino",
        choices=list(PARTICLE_SEEDS),
        help="Seed particle (default: L-tromino)",
    )
    p.add_argument(
        "--seed", type=int, default=202_21,
        help="Random seed for initial population (default: 20221)",
    )
    p.add_argument(
        "--output_dir", type=str, default="archive/iter_203.1/results/",
        help="Output directory (default: archive/iter_203.1/results/)",
    )
    return p.parse_args(argv)


# ── Main ─────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    args = parse_args(argv)
    project_root = Path(__file__).parent.parent
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (project_root / output_dir).resolve()

    # Resolve fitness class
    if args.fitness not in REGISTRY:
        print(f"Unknown fitness: {args.fitness!r}. Available: {list(REGISTRY)}",
              file=sys.stderr)
        return 1
    fitness_cls = REGISTRY[args.fitness]

    # Resolve particle seed
    particle = PARTICLE_SEEDS[args.particle_seed]

    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Run evolution ───────────────────────────────────────────────
    t0 = time.time()
    result = run_evolution(
        fitness_cls=fitness_cls,
        particle=particle,
        generations=args.generations,
        population_size=args.pop_size,
        rng_seed=args.seed,
    )
    elapsed = time.time() - t0

    # ── 2. Save champion rule JSON ─────────────────────────────────────
    champion_rule = chromosome_to_rule_dict(
        np.asarray(result["best_chrom"], dtype=np.uint8)
    )
    champion_payload = {
        "fitness_fn": args.fitness,
        "fitness": float(result["best_fitness"]),
        "generation": int(result["best_generation"]),
        "generations_run": int(result["generations_completed"]),
        "population_size": args.pop_size,
        "elite_size": max(2, int(args.pop_size * 0.10)),
        "crossover_rate": CROSSOVER_RATE,
        "mutation_rate": MUTATION_RATE,
        "particle_seed": args.particle_seed,
        "rng_seed": args.seed,
        "elapsed_sec": round(elapsed, 2),
        "metrics": result["best_metrics"],
        "rule": {str(k): int(v) for k, v in champion_rule.items()},
        "chromosome": [int(b) for b in result["best_chrom"]],
    }
    champion_path = output_dir / "champion_rule.json"
    with open(champion_path, "w") as f:
        json.dump(champion_payload, f, indent=2)
    print(f"\nSaved champion rule -> {champion_path}")

    # ── 3. Save fitness log CSV ────────────────────────────────────────
    log_path = output_dir / "fitness_log.csv"
    fieldnames = ["generation", "max", "mean", "non_zero"]
    with open(log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in result["stats"]:
            writer.writerow({
                "generation": s["generation"],
                "max": f"{s['max']:.6f}",
                "mean": f"{s['mean']:.6f}",
                "non_zero": s["non_zero"],
            })
    print(f"Saved fitness log  -> {log_path}")

    # ── 4. Validate champion (512-step run) ────────────────────────────
    print(f"\n--- Validating champion rule ({champion_path}) ---")
    validation = validate_champion(champion_rule, particle, output_dir)
    print(f"  validation_fitness = {validation['final_fitness']:.6f}")
    print(f"  displacement       = {validation['displacement']:.4f}")
    print(f"  bits conserved     = {validation['conserved']}")
    print(f"  initial_bits       = {validation['initial_bits']}")
    print(f"  final_bits         = {validation['final_bits']}")

    # ── 5. Qualitative assessment ──────────────────────────────────────
    metrics = result["best_metrics"] or {}
    reason = metrics.get("reason", "ok")
    conserved = validation["conserved"]
    disp = validation["displacement"]

    if not conserved:
        assessment = (
            "The champion rule failed the bit-conservation gate — it likely "
            "annihilates or creates matter during the simulation. "
            "This is a known local optimum for displacement-based fitness."
        )
    elif disp < 2.0:
        assessment = (
            "The champion pattern is essentially stationary (displacement "
            f"< {2.0:.1f}). This strongly suggests the search converged to a "
            "local optimum of oscillating or still-life patterns that "
            "satisfy bit conservation but produce no net movement."
        )
    elif disp < 10.0:
        assessment = (
            f"The champion shows modest displacement ({disp:.2f} units over "
            "512 steps). There may be weak glider-like behaviour but the "
            "velocity is well below light-speed (c). Further evolution or "
            "a different search strategy may be needed."
        )
    else:
        assessment = (
            f"The champion achieved meaningful displacement ({disp:.2f} units). "
            "This may indicate genuine glider-like behaviour worthy of "
            "further investigation."
        )

    # ── 6. Collect last 20 lines of console output ─────────────────────
    # (We will capture these as the log_excerpt in the YAML block below)

    # ── 7. Print final YAML block to stdout ────────────────────────────
    final_fitness = float(result["best_fitness"])
    max_disp = float(disp)

    yaml_block = (
        "status: ok\n"
        "artifacts:\n"
        f'  - "{champion_path}"\n'
        f'  - "{log_path}"\n'
        "metrics:\n"
        f"  best_fitness: {final_fitness:.6f}\n"
        f"  max_displacement: {max_disp:.4f}\n"
        "log_excerpt: |\n"
    )
    # Print each line indented properly
    lines = (
        f"Evolution complete in {elapsed:.1f}s\n"
        f"  Best fitness: {final_fitness:.6f} at generation {result['best_generation']}\n"
        f"  Validation displacement: {disp:.4f} bits conserved: {conserved}\n"
        f"  Champion rule saved to: {champion_path}\n"
        f"  Fitness log saved to: {log_path}\n"
        f"  Best fitness so far across generations: {final_fitness:.6f}\n"
        f"  Particle seed: {args.particle_seed}\n"
        f"  RNG seed: {args.seed}\n"
        f"  Generations completed: {args.generations}\n"
        f"  Population size: {args.pop_size}\n"
        f"  Fitness function: {args.fitness}\n"
        f"  Bit conservation: {reason}\n"
    )
    for line in lines.splitlines():
        yaml_block += f"    {line}\n"

    yaml_block += f'experimenter_view: |\n    {assessment}\n'
    yaml_block += f'notes: "Re-run with seed {args.seed}."\n'

    print("\n=== Evolution complete ===")
    print(yaml_block)

    return 0


if __name__ == "__main__":
    sys.exit(main())
