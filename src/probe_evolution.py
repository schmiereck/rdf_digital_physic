#!/usr/bin/env python3
"""
probe_evolution.py  —  5-generation evolutionary search probe

Uses DisplacementConsistencyFitness (from new_fitness.py) to search for
hexagonal CA rules that produce consistent, directional motion from the
3-bit L-tromino seed.

Outputs:
  archive/iter_220/results/champion_rule.json
  archive/iter_220/results/fitness_log.csv
"""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Ensure src is on path ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import from existing modules (mapped to evoflux.* conceptually)
#   evoflux.evoflux       → evolution           (C2 rule generation)
#   evoflux.fitness       → new_fitness         (DisplacementConsistencyFitness)
#   evoflux.rules         → rule (imported for LUT helpers)
#   evoflux.seeds         → seeds               (seed utilities)

from evolution import generate_random_c2_rule, rule_dict_to_lut, step_grid  # noqa: E402
from new_fitness import DisplacementConsistencyFitness                    # noqa: E402
from seeds import L_TROMINO_SEED                                          # noqa: E402
from rule import Rule                                                     # noqa: E402

# ── Configuration ────────────────────────────────────────────────────────────

POPULATION_SIZE = 100
GRID_SIZE       = 128
STEPS           = 500            # simulation horizon
GENERATIONS     = 5
ELITE_SIZE      = 10
MUTATION_RATE   = 0.01
RNG_SEED        = None           # let random seed be implicit

OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_220" / "results"
LUT_SIZE = 128

# ── Chromosome helpers ───────────────────────────────────────────────────────


def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    """Convert a 128-element binary chromosome to a sparse rule_dict."""
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    """Convert a rule_dict to a 128-element binary chromosome."""
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Simulation + history collection ──────────────────────────────────────────


def simulate_with_history(
    rule_dict: dict,
    horizon: int = STEPS,
    grid_size: int = GRID_SIZE,
    seed_com=None,
) -> list:
    """Run a CA simulation and return a history suitable for
    DisplacementConsistencyFitness.__call__().

    Returns a list of dicts, each with keys: 'step', 'com', 'bit_count'.
    """
    lut = rule_dict_to_lut(rule_dict)

    # Seed grid
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    grid[63, 63] = 1
    grid[64, 63] = 1
    grid[64, 64] = 1

    def com_and_bits(g):
        rows, cols = np.where(g > 0)
        if len(rows) == 0:
            return (0.0, 0.0), 0
        return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

    # Record step 0
    hist = [{"step": 0, "com": com_and_bits(grid)[0], "bit_count": com_and_bits(grid)[1]}]

    for t in range(1, horizon + 1):
        grid = step_grid(grid, lut)
        c, b = com_and_bits(grid)
        hist.append({"step": t, "com": c, "bit_count": b})

    return hist


# ── Fitness evaluator ────────────────────────────────────────────────────────


class FitnessEvaluator:
    """Wraps DisplacementConsistencyFitness to evaluate a rule_dict."""

    def __init__(self, num_windows: int = 5):
        self.fitness_fn = DisplacementConsistencyFitness(num_windows=num_windows)

    def evaluate(self, rule_dict: dict) -> dict:
        """Return a dict with 'fitness' and 'rule_dict' keys."""
        hist = simulate_with_history(rule_dict)
        score = self.fitness_fn(hist)
        return {"fitness": float(score), "rule_dict": rule_dict}


# ── Population initialisation ────────────────────────────────────────────────


def generate_random_population(size: int, rng: random.Random) -> list[np.ndarray]:
    """Generate a population of random C2-symmetric chromosomes."""
    population: list[np.ndarray] = []
    for _ in range(size):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))
        # Build C2 rule
        rule = _try_build_c2_rule(pairs)
        if rule is None:
            continue
        population.append(rule_dict_to_chromosome(rule))
    # Fallback: random chromosomes for any shortage
    while len(population) < size:
        chrom = np.array(
            [rng.randint(0, 1) for _ in range(LUT_SIZE)], dtype=np.uint8
        )
        population.append(chrom)
    return population[:size]


