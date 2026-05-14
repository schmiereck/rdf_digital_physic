#!/usr/bin/env python3
"""
run_iter_173_evo.py — 3-generation evolutionary search using StableVelocityFitness.

- Population: 100 C2-symmetric rules per generation
- Generations: 0, 1, 2 (3 total)
- Seed: L-tromino (3 asymmetric bits) on 128x128 toroidal hex grid
- Fitness: StableVelocityFitness (see fitness_stable_velocity.py)
- Selection: top 10 elites carried forward, rest bred via mutation + crossover
- Goal: discover at least one rule in Gen 2 with fitness > 0.5

Outputs:
  archive/iter_173/results/gen2_population.csv   (final population, IDs + fitness)
  archive/iter_173/results/champion_rule.json    (rule dict of top Gen-2 rule)
"""

import concurrent.futures
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import (
    _try_build_c2_rule,
    generate_random_c2_rule,
)
from fitness_stable_velocity import evaluate as eval_stable_velocity

PROJECT_ROOT  = Path(__file__).parent.parent
OUTPUT_DIR    = PROJECT_ROOT / "archive" / "iter_173" / "results"
GEN_POPS_DIR  = OUTPUT_DIR / "populations"

POPULATION_SIZE = 100
ELITE_FRACTION  = 0.10
ELITE_SIZE      = int(POPULATION_SIZE * ELITE_FRACTION)   # 10
N_GENERATIONS   = 3      # Gen 0, 1, 2
RULE_SEED       = 173
MAX_WORKERS     = 4
FITNESS_GOAL    = 0.5


# ── Breeding helpers (same scheme as iter_171_evo) ────────────────────────────

def extract_base_pairs(rule_dict: dict) -> list:
    seen, pairs = set(), []
    for a, b in rule_dict.items():
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            pairs.append((a, b))
    return pairs


def mutate_rule(parent_rule: dict, rng: random.Random,
                drop_rate: float = 0.4) -> dict:
    parent_pairs = extract_base_pairs(parent_rule)
    for _ in range(2000):
        kept  = [p for p in parent_pairs if rng.random() > drop_rate]
        n_new = rng.randint(1, 4)
        new_p = kept[:]
        for _ in range(n_new):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            new_p.append((a, b))
        if not new_p:
            continue
        rule = _try_build_c2_rule(new_p)
        if rule is not None:
            return rule
    return generate_random_c2_rule(rng)


def crossover_rules(p1: dict, p2: dict, rng: random.Random) -> dict:
    pairs1 = extract_base_pairs(p1)
    pairs2 = extract_base_pairs(p2)
    for _ in range(2000):
        s1 = rng.sample(pairs1, rng.randint(1, max(1, len(pairs1))))
        s2 = rng.sample(pairs2, rng.randint(1, max(1, len(pairs2))))
        rule = _try_build_c2_rule(s1 + s2)
        if rule is not None:
            return rule
    return generate_random_c2_rule(rng)


def breed_next_generation(elite: list, rng: random.Random) -> list:
    elite_rules = [e["rule_dict"] for e in elite]
    children    = list(elite_rules)            # elitism: carry forward top N

    while len(children) < POPULATION_SIZE:
        roll = rng.random()
        if roll < 0.55 or len(elite_rules) < 2:
            parent = rng.choice(elite_rules)
            children.append(mutate_rule(parent, rng))
        else:
            p1, p2 = rng.sample(elite_rules, 2)
            children.append(crossover_rules(p1, p2, rng))

    return children


# ── Parallel evaluation ───────────────────────────────────────────────────────

def _eval_worker(args: tuple) -> dict:
    rule_id, rule_dict = args
    m = eval_stable_velocity(rule_dict)
    return {"rule_id": rule_id, "rule_dict": rule_dict, **m}


