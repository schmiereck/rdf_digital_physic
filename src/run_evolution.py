#!/usr/bin/env python3
"""
run_evolution.py

Evolutionary search for a stable glider using SimpleMotionFitness.

Population : 100 C2-symmetric rules
Generations: 10
Selection  : truncation (top 10 = 10%)
Mutation   : bit-flip / pair-replace on kernel pairs, with random fallback
"""

import csv
import random
import sys
from pathlib import Path

import numpy as np

import rules
from evolution import _try_build_c2_rule, _rotate_c2, generate_random_c2_rule
from fitness_simple_motion import SimpleMotionFitness

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_176" / "results"

POPULATION_SIZE = 100
N_GENERATIONS   = 10
ELITE_SIZE      = 10          # top 10% kept for selection
GRID_SIZE       = 64
STEPS           = 200


# ── Kernel-pair helpers ───────────────────────────────────────────────────────

def _extract_pairs(rule_dict: dict) -> list[tuple[int, int]]:
    """Recover a minimal set of kernel pairs from a C2 rule dict."""
    seen: set[tuple[int, int]] = set()
    pairs: list[tuple[int, int]] = []
    for a, b in rule_dict.items():
        a, b = int(a), int(b)
        if a == b:
            continue
        canon = (min(a, b), max(a, b))
        if canon in seen:
            continue
        seen.add(canon)
        ra, rb = _rotate_c2(a), _rotate_c2(b)
        seen.add((min(ra, rb), max(ra, rb)))
        pairs.append((a, b))
    return pairs


def _random_rule_with_pairs(rng: random.Random) -> tuple[dict, list]:
    """Generate a fresh random C2 rule and return (rule_dict, pairs)."""
    for _ in range(10_000):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule, pairs
    raise RuntimeError("failed to generate valid C2 rule")


def _mutate(parent_rule: dict, rng: random.Random,
            max_attempts: int = 500) -> tuple[dict, list]:
    """Mutate a C2 rule by perturbing its kernel pairs."""
    parent_pairs = _extract_pairs(parent_rule)
    for _ in range(max_attempts):
        pairs = list(parent_pairs)
        choice = rng.random()

        if choice < 0.5 and pairs:          # flip one bit in a pair member
            idx = rng.randrange(len(pairs))
            a, b = pairs[idx]
            bit = rng.randrange(7)
            if rng.random() < 0.5:
                a = max(1, (a ^ (1 << bit)) & 127)
            else:
                b = max(1, (b ^ (1 << bit)) & 127)
            if a == b:
                continue
            pairs[idx] = (a, b)

        elif choice < 0.8 and pairs:        # replace one pair entirely
            idx = rng.randrange(len(pairs))
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs[idx] = (a, b)

        else:                               # add a new pair
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))

        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule, pairs

    return _random_rule_with_pairs(rng)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rng     = random.Random(176)
    fitness = SimpleMotionFitness(grid_size=GRID_SIZE, steps=STEPS)

    # ── Initialise population ─────────────────────────────────────────────────
    print(f"Initialising population of {POPULATION_SIZE} rules …")
    population: list[dict] = [
        rules.random_c2_symmetric_rule(rng) for _ in range(POPULATION_SIZE)
    ]

    champion_rule       = None
    champion_fitness    = -1.0
    champion_generation = 0
    gen_log: list[dict] = []

    # ── Evolution loop ────────────────────────────────────────────────────────
    for gen in range(1, N_GENERATIONS + 1):
        print(f"\n=== Generation {gen}/{N_GENERATIONS} ===")

        scores: list[float] = []
        for i, rule in enumerate(population):
            result = fitness.evaluate(rule)
            scores.append(result["fitness"])
            if (i + 1) % 20 == 0:
                print(f"  evaluated {i + 1}/{POPULATION_SIZE} …")

        scores_np = np.array(scores)
        gen_min   = float(scores_np.min())
        gen_mean  = float(scores_np.mean())
        gen_max   = float(scores_np.max())
        gen_std   = float(scores_np.std())

        print(f"  min={gen_min:.6f}  mean={gen_mean:.6f}  "
              f"max={gen_max:.6f}  std={gen_std:.6f}")

        gen_log.append({
            "generation": gen,
            "min":        round(gen_min,  8),
            "mean":       round(gen_mean, 8),
            "max":        round(gen_max,  8),
            "std":        round(gen_std,  8),
        })

        # Track champion across all generations
        best_idx = int(scores_np.argmax())
        if scores[best_idx] > champion_fitness:
            champion_fitness    = scores[best_idx]
            champion_rule       = population[best_idx]
            champion_generation = gen
            print(f"  ** New champion: fitness={champion_fitness:.6f} "
                  f"(gen {champion_generation}) **")

        # ── Selection: keep top ELITE_SIZE ───────────────────────────────────
        ranked = sorted(range(POPULATION_SIZE), key=lambda i: scores[i], reverse=True)
        elites = [population[i] for i in ranked[:ELITE_SIZE]]

        # ── Procreation: mutate elites to fill next generation ────────────────
        if gen < N_GENERATIONS:
            next_gen: list[dict] = list(elites)           # carry elites forward
            while len(next_gen) < POPULATION_SIZE:
                parent = rng.choice(elites)
                child, _ = _mutate(parent, rng)
                next_gen.append(child)
            population = next_gen

    # ── Save champion rule ────────────────────────────────────────────────────
    champion_path = RESULTS_DIR / "new_champion_rule.txt"
    with open(champion_path, "w") as f:
        f.write(f"# Champion rule (fitness={champion_fitness:.8f}, "
                f"generation={champion_generation})\n")
        for k in sorted(champion_rule.keys()):
            f.write(f"{k}: {champion_rule[k]}\n")
    print(f"\nSaved champion rule -> {champion_path}")

    # ── Save evolution log ────────────────────────────────────────────────────
    log_path = RESULTS_DIR / "evolution_log.csv"
    fieldnames = ["generation", "min", "mean", "max", "std"]
    with open(log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(gen_log)
    print(f"Saved evolution log  -> {log_path}")

    # ── Final summary ─────────────────────────────────────────────────────────
    print("\n=== Evolution complete ===")
    print(f"  champion_fitness:    {champion_fitness:.8f}")
    print(f"  champion_generation: {champion_generation}")
    print(f"  final_gen_mean:      {gen_log[-1]['mean']:.8f}")
    print(f"  final_gen_max:       {gen_log[-1]['max']:.8f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