def _try_build_c2_rule(pairs):
    """Build a C2-symmetric rule from (src, dst) pairs.

    For hex 60-degree rotation, C2 = two 60° rotations = 180° rotation.
    _rotate_c2 maps a state to its 180°-rotated counterpart.
    """
    def _rotate60(state):
        c  = (state >> 6) & 1
        b1 = (state >> 5) & 1
        b2 = (state >> 4) & 1
        b3 = (state >> 3) & 1
        b4 = (state >> 2) & 1
        b5 = (state >> 1) & 1
        b6 = (state >> 0) & 1
        return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5

    def _rotate_c2(state):
        return _rotate60(_rotate60(_rotate60(state)))

    rule = {}
    for a, b in pairs:
        rot_a, rot_b = _rotate_c2(a), _rotate_c2(b)
        for src, dst in [(a, b), (b, a), (rot_a, rot_b), (rot_b, rot_a)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


# ── Genetic operators ────────────────────────────────────────────────────────


def swap_mutate(chrom: np.ndarray, num_swaps: int, rng: random.Random) -> np.ndarray:
    """Mutate a chromosome by `num_swaps` random index swaps."""
    out = chrom.copy()
    n = len(out)
    for _ in range(num_swaps):
        i, j = rng.sample(range(n), 2)
        out[i], out[j] = out[j], out[i]
    return out


def select_top_k(
    population: list, scores: list, k: int
) -> list:
    order = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── EvolutionaryOptimizer ────────────────────────────────────────────────────


class EvolutionaryOptimizer:
    """Runs a genetic algorithm over CA rule populations."""

    def __init__(
        self,
        population_size: int = POPULATION_SIZE,
        generations: int = GENERATIONS,
        elite_size: int = ELITE_SIZE,
        mutation_rate: float = MUTATION_RATE,
        horizon: int = STEPS,
        grid_size: int = GRID_SIZE,
        rng_seed: int = RNG_SEED,
        fitness_num_windows: int = 5,
    ):
        self.population_size = population_size
        self.generations = generations
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.horizon = horizon
        self.grid_size = grid_size
        self.rng = random.Random(rng_seed)
        self.fitness_eval = FitnessEvaluator(num_windows=fitness_num_windows)
        self.num_swaps = max(1, round(mutation_rate * LUT_SIZE))
        self.gen_log: list[dict] = []
        self.champion_chrom: np.ndarray | None = None
        self.champion_fitness = -1.0
        self.champion_metrics: dict | None = None

    def run(self) -> dict:
        """Run the evolution and return results."""
        print(f"=== Evolutionary Probe ===")
        print(f"  population_size={self.population_size}  "
              f"generations={self.generations}  "
              f"elite={self.elite_size}  "
              f"mutations={self.num_swaps}  "
              f"horizon={self.horizon}  "
              f"grid={self.grid_size}  "
              f"swaps/child={self.num_swaps}")

        # Generate initial population
        print("  Generating random C2-symmetric population ...")
        population = generate_random_population(self.population_size, self.rng)

        # Evaluate generation 0
        scores, all_metrics = self._evaluate_population(population)
        self._log_generation(0, scores, all_metrics)
        self._update_champion(0, scores, all_metrics, population)

        for gen in range(1, self.generations + 1):
            elites = select_top_k(population, scores, self.elite_size)
            next_pop = [e.copy() for e in elites]
            while len(next_pop) < self.population_size:
                parent = self.rng.choice(elites)
                child = swap_mutate(parent, self.num_swaps, self.rng)
                next_pop.append(child)
            population = next_pop

            scores, all_metrics = self._evaluate_population(population)
            self._log_generation(gen, scores, all_metrics)
            self._update_champion(gen, scores, all_metrics, population)

        return {
            "gen_log": self.gen_log,
            "champion_chrom": self.champion_chrom,
            "champion_fitness": float(self.champion_fitness),
            "champion_metrics": self.champion_metrics,
            "final_population": population,
            "final_scores": scores,
        }

    def _evaluate_population(self, population: list) -> tuple[list, list]:
        """Evaluate every rule in the population. Returns (scores, metrics)."""
        scores: list[float] = []
        all_metrics: list[dict] = []
        for i, chrom in enumerate(population):
            rule_dict = chromosome_to_rule_dict(chrom)
            m = self.fitness_eval.evaluate(rule_dict)
            scores.append(m["fitness"])
            all_metrics.append(m)
            if (i + 1) % 25 == 0:
                print(f"    ... evaluated {i+1}/{len(population)} ...")
        return scores, all_metrics

    def _log_generation(self, gen: int, scores: list, all_metrics: list):
        scores_np = np.asarray(scores)
        entry = {
            "generation": gen,
            "min_fitness": float(scores_np.min()),
            "mean_fitness": float(scores_np.mean()),
            "max_fitness": float(scores_np.max()),
            "std_fitness": float(scores_np.std()),
        }
        self.gen_log.append(entry)
        print(
            f"  Gen {gen:2d}: max={entry['max_fitness']:.4f}  "
            f"mean={entry['mean_fitness']:.4f}  "
            f"std={entry['std_fitness']:.4f}  "
            f"min={entry['min_fitness']:.4f}"
        )

    def _update_champion(self, gen, scores, all_metrics, population):
        best_idx = int(np.argmax(scores))
        if scores[best_idx] > self.champion_fitness:
            self.champion_fitness = float(scores[best_idx])
            self.champion_chrom = population[best_idx].copy()
            self.champion_metrics = all_metrics[best_idx]
            if gen > 0:
                print(f"    ** new champion @ gen {gen} **")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run evolution
    optimizer = EvolutionaryOptimizer(
        population_size=POPULATION_SIZE,
        generations=GENERATIONS,
        elite_size=ELITE_SIZE,
        mutation_rate=MUTATION_RATE,
        horizon=STEPS,
        grid_size=GRID_SIZE,
        rng_seed=RNG_SEED,
        fitness_num_windows=5,
    )
    result = optimizer.run()

    # ── Save champion rule ──────────────────────────────────────────────
    champ_rule_dict = chromosome_to_rule_dict(result["champion_chrom"])
    payload = {
        "fitness": result["champion_fitness"],
        "champion_generation": 0,
        "num_generations": GENERATIONS,
        "population_size": POPULATION_SIZE,
        "elite_size": ELITE_SIZE,
        "mutation_rate": MUTATION_RATE,
        "horizon": STEPS,
        "grid_size": GRID_SIZE,
        "fitness_function": "DisplacementConsistencyFitness",
        "metrics": result["champion_metrics"],
        "rule_dict": {str(k): int(v) for k, v in champ_rule_dict.items()},
        "chromosome": [int(b) for b in result["champion_chrom"]],
    }

    champion_path = OUTPUT_DIR / "champion_rule.json"
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved champion rule -> {champion_path}")

    # ── Save fitness log CSV ───────────────────────────────────────────
    log_df = pd.DataFrame(result["gen_log"])
    # Select only the required columns
    log_df = log_df[["generation", "mean_fitness", "max_fitness", "min_fitness", "std_fitness"]]
    log_path = OUTPUT_DIR / "fitness_log.csv"
    log_df.to_csv(log_path, index=False)
    print(f"Saved fitness log   -> {log_path}")

    # ── Print fitness log to stdout ────────────────────────────────────
    print("\n=== Fitness Log ===")
    print(log_df.to_string(index=False))

    # ── Report on success criterion ────────────────────────────────────
    mean_gen1 = log_df.loc[log_df["generation"] == 0, "mean_fitness"].values[0]
    mean_gen5 = log_df.loc[log_df["generation"] == GENERATIONS, "mean_fitness"].values[0]
    criterion_met = mean_gen5 >= 2 * mean_gen1

    print(f"\n=== Success Criterion Check ===")
    print(f"  mean_fitness_gen1 = {mean_gen1:.6f}")
    print(f"  mean_fitness_gen5 = {mean_gen5:.6f}")
    print(f"  2 * mean_fitness_gen1 = {2 * mean_gen1:.6f}")
    if criterion_met:
        print(f"  RESULT: Criterion MET — mean_fitness_gen5 ({mean_gen5:.6f}) >= "
              f"2 * mean_fitness_gen1 ({2 * mean_gen1:.6f})")
    else:
        print(f"  RESULT: Criterion NOT MET — mean_fitness_gen5 ({mean_gen5:.6f}) < "
              f"2 * mean_fitness_gen1 ({2 * mean_gen1:.6f})")

    # Return values for the executor
    return {
        "mean_gen1": mean_gen1,
        "mean_gen5": mean_gen5,
        "criterion_met": criterion_met,
    }


if __name__ == "__main__":
    main()
