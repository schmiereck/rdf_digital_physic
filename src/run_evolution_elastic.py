#!/usr/bin/env python3
"""
run_evolution_elastic.py  —  iter_187 evolutionary search for elastic-collision rules.

Goal
----
Evolve a C2-symmetric CA rule whose two L-tromino gliders bounce elastically
off each other, rather than annihilating or fusing on contact.  Fitness is
``CollisionFitness`` from ``fitness_functions.py`` and an ideal score is 1.0.

Genetic algorithm
-----------------
  * Chromosome           : 128-bit center-output LUT (same as iter_179)
  * Population size      : 100
  * Generations          : 10
  * Selection            : top 10 percent elitism (the 10 best survive each
                           generation and are used as parents for the new
                           offspring).
  * Crossover            : two-point crossover, applied with probability 0.8.
  * Mutation             : per-bit bit-flip mutation, rate 0.01.
  * Initial population   : 100 random C2-symmetric rules with 8 kernel pairs.

Outputs
-------
  * Best rule kernel definition (rule_dict + chromosome + score) is written to
    ``archive/iter_187/results/best_elastic_rule.json``.
  * Per-generation max fitness is printed to stdout.
"""

from __future__ import annotations

import concurrent.futures
import json
import random
import sys
from pathlib import Path

import numpy as np

# Ensure src/ is importable when run as a script
sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule
from fitness_functions import CollisionFitness


# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_187" / "results"
BEST_RULE    = OUTPUT_DIR / "best_elastic_rule.json"


# ── GA hyper-parameters ─────────────────────────────────────────────────────

POPULATION_SIZE = 100
NUM_GENERATIONS = 10
ELITE_FRACTION  = 0.10           # top-10% selection
DENSITY         = 8              # C2 kernel pairs per random seed rule
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.01
LUT_SIZE        = 128
RNG_SEED        = 187_001
MAX_WORKERS     = 4

ELITE_COUNT = max(2, int(POPULATION_SIZE * ELITE_FRACTION))


# ── Chromosome <-> rule_dict conversions (same encoding as iter_179) ────────

def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    """Convert a rule_dict to its 128-bit center-output chromosome.

    Each entry in the chromosome is the *output center bit* for one of the
    128 possible neighbourhood states. The default (no override) value for
    state ``s`` is ``(s >> 6) & 1`` -- i.e. the identity rule keeps the
    current center cell.
    """
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    """Convert a 128-bit chromosome back to a sparse rule_dict.

    Only non-identity entries are stored.  Following the iter_179 convention
    the low six bits of the stored output value are copied from the input
    state (they are ignored by the simulator, which only reads bit 6).
    """
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


# ── Initial population: random C2-symmetric rules ───────────────────────────

def generate_c2_rule_density(
    rng: random.Random, density: int = DENSITY, max_attempts: int = 10_000,
) -> dict:
    """Generate a C2-symmetric rule with exactly ``density`` kernel pairs."""
    for _ in range(max_attempts):
        pairs = []
        for _ in range(density):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate C2 rule with density {density}")


# ── Fitness evaluation (process-pool parallel) ──────────────────────────────

_FITNESS = CollisionFitness()


def _eval_worker(task: tuple) -> tuple:
    """Worker entry point: evaluate one chromosome and return (idx, fitness, metrics)."""
    idx, chrom_list = task
    chrom     = np.asarray(chrom_list, dtype=np.uint8)
    rule_dict = chromosome_to_rule_dict(chrom)
    metrics   = _FITNESS.evaluate(rule_dict)
    return idx, float(metrics["fitness"]), metrics


def evaluate_population(population: list) -> tuple[list, list]:
    """Evaluate every chromosome in parallel.

    Returns ``(fitnesses, metrics)`` where ``metrics[i]`` is the full result
    dict produced by ``CollisionFitness.evaluate``.
    """
    n         = len(population)
    fitnesses = [0.0] * n
    metrics_l = [None] * n
    tasks     = [(i, chrom.tolist()) for i, chrom in enumerate(population)]

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_eval_worker, t): t[0] for t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            idx, fitness, metrics = fut.result()
            fitnesses[idx] = fitness
            metrics_l[idx] = metrics

    return fitnesses, metrics_l


