#!/usr/bin/env python3
"""
run_evolution_exp_220.py  —  20-generation evolutionary search for a stable glider

Uses DisplacementConsistencyFitness (new_fitness.py) with the 3-bit L-tromino
seed to search for hexagonal CA rules that produce consistent, directional motion.

Parameters:
  population_size : 100
  generations     : 20
  elite_size      : 10
  mutation_rate   : 0.01
  horizon         : 500 steps

Outputs:
  archive/iter_220/results/champion_rule.json
  archive/iter_220/results/evolution_summary.csv
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import generate_random_c2_rule, rule_dict_to_lut, step_grid  # noqa: E402
from new_fitness import DisplacementConsistencyFitness                       # noqa: E402

OUTPUT_DIR      = PROJECT_ROOT / "archive" / "iter_220" / "results"
POPULATION_SIZE = 100
GENERATIONS     = 20
ELITE_SIZE      = 10
MUTATION_RATE   = 0.01
GRID_SIZE       = 128
STEPS           = 500
LUT_SIZE        = 128
RNG_SEED        = 220


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


# ── Simulation + history collection ──────────────────────────────────────────

def simulate_with_history(rule_dict: dict) -> list:
    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    grid[63, 63] = 1
    grid[64, 63] = 1
    grid[64, 64] = 1

    def com_and_bits(g):
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return (0.0, 0.0), 0
        return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

    c0, b0 = com_and_bits(grid)
    hist = [{"step": 0, "com": c0, "bit_count": b0}]
    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        c, b = com_and_bits(grid)
        hist.append({"step": t, "com": c, "bit_count": b})
    return hist


# ── Fitness evaluator ─────────────────────────────────────────────────────────

_fitness_fn = DisplacementConsistencyFitness(num_windows=5)


def evaluate_rule(rule_dict: dict) -> float:
    hist  = simulate_with_history(rule_dict)
    score = _fitness_fn(hist)
    return float(score)


# ── Population helpers ────────────────────────────────────────────────────────

def generate_population(size: int, rng: random.Random) -> list[np.ndarray]:
    pop: list[np.ndarray] = []
    while len(pop) < size:
        rule = generate_random_c2_rule(rng)
        pop.append(rule_dict_to_chromosome(rule))
    return pop[:size]


def evaluate_population(population: list[np.ndarray]) -> list[float]:
    scores: list[float] = []
    for i, chrom in enumerate(population):
        rd    = chromosome_to_rule_dict(chrom)
        score = evaluate_rule(rd)
        scores.append(score)
        if (i + 1) % 25 == 0:
            print(f"    ... evaluated {i + 1}/{len(population)}")
    return scores


def select_top_k(population, scores, k):
    order = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


def swap_mutate(chrom: np.ndarray, num_swaps: int, rng: random.Random) -> np.ndarray:
    out = chrom.copy()
    n   = len(out)
    for _ in range(num_swaps):
        i, j     = rng.sample(range(n), 2)
        out[i], out[j] = out[j], out[i]
    return out


# ── Main evolution loop ───────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng       = random.Random(RNG_SEED)
    num_swaps = max(1, round(MUTATION_RATE * LUT_SIZE))

    print("=== run_evolution_exp_220 ===")
    print(f"  population={POPULATION_SIZE}  generations={GENERATIONS}  "
          f"elite={ELITE_SIZE}  swaps/child={num_swaps}  horizon={STEPS}")

    t0         = time.time()
    population = generate_population(POPULATION_SIZE, rng)

    champion_chrom:   np.ndarray | None = None
    champion_fitness: float             = -1.0
    gen_log: list[dict] = []

    # ── Evaluate generation 0 ────────────────────────────────────────────────
    scores = evaluate_population(population)
    best_idx = int(np.argmax(scores))
    if scores[best_idx] > champion_fitness:
        champion_fitness = float(scores[best_idx])
        champion_chrom   = population[best_idx].copy()

    gen_log.append({
        "generation":   0,
        "best_fitness": float(np.max(scores)),
        "mean_fitness": float(np.mean(scores)),
    })
    print(f"  Gen  0: best={gen_log[-1]['best_fitness']:.6f}  "
          f"mean={gen_log[-1]['mean_fitness']:.6f}")

    # ── Generational loop ─────────────────────────────────────────────────────
    for gen in range(1, GENERATIONS + 1):
        elites   = select_top_k(population, scores, ELITE_SIZE)
        next_pop = [e.copy() for e in elites]
        while len(next_pop) < POPULATION_SIZE:
            parent = rng.choice(elites)
            child  = swap_mutate(parent, num_swaps, rng)
            next_pop.append(child)
        population = next_pop

        scores   = evaluate_population(population)
        best_idx = int(np.argmax(scores))

        if scores[best_idx] > champion_fitness:
            champion_fitness = float(scores[best_idx])
            champion_chrom   = population[best_idx].copy()
            print(f"    ** new champion @ gen {gen}: {champion_fitness:.6f} **")

        gen_log.append({
            "generation":   gen,
            "best_fitness": float(np.max(scores)),
            "mean_fitness": float(np.mean(scores)),
        })
        print(f"  Gen {gen:2d}: best={gen_log[-1]['best_fitness']:.6f}  "
              f"mean={gen_log[-1]['mean_fitness']:.6f}  "
              f"champion={champion_fitness:.6f}")

    elapsed = time.time() - t0
    print(f"\n=== Search complete in {elapsed:.1f}s ===")
    print(f"  Champion fitness: {champion_fitness:.6f}")

    # ── Save champion rule ────────────────────────────────────────────────────
    champ_rd = chromosome_to_rule_dict(champion_chrom)
    payload  = {
        "fitness":          champion_fitness,
        "fitness_function": "DisplacementConsistencyFitness",
        "generations":      GENERATIONS,
        "population_size":  POPULATION_SIZE,
        "elite_size":       ELITE_SIZE,
        "mutation_rate":    MUTATION_RATE,
        "horizon":          STEPS,
        "grid_size":        GRID_SIZE,
        "seed_particle":    "L_TROMINO_3bit",
        "seed_cells":       [[63, 63], [64, 63], [64, 64]],
        "elapsed_sec":      round(elapsed, 2),
        "rule_dict":        {str(k): int(v) for k, v in champ_rd.items()},
        "chromosome":       [int(b) for b in champion_chrom],
    }
    champion_path = OUTPUT_DIR / "champion_rule.json"
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved champion rule  -> {champion_path}")

    # ── Save evolution summary CSV ─────────────────────────────────────────────
    summary_df   = pd.DataFrame(gen_log)[["generation", "best_fitness", "mean_fitness"]]
    summary_path = OUTPUT_DIR / "evolution_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Saved evolution summary -> {summary_path}")

    # ── Print summary table ────────────────────────────────────────────────────
    print("\n=== Evolution Summary ===")
    print(summary_df.to_string(index=False))

    # Check for plateau: compare last 5 gens vs first 5 gens
    gen0_mean  = gen_log[0]["mean_fitness"]
    gen_n_mean = gen_log[-1]["mean_fitness"]
    improved   = gen_n_mean > gen0_mean * 1.5
    print(f"\n  mean_fitness gen0:  {gen0_mean:.6f}")
    print(f"  mean_fitness genN:  {gen_n_mean:.6f}")
    print(f"  Fitness improved significantly: {improved}")


if __name__ == "__main__":
    main()
