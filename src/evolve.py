#!/usr/bin/env python3
"""
evolve.py  —  Gen-1 genetic algorithm for L-tromino motion (iter_170)

Reads Gen-0 results, applies tournament selection (k=3) + uniform crossover
(p=0.5 per bit) + bit-flip mutation (p=0.01 per bit) to produce Gen-1.

Chromosome: 128-bit binary LUT (center-cell output for each 7-bit state).
Fitness:    displacement / (1 + final_bit_count) after 200 steps.
Output:     archive/iter_170/results/gen_1_results.json
"""

import concurrent.futures
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
GEN0_PATH    = PROJECT_ROOT / "archive" / "iter_170" / "results" / "gen_0_results.json"
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_170" / "results"

POPULATION_SIZE = 100
GRID_SIZE       = 128
STEPS           = 200
TOURNAMENT_SIZE = 3
CROSSOVER_PROB  = 0.5
MUTATION_PROB   = 0.01
LTROMINO_CELLS  = [(63, 63), (64, 63), (64, 64)]
RNG_SEED        = 1701


# ── Rule / chromosome helpers ──────────────────────────────────────────────────

def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    """Convert a rule dict to the 128-bit binary center-cell LUT."""
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Simulation (identical to archive/iter_170/evolve.py) ──────────────────────

def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def _center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def evaluate_lut(lut: np.ndarray) -> dict:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1
    initial_com = _center_of_mass(grid)

    for _ in range(STEPS):
        grid = _step_grid(grid, lut)

    final_com       = _center_of_mass(grid)
    final_bit_count = int(grid.sum())
    dx              = final_com[0] - initial_com[0]
    dy              = final_com[1] - initial_com[1]
    displacement    = math.sqrt(dx * dx + dy * dy)
    fitness         = displacement / (1.0 + final_bit_count)
    return {
        "fitness":         fitness,
        "displacement":    displacement,
        "final_bit_count": final_bit_count,
        "initial_com":     list(initial_com),
        "final_com":       list(final_com),
    }


def _eval_worker(args: tuple) -> dict:
    rule_id, chrom_list = args
    lut    = np.array(chrom_list, dtype=np.uint8)
    result = evaluate_lut(lut)
    return {"rule_id": rule_id, "chromosome": chrom_list, **result}


# ── Genetic operators ──────────────────────────────────────────────────────────

def tournament_select(
    chromosomes: list,
    fitnesses: list,
    k: int,
    rng: random.Random,
) -> np.ndarray:
    candidates = rng.sample(range(len(chromosomes)), k)
    best = max(candidates, key=lambda i: fitnesses[i])
    return chromosomes[best].copy()


def uniform_crossover(
    p1: np.ndarray,
    p2: np.ndarray,
    prob: float,
    rng: random.Random,
) -> np.ndarray:
    mask  = np.array([rng.random() < prob for _ in range(len(p1))], dtype=bool)
    child = p1.copy()
    child[mask] = p2[mask]
    return child


def bit_flip_mutation(chrom: np.ndarray, prob: float, rng: random.Random) -> np.ndarray:
    for i in range(len(chrom)):
        if rng.random() < prob:
            chrom[i] ^= 1
    return chrom


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(GEN0_PATH) as f:
        gen0 = json.load(f)
    gen0_pop = gen0["population"]
    print(f"Loaded {len(gen0_pop)} Gen-0 rules from {GEN0_PATH.name}")

    gen0_chroms    = [rule_dict_to_lut(e["rule"]) for e in gen0_pop]
    gen0_fitnesses = [e["fitness"] for e in gen0_pop]
    print(f"Gen-0 max={max(gen0_fitnesses):.6f}  "
          f"mean={sum(gen0_fitnesses)/len(gen0_fitnesses):.6f}")

    rng             = random.Random(RNG_SEED)
    gen1_chroms: list = []
    for _ in range(POPULATION_SIZE):
        p1    = tournament_select(gen0_chroms, gen0_fitnesses, TOURNAMENT_SIZE, rng)
        p2    = tournament_select(gen0_chroms, gen0_fitnesses, TOURNAMENT_SIZE, rng)
        child = uniform_crossover(p1, p2, CROSSOVER_PROB, rng)
        child = bit_flip_mutation(child, MUTATION_PROB, rng)
        gen1_chroms.append(child)

    print(f"\nGenerated {POPULATION_SIZE} Gen-1 offspring. Evaluating ...")

    tasks   = [(f"gen1_rule_{i+1:03d}", chrom.tolist())
               for i, chrom in enumerate(gen1_chroms)]
    pop     = []
    workers = min(4, POPULATION_SIZE)

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_eval_worker, t): t[0] for t in tasks}
        done    = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            pop.append(result)
            done += 1
            print(
                f"  [{done:3d}/{POPULATION_SIZE}] {result['rule_id']}: "
                f"fitness={result['fitness']:.6f}  "
                f"disp={result['displacement']:.4f}  "
                f"bits={result['final_bit_count']:5d}"
            )

    pop.sort(key=lambda e: e["fitness"], reverse=True)

    fitnesses    = [e["fitness"] for e in pop]
    max_fitness  = float(max(fitnesses))
    mean_fitness = float(sum(fitnesses) / len(fitnesses))
    min_fitness  = float(min(fitnesses))

    print(f"\n=== Gen-1 Summary ===")
    print(f"  max_fitness:  {max_fitness:.8f}")
    print(f"  mean_fitness: {mean_fitness:.8f}")
    print(f"  min_fitness:  {min_fitness:.8f}")

    results = {
        "generation":      1,
        "population_size": POPULATION_SIZE,
        "tournament_size": TOURNAMENT_SIZE,
        "crossover_prob":  CROSSOVER_PROB,
        "mutation_prob":   MUTATION_PROB,
        "grid_size":       GRID_SIZE,
        "steps":           STEPS,
        "ltromino_cells":  LTROMINO_CELLS,
        "fitness_formula": "displacement / (1 + final_bit_count)",
        "max_fitness":     round(max_fitness,  10),
        "mean_fitness":    round(mean_fitness, 10),
        "min_fitness":     round(min_fitness,  10),
        "population": [
            {
                "rule_id":         e["rule_id"],
                "chromosome":      e["chromosome"],
                "fitness":         round(e["fitness"],      10),
                "displacement":    round(e["displacement"],  8),
                "final_bit_count": e["final_bit_count"],
                "final_com":       [round(x, 4) for x in e["final_com"]],
                "initial_com":     [round(x, 4) for x in e["initial_com"]],
            }
            for e in pop
        ],
    }

    out_path = OUTPUT_DIR / "gen_1_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
