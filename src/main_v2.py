#!/usr/bin/env python3
"""
main_v2.py  —  Configurable evolutionary planner for v<c glider search.

Usage:
    python src/main_v2.py --fitness=SparseGliderFitness --generations=N
    python src/main_v2.py --fitness=CumulativeDisplacementFitness --generations=N

Writes results to archive/iter_200.4/results/.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import generate_random_c2_rule, rule_dict_to_lut
from fitness_v2 import SparseGliderFitness, CumulativeDisplacementFitness, T_TROMINO

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_200.4" / "results"

POPULATION_SIZE = 20
ELITE_FRACTION  = 0.20
CROSSOVER_RATE  = 0.80
MUTATION_RATE   = 0.01
LUT_SIZE        = 128
RNG_SEED        = 200_4

REGISTRY = {
    "SparseGliderFitness":          SparseGliderFitness,
    "CumulativeDisplacementFitness": CumulativeDisplacementFitness,
}


# ── Chromosome helpers ────────────────────────────────────────────────────────

def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Genetic operators ─────────────────────────────────────────────────────────

def two_point_crossover(p1: np.ndarray, p2: np.ndarray, rng: random.Random):
    n    = len(p1)
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


# ── Evolution loop ────────────────────────────────────────────────────────────

def run_evolution(fitness_cls, generations: int, rng_seed: int = RNG_SEED) -> dict:
    fitness_fn = fitness_cls()
    rng        = random.Random(rng_seed)
    elite_k    = max(2, int(POPULATION_SIZE * ELITE_FRACTION))

    print(f"=== Evolution: {fitness_fn.name} ===")
    print(f"  generations={generations}  population={POPULATION_SIZE}  elite={elite_k}")
    print(f"  crossover_rate={CROSSOVER_RATE}  mutation_rate={MUTATION_RATE}")

    # Initial population
    population = [
        rule_dict_to_chromosome(generate_random_c2_rule(rng))
        for _ in range(POPULATION_SIZE)
    ]

    stats_log: list[dict] = []
    best_fitness    = -1.0
    best_chrom      = None
    best_metrics    = None
    best_generation = -1

    def evaluate_all(pop):
        fits, mets = [], []
        for chrom in pop:
            rule_dict = chromosome_to_rule_dict(chrom)
            # This is the critical call: fitness_fn(rule_dict) must return (float, dict).
            # The bugfix in fitness_v2.py ensures __call__ returns a 2-tuple, not a dict.
            fitness, metrics = fitness_fn(rule_dict)
            fits.append(fitness)
            mets.append(metrics)
        return fits, mets

    fitnesses, metrics_l = evaluate_all(population)
    gen_best_idx = int(np.argmax(fitnesses))
    best_fitness    = float(fitnesses[gen_best_idx])
    best_chrom      = population[gen_best_idx].copy()
    best_metrics    = metrics_l[gen_best_idx]
    best_generation = 0

    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    stats_log.append({
        "generation": 0, "max": best_fitness,
        "mean": float(np.mean(fitnesses)), "non_zero": n_nonzero,
    })
    print(f"  Gen  0: max={best_fitness:.6f}  mean={stats_log[-1]['mean']:.6f}  "
          f"non_zero={n_nonzero}/{POPULATION_SIZE}")

    for gen in range(1, generations + 1):
        elite   = select_top_k(population, fitnesses, elite_k)
        new_pop = [e.copy() for e in elite]
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = rng.sample(elite, 2)
            if rng.random() < CROSSOVER_RATE:
                c1, c2 = two_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            new_pop.append(per_bit_mutation(c1, MUTATION_RATE, rng))
            if len(new_pop) < POPULATION_SIZE:
                new_pop.append(per_bit_mutation(c2, MUTATION_RATE, rng))

        population = new_pop
        fitnesses, metrics_l = evaluate_all(population)
        gen_best_idx = int(np.argmax(fitnesses))
        gen_best     = float(fitnesses[gen_best_idx])

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_chrom      = population[gen_best_idx].copy()
            best_metrics    = metrics_l[gen_best_idx]
            best_generation = gen

        n_nonzero = sum(1 for f in fitnesses if f > 0.0)
        stats_log.append({
            "generation": gen, "max": gen_best,
            "mean": float(np.mean(fitnesses)), "non_zero": n_nonzero,
        })
        print(f"  Gen {gen:2d}: max={gen_best:.6f}  mean={stats_log[-1]['mean']:.6f}  "
              f"non_zero={n_nonzero}/{POPULATION_SIZE}  "
              f"best_so_far={best_fitness:.6f}@gen{best_generation}")

    return {
        "best_fitness":    float(best_fitness),
        "best_chrom":      best_chrom,
        "best_metrics":    best_metrics,
        "best_generation": best_generation,
        "stats":           stats_log,
        "generations_completed": generations,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Evolutionary glider search")
    p.add_argument("--fitness",     default="SparseGliderFitness",
                   help="Fitness class name (default: SparseGliderFitness)")
    p.add_argument("--generations", type=int, default=10,
                   help="Number of generations (default: 10)")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.fitness not in REGISTRY:
        print(f"Unknown fitness function: {args.fitness!r}. "
              f"Available: {list(REGISTRY)}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    t0     = time.time()
    result = run_evolution(REGISTRY[args.fitness], generations=args.generations)
    elapsed = time.time() - t0

    print(f"\n=== Run complete in {elapsed:.1f}s ===")
    print(f"  Best fitness   : {result['best_fitness']:.6f}")
    print(f"  Best generation: {result['best_generation']}")
    print(f"  Generations completed: {result['generations_completed']}")

    champ_rule = chromosome_to_rule_dict(
        np.asarray(result["best_chrom"], dtype=np.uint8)
    )

    champion_path = OUTPUT_DIR / "champion_rule.json"
    payload = {
        "fitness_fn":         args.fitness,
        "fitness":            result["best_fitness"],
        "generation":         result["best_generation"],
        "generations_run":    result["generations_completed"],
        "metrics":            result["best_metrics"],
        "rule":               {str(k): int(v) for k, v in champ_rule.items()},
        "chromosome":         list(map(int, result["best_chrom"])),
        "elapsed_sec":        round(elapsed, 2),
    }
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved champion : {champion_path}")

    stats_path = OUTPUT_DIR / "generation_stats.json"
    with open(stats_path, "w") as f:
        json.dump(result["stats"], f, indent=2)
    print(f"Saved stats    : {stats_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
