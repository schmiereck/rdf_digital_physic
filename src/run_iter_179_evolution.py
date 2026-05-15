#!/usr/bin/env python3
"""
run_iter_179_evolution.py — iter_179.3 evolutionary search using CheckpointFitness.

Initial population: 100 random C2-symmetric rules, each with 8 kernel pairs.
GA operators (applied on the 128-bit center-output LUT chromosome):
  - tournament selection (k=4)
  - two-point crossover (rate 0.8)
  - per-bit mutation (rate 0.01)
Fitness: CheckpointFitness on the L-tromino seed with checkpoints
  [50, 100, 150, 200] over 200 simulation steps.

Outputs:
  archive/iter_179/results/evolution_log.csv
  archive/iter_179/results/final_population.json
"""

import concurrent.futures
import csv
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule

PROJECT_ROOT     = Path(__file__).parent.parent
OUTPUT_DIR       = PROJECT_ROOT / "archive" / "iter_179" / "results"
EVOLUTION_LOG    = OUTPUT_DIR / "evolution_log.csv"
FINAL_POPULATION = OUTPUT_DIR / "final_population.json"

POPULATION_SIZE  = 100
NUM_GENERATIONS  = 10
DENSITY          = 8
TOURNAMENT_SIZE  = 4
CROSSOVER_RATE   = 0.8
MUTATION_RATE    = 0.01
GRID_SIZE        = 128
LUT_SIZE         = 128
TOTAL_STEPS      = 200
CHECKPOINTS      = {50, 100, 150, 200}
LTROMINO_CELLS   = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS     = len(LTROMINO_CELLS)
RNG_SEED         = 179_003
MAX_WORKERS      = 4


# ── C2 rule generation with fixed density ─────────────────────────────────────

def generate_c2_rule_density(rng: random.Random, density: int = DENSITY,
                              max_attempts: int = 10_000) -> dict:
    """Generate a C2-symmetric rule with exactly *density* kernel pairs."""
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


# ── Chromosome <-> rule_dict ──────────────────────────────────────────────────

def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    """Convert a rule_dict to its 128-bit center-output LUT chromosome.

    Default (identity) entries map state s -> output center bit = (s >> 6) & 1.
    """
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    """Convert a 128-bit chromosome back to a rule_dict.

    Only non-identity entries are recorded (entries where the output center
    differs from the input center).  The remaining low 6 bits are copied from
    the input state -- they have no effect on simulation since the simulator
    only reads bit 6 of the output value.
    """
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


# ── Simulation primitives ─────────────────────────────────────────────────────

def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
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


def evaluate_chromosome(chrom_list: list) -> float:
    """CheckpointFitness on the L-tromino seed.

    Returns the centre-of-mass displacement after TOTAL_STEPS steps, or 0.0
    if any checkpoint detects a bit-count change from INITIAL_BITS.
    """
    lut  = np.asarray(chrom_list, dtype=np.uint8)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1
    initial_com = center_of_mass(grid)

    for step in range(1, TOTAL_STEPS + 1):
        grid = step_grid(grid, lut)
        if step in CHECKPOINTS and int(grid.sum()) != INITIAL_BITS:
            return 0.0

    final_com = center_of_mass(grid)
    dx = final_com[0] - initial_com[0]
    dy = final_com[1] - initial_com[1]
    return math.sqrt(dx * dx + dy * dy)


def _eval_worker(task: tuple) -> tuple:
    idx, chrom_list = task
    return idx, evaluate_chromosome(chrom_list)


def evaluate_population(population: list) -> list:
    """Evaluate every chromosome in *population* using a process pool."""
    n         = len(population)
    fitnesses = [0.0] * n
    tasks     = [(i, chrom.tolist()) for i, chrom in enumerate(population)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_eval_worker, t): t[0] for t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            idx, fitness = fut.result()
            fitnesses[idx] = float(fitness)
    return fitnesses


# ── Genetic operators ─────────────────────────────────────────────────────────

def tournament_select(population, fitnesses, k, rng):
    indices = rng.sample(range(len(population)), k)
    best    = max(indices, key=lambda i: fitnesses[i])
    return population[best].copy()


