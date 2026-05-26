#!/usr/bin/env python3
"""
totalistic_ga.py

Step 3 of the pre-registered experiment (iter_253).
Evolutionary GA for totalistic B/S rules on the FCC lattice.

Triggered because the designed sweep yielded < 5 candidates.
Population: 200 rules.
Genome: 26-bit (bits 0-10 = B for counts 1-11, bits 11-23 = S for counts 1-12).
Generations: 50 (or until total unique rules evaluated >= 10,000).
"""

from __future__ import annotations
import csv
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from synchronous_ca_fcc import (
    FCC_OFFSETS,
    bounding_extent,
    format_rule,
    lambda_param,
    simulate,
    step_ca,
    trig_com,
    unwrap_com,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
L = 40
CENTER = (L // 2, L // 2, L // 2)
GA_STEPS = 300
POP_SIZE = 200
GENERATIONS = 50
TOURNAMENT_SIZE = 3
MUTATION_P = 0.1
ELITE_SIZE = 5

GA_RNG = random.Random(42)
SEED_RNG = random.Random(42)

ARCHIVE_DIR = SCRIPT_DIR.parent / "archive" / "iter_253" / "results"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
GA_CSV = ARCHIVE_DIR / "ga_results.csv"

# Track globally evaluated rules to avoid duplicates and count toward 10,000
_globally_evaluated_rules = set()

# ---------------------------------------------------------------------------
# Genome helpers
# ---------------------------------------------------------------------------

def genome_to_rule(genome: list[int]) -> tuple[set, set]:
    """Convert 26-bit genome to (B, S) sets."""
    B = {i + 1 for i in range(11) if genome[i] == 1}
    S = {i + 1 for i in range(12) if genome[11 + i] == 1}
    return B, S


def rule_to_genome(B: set, S: set) -> list[int]:
    """Convert (B, S) to 26-bit genome."""
    genome = [0] * 26
    for k in B:
        if 1 <= k <= 11:
            genome[k - 1] = 1
    for k in S:
        if 1 <= k <= 12:
            genome[10 + k] = 1
    return genome


def random_genome() -> list[int]:
    """Generate a random valid genome (at least one bit in B and one in S)."""
    while True:
        g = [GA_RNG.randint(0, 1) for _ in range(26)]
        if any(g[:11]) and any(g[11:23]):
            return g


def mutate(genome: list[int], p: float = MUTATION_P) -> list[int]:
    """Bit-flip mutation."""
    child = genome.copy()
    for i in range(26):
        if GA_RNG.random() < p:
            child[i] = 1 - child[i]
    # Ensure validity
    if not any(child[:11]) or not any(child[11:23]):
        # Repair: force at least one bit in each section
        if not any(child[:11]):
            child[GA_RNG.randint(0, 10)] = 1
        if not any(child[11:23]):
            child[GA_RNG.randint(11, 22)] = 1
    return child


def crossover(p1: list[int], p2: list[int]) -> list[int]:
    """Uniform crossover."""
    child = [GA_RNG.choice([p1[i], p2[i]]) for i in range(26)]
    if not any(child[:11]) or not any(child[11:23]):
        if not any(child[:11]):
            child[GA_RNG.randint(0, 10)] = 1
        if not any(child[11:23]):
            child[GA_RNG.randint(11, 22)] = 1
    return child


# ---------------------------------------------------------------------------
# Seed generation for GA evaluation
# ---------------------------------------------------------------------------

def make_grid() -> np.ndarray:
    return np.zeros((L, L, L), dtype=np.uint8)


def set_cells(grid: np.ndarray, coords: list[tuple[int, int, int]]) -> None:
    for l, r, c in coords:
        grid[l % L, r % L, c % L] = 1


def generate_ga_seeds() -> list[tuple[str, list[tuple[int, int, int]]]]:
    """Generate 5 evaluation seeds deterministically."""
    seeds = []
    c = CENTER

    # 1 bit pair
    off = FCC_OFFSETS[0]
    seeds.append(("ga_pair_0", [c, (c[0] + off[0], c[1] + off[1], c[2] + off[2])]))

    # 1 L-tromino
    seeds.append(("ga_tromino_0", [c, (c[0] + 1, c[1] + 1, c[2] + 1), (c[0] + 2, c[1] + 2, c[2] + 2)]))

    # 3 random compact clusters of size 3-6
    compact_seeds = []
    while len(compact_seeds) < 3:
        size = SEED_RNG.randint(3, 6)
        cluster = [c]
        for _ in range(size - 1):
            existing = SEED_RNG.choice(cluster)
            off = SEED_RNG.choice(FCC_OFFSETS)
            new_cell = (
                (existing[0] + off[0]),
                (existing[1] + off[1]),
                (existing[2] + off[2]),
            )
            if new_cell not in cluster:
                cluster.append(new_cell)
        sorted_cluster = sorted(cluster)
        if sorted_cluster not in [sorted(s) for s in compact_seeds]:
            compact_seeds.append(sorted_cluster)

    for idx, coords in enumerate(compact_seeds):
        seeds.append((f"ga_compact_{idx}", coords))

    return seeds


# ---------------------------------------------------------------------------
# Fitness evaluation
# ---------------------------------------------------------------------------

def evaluate_rule(B: set, S: set, seeds: list) -> float:
    """Evaluate a rule on the GA seed set. Return mean fitness."""
    fitnesses = []
    for sname, scoords in seeds:
        grid = make_grid()
        set_cells(grid, scoords)
        initial_bits = len(scoords)

        result = simulate(grid, B, S, steps=GA_STEPS)
        bit_counts = result["bit_counts"]
        coms = result["coms"]
        extents = result["extents"]
        survival_time = result["survival_time"]

        survival_score = min(survival_time / 300.0, 1.0)

        eval_step = min(survival_time, GA_STEPS)
        if len(coms) > eval_step:
            disp_vec = tuple(coms[eval_step][i] - coms[0][i] for i in range(3))
            net_displacement = float(np.linalg.norm(disp_vec))
        else:
            net_displacement = 0.0
        displacement_score = min(net_displacement / 10.0, 1.0)

        if survival_time > 100:
            max_extent = max(extents[101:survival_time + 1]) if survival_time <= GA_STEPS else max(extents[101:])
        else:
            max_extent = float('inf')
        compact_score = 1.0 if max_extent <= 10 else 0.0

        if survival_time > 100:
            max_bits = max(bit_counts[101:survival_time + 1]) if survival_time <= GA_STEPS else max(bit_counts[101:])
            max_bit_ratio = max_bits / max(initial_bits, 1)
        else:
            max_bit_ratio = float('inf')
        no_bloom_score = 1.0 if max_bit_ratio <= 4.0 else 0.0

        fitness = survival_score * displacement_score * compact_score * no_bloom_score
        fitnesses.append(fitness)

    return float(np.mean(fitnesses))


# ---------------------------------------------------------------------------
# GA main loop
# ---------------------------------------------------------------------------

def tournament_select(population: list, fitnesses: list, k: int = TOURNAMENT_SIZE) -> list[int]:
    """Select one individual via tournament."""
    contestants = GA_RNG.sample(range(len(population)), k)
    best = contestants[0]
    best_f = fitnesses[best]
    for idx in contestants[1:]:
        if fitnesses[idx] > best_f:
            best = idx
            best_f = fitnesses[idx]
    return population[best]


def main():
    print("=" * 70)
    print("STEP 3 -- EVOLUTIONARY GA (iter_253)")
    print("=" * 70)

    seeds = generate_ga_seeds()
    print(f"GA seeds: {len(seeds)}")
    print(f"Population: {POP_SIZE}, Generations: {GENERATIONS}")
    print(f"Target: evaluate >= 10,000 unique rules total")
    print()

    # Load previously evaluated rules from sweep if available
    sweep_summary_path = ARCHIVE_DIR / "sweep_summary.json"
    if sweep_summary_path.exists():
        with open(sweep_summary_path, "r") as f:
            sweep_data = json.load(f)
        previously_evaluated = sweep_data.get("total_rules", 0)
        print(f"Previously evaluated rules from sweep: {previously_evaluated}")
    else:
        previously_evaluated = 0

    # Initialize population
    population = [random_genome() for _ in range(POP_SIZE)]
    for g in population:
        B, S = genome_to_rule(g)
        _globally_evaluated_rules.add(format_rule(B, S))

    # Evaluate initial population
    fitnesses = []
    for i, genome in enumerate(population):
        B, S = genome_to_rule(genome)
        f = evaluate_rule(B, S, seeds)
        fitnesses.append(f)
        if (i + 1) % 50 == 0:
            print(f"  Initial eval {i + 1}/{POP_SIZE} ...")

    best_ever = None
    best_fitness_ever = -1.0

    with open(GA_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["gen", "rule_str", "mean_fitness", "best_fitness"])
        writer.writeheader()

        for gen in range(1, GENERATIONS + 1):
            # Elitism
            sorted_idx = np.argsort(fitnesses)[::-1]
            new_pop = [population[idx].copy() for idx in sorted_idx[:ELITE_SIZE]]

            # Generate offspring
            while len(new_pop) < POP_SIZE:
                p1 = tournament_select(population, fitnesses)
                p2 = tournament_select(population, fitnesses)
                child = crossover(p1, p2)
                child = mutate(child)
                new_pop.append(child)

            population = new_pop

            # Evaluate new population (skip re-evaluation of known rules? No, evaluate all)
            fitnesses = []
            for i, genome in enumerate(population):
                B, S = genome_to_rule(genome)
                rstr = format_rule(B, S)
                _globally_evaluated_rules.add(rstr)
                f = evaluate_rule(B, S, seeds)
                fitnesses.append(f)

            best_idx = int(np.argmax(fitnesses))
            best_genome = population[best_idx]
            best_B, best_S = genome_to_rule(best_genome)
            best_rule_str = format_rule(best_B, best_S)
            best_f = fitnesses[best_idx]
            mean_f = float(np.mean(fitnesses))

            if best_f > best_fitness_ever:
                best_fitness_ever = best_f
                best_ever = best_genome

            writer.writerow({
                "gen": gen,
                "rule_str": best_rule_str,
                "mean_fitness": round(mean_f, 6),
                "best_fitness": round(best_f, 6),
            })
            f.flush()

            total_unique = previously_evaluated + len(_globally_evaluated_rules)
            print(f"Gen {gen:02d}: best_f={best_f:.4f}, mean_f={mean_f:.4f}, unique_rules={total_unique}")

            # Continue until we hit 10,000 unique rules evaluated
            if gen >= GENERATIONS and total_unique >= 10000:
                break

        # If we haven't reached 10,000 unique rules, keep running generations
        extra_gen = 0
        while total_unique < 10000:
            extra_gen += 1
            sorted_idx = np.argsort(fitnesses)[::-1]
            new_pop = [population[idx].copy() for idx in sorted_idx[:ELITE_SIZE]]
            while len(new_pop) < POP_SIZE:
                p1 = tournament_select(population, fitnesses)
                p2 = tournament_select(population, fitnesses)
                child = crossover(p1, p2)
                child = mutate(child)
                new_pop.append(child)
            population = new_pop

            fitnesses = []
            for genome in population:
                B, S = genome_to_rule(genome)
                rstr = format_rule(B, S)
                _globally_evaluated_rules.add(rstr)
                f = evaluate_rule(B, S, seeds)
                fitnesses.append(f)

            best_idx = int(np.argmax(fitnesses))
            best_genome = population[best_idx]
            best_B, best_S = genome_to_rule(best_genome)
            best_rule_str = format_rule(best_B, best_S)
            best_f = fitnesses[best_idx]
            mean_f = float(np.mean(fitnesses))

            if best_f > best_fitness_ever:
                best_fitness_ever = best_f
                best_ever = best_genome

            writer.writerow({
                "gen": GENERATIONS + extra_gen,
                "rule_str": best_rule_str,
                "mean_fitness": round(mean_f, 6),
                "best_fitness": round(best_f, 6),
            })
            f.flush()

            total_unique = previously_evaluated + len(_globally_evaluated_rules)
            print(f"Gen {GENERATIONS + extra_gen:02d}: best_f={best_f:.4f}, mean_f={mean_f:.4f}, unique_rules={total_unique}")

    print(f"\nGA finished. Total unique rules evaluated: {total_unique}")
    print(f"Best fitness ever: {best_fitness_ever:.6f}")
    if best_ever is not None:
        best_B, best_S = genome_to_rule(best_ever)
        print(f"Best rule: {format_rule(best_B, best_S)}")

    # Identify candidate rules (fitness > 0 on any seed)
    # Re-evaluate best rules on full seed suite to find candidates
    print("\nRe-evaluating top rules on full seed suite for candidate identification ...")
    candidate_rules = []
    # Check top 20 unique rules by fitness
    unique_rules = {}
    for genome in population:
        B, S = genome_to_rule(genome)
        rstr = format_rule(B, S)
        if rstr not in unique_rules:
            unique_rules[rstr] = evaluate_rule(B, S, seeds)

    top_rules = sorted(unique_rules.items(), key=lambda x: x[1], reverse=True)[:20]
    for rstr, fit in top_rules:
        if fit > 0:
            candidate_rules.append(rstr)

    print(f"Candidate rules with fitness > 0: {len(candidate_rules)}")

    # Save GA summary
    ga_summary = {
        "total_unique_rules_evaluated": total_unique,
        "generations_run": GENERATIONS + extra_gen,
        "best_fitness": best_fitness_ever,
        "best_rule": format_rule(*genome_to_rule(best_ever)) if best_ever else None,
        "candidate_rules": candidate_rules,
    }
    with open(ARCHIVE_DIR / "ga_summary.json", "w") as f:
        json.dump(ga_summary, f, indent=2)
    print(f"Saved GA summary: {ARCHIVE_DIR / 'ga_summary.json'}")

    return candidate_rules, total_unique


if __name__ == "__main__":
    main()
