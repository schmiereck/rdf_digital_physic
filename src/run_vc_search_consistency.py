#!/usr/bin/env python3
"""
run_vc_search_consistency.py  -  Evolutionary search for v<c gliders using DisplacementConsistencyFitness.

Setup
-----
* Fitness     : DisplacementConsistencyFitness with num_windows=5 and max_bit_threshold=6
* Population  : 100 random C2-symmetric rules
* Generations : 20
* Seed        : 3-bit L-tromino seed [[63, 63], [64, 63], [64, 64]]
* Simulation  : 200 steps

Outputs (archive/iter_220/results/):
  champion_vc_rule_consistency.json    : champion rule + metrics
  trajectory_log.csv                   : generation,best_fitness,mean_fitness per generation
"""

from __future__ import annotations

import csv
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

# Ensure src/ is in the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import (
    generate_random_c2_rule,
    rule_dict_to_lut,
    step_grid,
)
from new_fitness import DisplacementConsistencyFitness

# ── Paths ─────────────────────────────────────────────────────────────────────

OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_220" / "results"
CHAMPION_JSON = OUTPUT_DIR / "champion_vc_rule_consistency.json"
TRAJECTORY_CSV = OUTPUT_DIR / "trajectory_log.csv"

# ── Search hyper-parameters ───────────────────────────────────────────────────

POPULATION_SIZE = 100
NUM_GENERATIONS = 20
ELITE_FRACTION = 0.10
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.01
LUT_SIZE = 128
RNG_SEED = 220
GRID_SIZE = 128
SIMULATION_STEPS = 200

ELITE_COUNT = max(2, int(POPULATION_SIZE * ELITE_FRACTION))

# 3-bit L-tromino seed coordinates
SEED_PARTICLE = [(63, 63), (64, 63), (64, 64)]


# ── Chromosome <-> rule_dict conversions ──────────────────────────────────────

def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


# ── Simulation + history collection ──────────────────────────────────────────

def simulate_with_history(rule_dict: dict) -> list[dict]:
    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_PARTICLE:
        grid[r, c] = 1

    def com_and_bits(g):
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return (0.0, 0.0), 0
        return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

    c0, b0 = com_and_bits(grid)
    hist = [{"step": 0, "com": c0, "bit_count": b0}]
    for t in range(1, SIMULATION_STEPS + 1):
        grid = step_grid(grid, lut)
        c, b = com_and_bits(grid)
        hist.append({"step": t, "com": c, "bit_count": b})
    return hist


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


def select_top_k(population: list[np.ndarray], fitnesses: list[float], k: int) -> list[np.ndarray]:
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Evolutionary search ────────────────────────────────────────────────────────

def run_search(fitness_fn) -> dict:
    print("=== Evolutionary Search (DisplacementConsistencyFitness) ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"  Population Size : {POPULATION_SIZE}")
    print(f"  Generations     : {NUM_GENERATIONS}")
    print(f"  Elite Count     : {ELITE_COUNT}")
    print(f"  Grid Size       : {GRID_SIZE}x{GRID_SIZE}")
    print(f"  Sim Steps       : {SIMULATION_STEPS}")
    print(f"  Seed Particle   : {SEED_PARTICLE}")
    print(f"  Max Bit Count   : {fitness_fn.max_bit_threshold}\n")

    # Initial random population of C2-symmetric rules
    population = [
        rule_dict_to_chromosome(generate_random_c2_rule(rng))
        for _ in range(POPULATION_SIZE)
    ]

    # Evaluate gen 0
    scores: list[float] = []
    for chrom in population:
        rd = chromosome_to_rule_dict(chrom)
        hist = simulate_with_history(rd)
        scores.append(fitness_fn(hist))

    best_idx        = int(np.argmax(scores))
    best_fitness    = float(scores[best_idx])
    best_chrom      = population[best_idx].copy()
    best_generation = 0
    max_ever        = best_fitness

    gen_log = [{
        "generation": 0,
        "best_fitness": best_fitness,
        "mean_fitness": float(np.mean(scores)),
    }]

    n_nonzero = sum(1 for f in scores if f > 0.0)
    print(
        f"  Gen  0: champion={best_fitness:.6f}  mean={np.mean(scores):.6f}"
        f"  non_zero={n_nonzero}"
    )

    for gen in range(1, NUM_GENERATIONS + 1):
        elite   = select_top_k(population, scores, ELITE_COUNT)
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

        population = new_pop[:POPULATION_SIZE]

        # Evaluate population
        scores = []
        for chrom in population:
            rd = chromosome_to_rule_dict(chrom)
            hist = simulate_with_history(rd)
            scores.append(fitness_fn(hist))

        gen_best_idx = int(np.argmax(scores))
        gen_best     = float(scores[gen_best_idx])
        gen_mean     = float(np.mean(scores))
        n_nonzero    = sum(1 for f in scores if f > 0.0)

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_chrom      = population[gen_best_idx].copy()
            best_generation = gen

        if best_fitness > max_ever:
            max_ever = best_fitness

        gen_log.append({
            "generation": gen,
            "best_fitness": gen_best,
            "mean_fitness": gen_mean,
        })

        print(
            f"  Gen {gen:2d}: champion={best_fitness:.6f}  gen_best={gen_best:.6f}"
            f"  mean={gen_mean:.6f}  non_zero={n_nonzero}"
        )

    return {
        "best_fitness":    best_fitness,
        "max_ever":        max_ever,
        "best_chrom":      best_chrom,
        "best_generation": best_generation,
        "gen_log":         gen_log,
        "fitness_function_name": fitness_fn.name,
    }


def main() -> int:
    fitness_fn = DisplacementConsistencyFitness(
        num_windows=5,
        max_bit_threshold=6,
    )

    t0 = time.time()
    result = run_search(fitness_fn)
    elapsed = time.time() - t0

    print(f"\n=== Search complete in {elapsed:.1f}s ===")

    # 1. Output champion_vc_rule_consistency.json
    rule_dict = chromosome_to_rule_dict(result["best_chrom"])
    payload = {
        "iteration":          "iter_220",
        "fitness_function":   result["fitness_function_name"],
        "fitness":            result["best_fitness"],
        "generation_of_best": result["best_generation"],
        "num_generations":    NUM_GENERATIONS,
        "population_size":    POPULATION_SIZE,
        "grid_size":          GRID_SIZE,
        "simulation_steps":   SIMULATION_STEPS,
        "seed_particle":      "L_TROMINO_3bit",
        "seed_cells":         SEED_PARTICLE,
        "elapsed_sec":        round(elapsed, 2),
        "rule_dict":          {str(k): int(v) for k, v in rule_dict.items()},
        "chromosome":         result["best_chrom"].tolist(),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHAMPION_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved champion rule JSON to: {CHAMPION_JSON}")

    # 2. Output trajectory log
    with open(TRAJECTORY_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["generation", "best_fitness", "mean_fitness"])
        writer.writeheader()
        for entry in result["gen_log"]:
            writer.writerow(entry)
    print(f"Saved trajectory log CSV to: {TRAJECTORY_CSV}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