def two_point_crossover(p1: np.ndarray, p2: np.ndarray, rng: random.Random):
    n      = len(p1)
    a, b   = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(chrom: np.ndarray, rate: float, rng: random.Random):
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"=== iter_179.3 — CheckpointFitness Evolution ===")
    print(f"Population: {POPULATION_SIZE}  Generations: {NUM_GENERATIONS}  "
          f"Density: {DENSITY}")
    print(f"Tournament k={TOURNAMENT_SIZE}  Crossover={CROSSOVER_RATE}  "
          f"Mutation={MUTATION_RATE}/bit")
    print(f"Checkpoints={sorted(CHECKPOINTS)}  TotalSteps={TOTAL_STEPS}")
    print(f"Seed: L-tromino at {LTROMINO_CELLS}\n")

    rng = random.Random(RNG_SEED)

    # ── Generation 0: random C2 rules with density=8 ──
    print("Generating initial population ...")
    population = []
    for _ in range(POPULATION_SIZE):
        rd = generate_c2_rule_density(rng, density=DENSITY)
        population.append(rule_dict_to_chromosome(rd))

    print(f"Evaluating generation 0 ({POPULATION_SIZE} rules) ...")
    fitnesses = evaluate_population(population)

    gen0_max  = float(np.max(fitnesses))
    gen0_mean = float(np.mean(fitnesses))
    log_rows  = [{
        "generation":   0,
        "max_fitness":  gen0_max,
        "mean_fitness": gen0_mean,
    }]
    print(f"  Gen 0: max={gen0_max:.6f}  mean={gen0_mean:.6f}  "
          f"non_zero={sum(1 for f in fitnesses if f > 0.0)}")

    best_fitness_found  = gen0_max
    generation_of_best  = 0
    best_chrom          = population[int(np.argmax(fitnesses))].copy()

    # ── Evolution loop ──
    for gen in range(1, NUM_GENERATIONS + 1):
        new_pop = []
        while len(new_pop) < POPULATION_SIZE:
            p1 = tournament_select(population, fitnesses, TOURNAMENT_SIZE, rng)
            p2 = tournament_select(population, fitnesses, TOURNAMENT_SIZE, rng)
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
        fitnesses  = evaluate_population(population)

        gen_max  = float(np.max(fitnesses))
        gen_mean = float(np.mean(fitnesses))
        log_rows.append({
            "generation":   gen,
            "max_fitness":  gen_max,
            "mean_fitness": gen_mean,
        })

        if gen_max > best_fitness_found:
            best_fitness_found = gen_max
            generation_of_best = gen
            best_chrom         = population[int(np.argmax(fitnesses))].copy()

        print(f"  Gen {gen:2d}: max={gen_max:.6f}  mean={gen_mean:.6f}  "
              f"non_zero={sum(1 for f in fitnesses if f > 0.0)}")

    # ── Persist evolution log ──
    with open(EVOLUTION_LOG, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["generation", "max_fitness", "mean_fitness"])
        for row in log_rows:
            writer.writerow([
                row["generation"],
                f"{row['max_fitness']:.10f}",
                f"{row['mean_fitness']:.10f}",
            ])
    print(f"\nSaved evolution log: {EVOLUTION_LOG}")

    # ── Persist final population ──
    order = np.argsort(fitnesses)[::-1]
    final_pop_data = {
        "generation":           NUM_GENERATIONS,
        "population_size":      POPULATION_SIZE,
        "best_fitness_found":   best_fitness_found,
        "generation_of_best":   generation_of_best,
        "tournament_size":      TOURNAMENT_SIZE,
        "crossover_rate":       CROSSOVER_RATE,
        "mutation_rate":        MUTATION_RATE,
        "total_steps":          TOTAL_STEPS,
        "checkpoints":          sorted(CHECKPOINTS),
        "ltromino_cells":       LTROMINO_CELLS,
        "rng_seed":             RNG_SEED,
        "population": [
            {
                "rule_id":    f"g{NUM_GENERATIONS}_rule_{rank+1:03d}",
                "fitness":    round(float(fitnesses[int(idx)]), 10),
                "chromosome": population[int(idx)].tolist(),
                "rule_dict": {
                    str(k): v
                    for k, v in chromosome_to_rule_dict(population[int(idx)]).items()
                },
            }
            for rank, idx in enumerate(order)
        ],
    }
    with open(FINAL_POPULATION, "w") as f:
        json.dump(final_pop_data, f, indent=2)
    print(f"Saved final population: {FINAL_POPULATION}")

    print(f"\n=== Summary ===")
    print(f"  best_fitness_found:  {best_fitness_found:.6f}")
    print(f"  generation_of_best:  {generation_of_best}")
    print(f"  any_rule_scored_above_zero: {best_fitness_found > 0.0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