def evaluate_population(rule_pairs: list) -> list:
    population = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_eval_worker, r): r[0] for r in rule_pairs}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            if done % 25 == 0 or done == len(rule_pairs):
                print(
                    f"    [{done:3d}/{len(rule_pairs)}] last: {result['rule_id']} "
                    f"fit={result['fitness']:.6f} "
                    f"v={result['mean_velocity']:.4f} "
                    f"std={result['std_dev_velocity']:.4f} "
                    f"bits={result['final_bit_count']}"
                )
    population.sort(key=lambda e: e["fitness"], reverse=True)
    return population


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GEN_POPS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== iter_173 — 3-Generation Evolutionary Search ===")
    print("Fitness: StableVelocityFitness")
    print(f"Seed: {RULE_SEED}  |  Pop: {POPULATION_SIZE}  |  Elite: {ELITE_SIZE}  "
          f"|  Gens: {N_GENERATIONS} (0..{N_GENERATIONS - 1})  |  Goal: > {FITNESS_GOAL}")

    rng = random.Random(RULE_SEED)

    # ── Generation 0 ──────────────────────────────────────────────────────────
    print(f"\n--- Generation 0: seeding {POPULATION_SIZE} random C2 rules ---")
    rules_gen0 = []
    for i in range(1, POPULATION_SIZE + 1):
        rd = generate_random_c2_rule(rng)
        rules_gen0.append((f"g0_rule_{i:03d}", rd))
    print(f"  Evaluating …")
    current_pop = evaluate_population(rules_gen0)
    gen_max  = current_pop[0]["fitness"]
    gen_mean = float(np.mean([e["fitness"] for e in current_pop]))
    print(f"  Gen-0  max={gen_max:.8f}  mean={gen_mean:.8f}  top={current_pop[0]['rule_id']}")

    max_by_gen  = [gen_max]
    mean_by_gen = [gen_mean]
    populations = {0: current_pop}

    # ── Generations 1 .. N_GENERATIONS-1 ─────────────────────────────────────
    for gen in range(1, N_GENERATIONS):
        elite = current_pop[:ELITE_SIZE]
        print(f"\n--- Generation {gen}: breeding from top {ELITE_SIZE} ---")
        print(f"  Elite fitness range: [{elite[-1]['fitness']:.6f}, "
              f"{elite[0]['fitness']:.6f}]")

        child_rules = breed_next_generation(elite, rng)
        rule_pairs  = [(f"g{gen}_rule_{i+1:03d}", rd)
                       for i, rd in enumerate(child_rules)]
        print(f"  Evaluating {len(rule_pairs)} rules …")
        current_pop = evaluate_population(rule_pairs)

        gen_max  = current_pop[0]["fitness"]
        gen_mean = float(np.mean([e["fitness"] for e in current_pop]))
        print(f"  Gen-{gen}  max={gen_max:.8f}  mean={gen_mean:.8f}  "
              f"top={current_pop[0]['rule_id']}")
        max_by_gen.append(gen_max)
        mean_by_gen.append(gen_mean)
        populations[gen] = current_pop

    # ── Save per-generation snapshots (JSON) ──────────────────────────────────
    for gen, pop in populations.items():
        snapshot = {
            "generation":   gen,
            "max_fitness":  round(pop[0]["fitness"], 10),
            "mean_fitness": round(float(np.mean([e["fitness"] for e in pop])), 10),
            "population": [
                {
                    "rule_id":          e["rule_id"],
                    "fitness":          round(e["fitness"], 10),
                    "mean_velocity":    round(e["mean_velocity"], 8),
                    "std_dev_velocity": round(e["std_dev_velocity"], 8),
                    "final_bit_count":  e["final_bit_count"],
                    "rule":             {str(k): v for k, v in e["rule_dict"].items()},
                }
                for e in pop
            ],
        }
        path = GEN_POPS_DIR / f"gen{gen}_population.json"
        with open(path, "w") as f:
            json.dump(snapshot, f, indent=2)
        print(f"Saved snapshot: {path}")

    # ── Save required CSV of final-generation population ──────────────────────
    final_pop = populations[N_GENERATIONS - 1]
    csv_path  = OUTPUT_DIR / "gen2_population.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rule_id", "fitness_score", "mean_velocity",
            "std_dev_velocity", "initial_bit_count", "final_bit_count",
        ])
        for e in final_pop:
            writer.writerow([
                e["rule_id"],
                f"{e['fitness']:.10f}",
                f"{e['mean_velocity']:.8f}",
                f"{e['std_dev_velocity']:.8f}",
                e["initial_bit_count"],
                e["final_bit_count"],
            ])
    print(f"\nSaved final-pop CSV: {csv_path}")

    # ── Save champion rule dict ───────────────────────────────────────────────
    champion = final_pop[0]
    champion_path = OUTPUT_DIR / "champion_rule.json"
    with open(champion_path, "w") as f:
        json.dump(
            {str(k): v for k, v in champion["rule_dict"].items()},
            f, indent=2, sort_keys=True,
        )
    print(f"Saved champion rule: {champion_path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n=== Evolution Summary ===")
    for g in range(N_GENERATIONS):
        print(f"  Gen {g}: max={max_by_gen[g]:.8f}  mean={mean_by_gen[g]:.8f}")
    print(f"  Champion: {champion['rule_id']}  fitness={champion['fitness']:.8f}")
    print(f"     mean_velocity   = {champion['mean_velocity']:.6f}")
    print(f"     std_dev_velocity= {champion['std_dev_velocity']:.6f}")
    print(f"     final_bit_count = {champion['final_bit_count']}")
    print(f"     velocities      = {champion['velocities']}")
    goal_met = champion["fitness"] > FITNESS_GOAL
    print(f"  Goal (fitness > {FITNESS_GOAL}): "
          f"{'REACHED' if goal_met else 'NOT REACHED'}")

    return 0 if goal_met else 2


if __name__ == "__main__":
    sys.exit(main())