# ── Genetic operators ───────────────────────────────────────────────────────

def two_point_crossover(
    p1: np.ndarray, p2: np.ndarray, rng: random.Random,
) -> tuple[np.ndarray, np.ndarray]:
    n      = len(p1)
    a, b   = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(
    chrom: np.ndarray, rate: float, rng: random.Random,
) -> np.ndarray:
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


def select_top_k(population: list, fitnesses: list, k: int) -> list:
    """Return the top-``k`` chromosomes ranked by fitness (descending)."""
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Main loop ───────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print("=== iter_187 — Elastic-Collision Evolution ===")
    print(
        f"Population: {POPULATION_SIZE}  Generations: {NUM_GENERATIONS}  "
        f"Density: {DENSITY}"
    )
    print(
        f"Elite: top {ELITE_COUNT} ({ELITE_FRACTION:.0%})  "
        f"Crossover: {CROSSOVER_RATE}  Mutation: {MUTATION_RATE}/bit"
    )
    print(f"Fitness: CollisionFitness (ideal=1.0)\n")

    # ── Generation 0: random C2 rules ──
    print("Generating initial population ...")
    population = [
        rule_dict_to_chromosome(generate_c2_rule_density(rng, density=DENSITY))
        for _ in range(POPULATION_SIZE)
    ]

    print(f"Evaluating generation 0 ({POPULATION_SIZE} rules) ...")
    fitnesses, metrics_l = evaluate_population(population)

    best_idx       = int(np.argmax(fitnesses))
    best_fitness   = float(fitnesses[best_idx])
    best_chrom     = population[best_idx].copy()
    best_metrics   = metrics_l[best_idx]
    best_generation = 0

    print(
        f"  Gen 0:  best={best_fitness:.6f}  "
        f"mean={float(np.mean(fitnesses)):.6f}  "
        f"non_zero={sum(1 for f in fitnesses if f > 0.0)}"
    )

    # ── Evolution loop ──
    for gen in range(1, NUM_GENERATIONS + 1):
        elite = select_top_k(population, fitnesses, ELITE_COUNT)

        # New population: keep elites verbatim; fill the rest with offspring
        # whose parents are sampled from the elites.
        new_pop = [e.copy() for e in elite]
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = rng.sample(elite, 2)
            if rng.random() < CROSSOVER_RATE:
                c1, c2 = two_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            c1 = per_bit_mutation(c1, MUTATION_RATE, rng)
            c2 = per_bit_mutation(c2, MUTATION_RATE, rng)
            new_pop.append(c1)
            if len(new_pop) < POPULATION_SIZE:
                new_pop.append(c2)

        population = new_pop
        fitnesses, metrics_l = evaluate_population(population)

        gen_best_idx = int(np.argmax(fitnesses))
        gen_best     = float(fitnesses[gen_best_idx])
        gen_mean     = float(np.mean(fitnesses))

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_chrom      = population[gen_best_idx].copy()
            best_metrics    = metrics_l[gen_best_idx]
            best_generation = gen

        print(
            f"  Gen {gen:2d}: best={gen_best:.6f}  mean={gen_mean:.6f}  "
            f"non_zero={sum(1 for f in fitnesses if f > 0.0)}"
        )

    # ── Persist best rule ────────────────────────────────────────────────
    best_rule_dict = chromosome_to_rule_dict(best_chrom)
    payload = {
        "iteration":           "iter_187",
        "fitness":             best_fitness,
        "generation_of_best":  best_generation,
        "num_generations":     NUM_GENERATIONS,
        "population_size":     POPULATION_SIZE,
        "elite_count":         ELITE_COUNT,
        "crossover_rate":      CROSSOVER_RATE,
        "mutation_rate":       MUTATION_RATE,
        "rng_seed":            RNG_SEED,
        "metrics":             best_metrics,
        "rule_dict":           {str(k): int(v) for k, v in best_rule_dict.items()},
        "chromosome":          best_chrom.tolist(),
    }
    with open(BEST_RULE, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nBest fitness: {best_fitness:.6f} (generation {best_generation})")
    print(f"Saved best rule: {BEST_RULE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
