#!/usr/bin/env python3
"""
evolve.py  —  Evolutionary search for v<c "massive" gliders (iter_197.2)

Imports MassiveGliderFitness and T_TROMINO_PARTICLE from
massive_glider_fitness.py and runs a GA over 7-bit hex LUT chromosomes
(only the center-output bit is mutable; the simulator only reads that bit).

The lightweight ``Evolution`` class wraps the GA loop and accepts
``fitness_fn`` and ``particle_shape`` so the same harness can be reused
with other fitness/particle pairs.

Outputs are written under archive/iter_197.2/results/.
"""

from __future__ import annotations

import concurrent.futures
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import generate_random_c2_rule
from massive_glider_fitness import (
    MassiveGliderFitness,
    T_TROMINO_PARTICLE,
)


PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_197.2" / "results"

LUT_SIZE        = 128
RNG_SEED        = 197_2
ELITE_FRACTION  = 0.10
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.01


# ── Chromosome <-> rule_dict ──────────────────────────────────────────────────

def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    """Convert a 128-bit center-output chromosome to the rule_dict form expected
    by MassiveGliderFitness (rule_dict_to_lut only reads the center bit anyway,
    so we encode v = (center_bit << 6) | (state & 0x3F))."""
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


# ── Module-level fitness (initialised in __main__ / worker) ──────────────────

_FITNESS: MassiveGliderFitness | None = None


def _eval_worker(chrom_list: list) -> dict:
    global _FITNESS
    if _FITNESS is None:
        _FITNESS = MassiveGliderFitness()
    chrom     = np.asarray(chrom_list, dtype=np.uint8)
    rule_dict = chromosome_to_rule_dict(chrom)
    m         = _FITNESS.evaluate(rule_dict)
    return {"chromosome": chrom_list, "metrics": m}


# ── Genetic operators ────────────────────────────────────────────────────────

def two_point_crossover(p1, p2, rng):
    n = len(p1)
    a, b = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(chrom, rate, rng):
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


def select_top_k(population, fitnesses, k):
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Evolution loop ───────────────────────────────────────────────────────────

class Evolution:
    """Minimal GA harness parameterised by fitness function and particle shape.

    ``particle_shape`` is forwarded for API completeness; the seed shape is
    actually owned by the fitness function (MassiveGliderFitness already uses
    T_TROMINO_PARTICLE internally).
    """

    def __init__(
        self,
        fitness_fn,
        particle_shape: list,
        generations: int = 50,
        population_size: int = 100,
        elite_fraction: float = ELITE_FRACTION,
        crossover_rate: float = CROSSOVER_RATE,
        mutation_rate:  float = MUTATION_RATE,
        rng_seed: int = RNG_SEED,
        max_workers: int = 8,
    ) -> None:
        self.fitness_fn      = fitness_fn
        self.particle_shape  = particle_shape
        self.generations     = generations
        self.population_size = population_size
        self.elite_count     = max(2, int(population_size * elite_fraction))
        self.crossover_rate  = crossover_rate
        self.mutation_rate   = mutation_rate
        self.rng             = random.Random(rng_seed)
        self.max_workers     = max_workers

    def initial_population(self) -> list:
        pop = []
        for _ in range(self.population_size):
            rule = generate_random_c2_rule(self.rng)
            pop.append(rule_dict_to_chromosome(rule))
        return pop

    def _evaluate(self, population):
        tasks = [c.tolist() for c in population]
        out   = [None] * len(tasks)
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as ex:
            futs = {ex.submit(_eval_worker, t): i for i, t in enumerate(tasks)}
            for fut in concurrent.futures.as_completed(futs):
                i = futs[fut]
                out[i] = fut.result()
        fitnesses = [r["metrics"]["fitness"] for r in out]
        metrics   = [r["metrics"]            for r in out]
        return fitnesses, metrics

    def run(self):
        print(f"=== Evolution: {self.fitness_fn.name} / particle={self.particle_shape} ===")
        print(f"  generations={self.generations}  population={self.population_size}  "
              f"elite={self.elite_count}  workers={self.max_workers}")

        population = self.initial_population()
        fitnesses, metrics_l = self._evaluate(population)
        best_idx        = int(np.argmax(fitnesses))
        best_fitness    = float(fitnesses[best_idx])
        best_chrom      = population[best_idx].copy()
        best_metrics    = metrics_l[best_idx]
        best_generation = 0

        stats = []
        n_nonzero = sum(1 for f in fitnesses if f > 0.0)
        stats.append({
            "generation": 0,
            "max":  float(np.max(fitnesses)),
            "mean": float(np.mean(fitnesses)),
            "std":  float(np.std(fitnesses)),
            "non_zero": int(n_nonzero),
        })
        print(f"  Gen  0: max={stats[-1]['max']:.4f}  mean={stats[-1]['mean']:.4f}  "
              f"non_zero={n_nonzero}")

        for gen in range(1, self.generations + 1):
            elite   = select_top_k(population, fitnesses, self.elite_count)
            new_pop = [e.copy() for e in elite]
            while len(new_pop) < self.population_size:
                p1, p2 = self.rng.sample(elite, 2)
                if self.rng.random() < self.crossover_rate:
                    c1, c2 = two_point_crossover(p1, p2, self.rng)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                c1 = per_bit_mutation(c1, self.mutation_rate, self.rng)
                c2 = per_bit_mutation(c2, self.mutation_rate, self.rng)
                new_pop.append(c1)
                if len(new_pop) < self.population_size:
                    new_pop.append(c2)

            population = new_pop
            fitnesses, metrics_l = self._evaluate(population)
            gen_best_idx = int(np.argmax(fitnesses))
            gen_best     = float(fitnesses[gen_best_idx])

            if gen_best > best_fitness:
                best_fitness    = gen_best
                best_chrom      = population[gen_best_idx].copy()
                best_metrics    = metrics_l[gen_best_idx]
                best_generation = gen

            n_nonzero = sum(1 for f in fitnesses if f > 0.0)
            stats.append({
                "generation": gen,
                "max":  gen_best,
                "mean": float(np.mean(fitnesses)),
                "std":  float(np.std(fitnesses)),
                "non_zero": int(n_nonzero),
            })
            print(f"  Gen {gen:2d}: max={gen_best:.4f}  "
                  f"mean={stats[-1]['mean']:.4f}  non_zero={n_nonzero}  "
                  f"best_so_far={best_fitness:.4f}@gen{best_generation}")

        return {
            "best_fitness":    float(best_fitness),
            "best_chrom":      best_chrom,
            "best_metrics":    best_metrics,
            "best_generation": int(best_generation),
            "stats":           stats,
            "final_population": [c.tolist() for c in population],
            "final_fitnesses":  [float(f) for f in fitnesses],
        }


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    evo = Evolution(
        fitness_fn      = MassiveGliderFitness(),
        particle_shape  = T_TROMINO_PARTICLE,
        generations     = 50,
        population_size = 100,
    )
    result = evo.run()
    elapsed = time.time() - t0

    print(f"\n=== Search complete in {elapsed:.1f}s ===")
    print(f"  Best fitness   : {result['best_fitness']:.6f}")
    print(f"  Best generation: {result['best_generation']}")
    print(f"  Best metrics   : {result['best_metrics']}")

    # Save champion
    champ_rule = chromosome_to_rule_dict(np.asarray(result["best_chrom"], dtype=np.uint8))
    champion_path = OUTPUT_DIR / "champion_rule.json"
    payload = {
        "fitness":        result["best_fitness"],
        "generation":     result["best_generation"],
        "metrics":        {k: (v if not isinstance(v, float) else round(v, 8))
                           for k, v in result["best_metrics"].items()},
        "particle":       T_TROMINO_PARTICLE,
        "rule":           {str(k): int(v) for k, v in champ_rule.items()},
        "chromosome":     list(map(int, result["best_chrom"])),
        "elapsed_sec":    round(elapsed, 2),
    }
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved champion: {champion_path}")

    # Save generation stats
    stats_path = OUTPUT_DIR / "generation_stats.json"
    with open(stats_path, "w") as f:
        json.dump(result["stats"], f, indent=2)
    print(f"Saved stats   : {stats_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
