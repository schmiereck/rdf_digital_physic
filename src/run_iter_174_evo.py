#!/usr/bin/env python3
"""
run_iter_174_evo.py — Continue iter_173 evolution for 11 more generations
(gen 3 .. gen 13) using StableVelocityFitness on the asymmetric L-tromino seed.

Inputs:
  archive/iter_173/results/populations/gen2_population.json

Outputs:
  archive/iter_174/results/populations/gen{N}_population.json   for N in 3..13
  archive/iter_174/results/gen_13_population.json               (final pop)
  archive/iter_174/results/best_rule.json                       (best rule across all gens)
  archive/iter_174/results/evolution_log.csv                    (per-gen summary)
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

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_GEN2   = PROJECT_ROOT / "archive" / "iter_173" / "results" / "populations" / "gen2_population.json"
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_174" / "results"
GEN_POPS_DIR = OUTPUT_DIR / "populations"

POPULATION_SIZE = 100
ELITE_FRACTION  = 0.10
ELITE_SIZE      = int(POPULATION_SIZE * ELITE_FRACTION)   # 10
START_GEN       = 3
END_GEN         = 13      # inclusive — produces gens 3..13 (11 new gens)
RULE_SEED       = 174
MAX_WORKERS     = 4


# ── Breeding helpers (same scheme as iter_173_evo) ────────────────────────────

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


# ── Population I/O ────────────────────────────────────────────────────────────

def load_population(path: Path) -> list:
    """Load a previously-saved population snapshot. Returns a list of dicts
    with the same shape as evaluate_population() output (sorted by fitness)."""
    with open(path) as f:
        snap = json.load(f)
    pop = []
    for e in snap["population"]:
        rule_dict = {int(k): int(v) for k, v in e["rule"].items()}
        pop.append({
            "rule_id":          e["rule_id"],
            "rule_dict":        rule_dict,
            "fitness":          float(e["fitness"]),
            "mean_velocity":    float(e["mean_velocity"]),
            "std_dev_velocity": float(e["std_dev_velocity"]),
            "initial_bit_count": 3,
            "final_bit_count":  int(e["final_bit_count"]),
            "velocities":       [],
            "com_checkpoints":  {},
        })
    pop.sort(key=lambda e: e["fitness"], reverse=True)
    return pop


def save_population_snapshot(gen: int, pop: list, path: Path) -> None:
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
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GEN_POPS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== iter_174 — Continued Evolution (StableVelocityFitness) ===")
    print(f"Loading gen-2 population from: {INPUT_GEN2}")
    gen2_pop = load_population(INPUT_GEN2)
    gen2_max  = gen2_pop[0]["fitness"]
    gen2_mean = float(np.mean([e["fitness"] for e in gen2_pop]))
    print(f"  Loaded {len(gen2_pop)} rules.  "
          f"max={gen2_max:.8f}  mean={gen2_mean:.8f}  "
          f"top={gen2_pop[0]['rule_id']}")
    print(f"Pop: {POPULATION_SIZE}  |  Elite: {ELITE_SIZE}  |  "
          f"Gens: {START_GEN}..{END_GEN}")

    rng = random.Random(RULE_SEED)

    # Track per-generation stats; we keep gen-2 stats as the starting point.
    log_rows = [{
        "generation":   2,
        "max_fitness":  gen2_max,
        "mean_fitness": gen2_mean,
        "best_rule_id": gen2_pop[0]["rule_id"],
    }]

    # Track best rule found across ALL generations (start with gen-2 champion).
    best_overall = dict(gen2_pop[0])

    current_pop = gen2_pop
    final_pop   = gen2_pop  # safety default; overwritten in the loop

    for gen in range(START_GEN, END_GEN + 1):
        elite = current_pop[:ELITE_SIZE]
        print(f"\n--- Generation {gen}: breeding from top {ELITE_SIZE} of gen {gen - 1} ---")
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

        log_rows.append({
            "generation":   gen,
            "max_fitness":  gen_max,
            "mean_fitness": gen_mean,
            "best_rule_id": current_pop[0]["rule_id"],
        })

        if gen_max > best_overall["fitness"]:
            best_overall = dict(current_pop[0])

        snapshot_path = GEN_POPS_DIR / f"gen{gen}_population.json"
        save_population_snapshot(gen, current_pop, snapshot_path)
        print(f"  Saved snapshot: {snapshot_path}")

        final_pop = current_pop

    # ── Save required final population JSON ──────────────────────────────────
    final_path = OUTPUT_DIR / "gen_13_population.json"
    save_population_snapshot(END_GEN, final_pop, final_path)
    print(f"\nSaved final population: {final_path}")

    # ── Save best rule across all generations ────────────────────────────────
    best_path = OUTPUT_DIR / "best_rule.json"
    with open(best_path, "w") as f:
        json.dump({
            "rule_id":           best_overall["rule_id"],
            "fitness":           best_overall["fitness"],
            "mean_velocity":     best_overall["mean_velocity"],
            "std_dev_velocity":  best_overall["std_dev_velocity"],
            "initial_bit_count": best_overall.get("initial_bit_count", 3),
            "final_bit_count":   best_overall["final_bit_count"],
            "rule":              {str(k): v for k, v in best_overall["rule_dict"].items()},
        }, f, indent=2, sort_keys=True)
    print(f"Saved best rule: {best_path}")

    # ── Save evolution log CSV ───────────────────────────────────────────────
    log_path = OUTPUT_DIR / "evolution_log.csv"
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["generation", "max_fitness", "mean_fitness", "best_rule_id"])
        for row in log_rows:
            writer.writerow([
                row["generation"],
                f"{row['max_fitness']:.10f}",
                f"{row['mean_fitness']:.10f}",
                row["best_rule_id"],
            ])
    print(f"Saved evolution log: {log_path}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n=== Evolution Summary ===")
    for row in log_rows:
        print(f"  Gen {row['generation']:2d}: "
              f"max={row['max_fitness']:.8f}  "
              f"mean={row['mean_fitness']:.8f}  "
              f"top={row['best_rule_id']}")
    print(f"\nBest overall: {best_overall['rule_id']}  "
          f"fitness={best_overall['fitness']:.8f}  "
          f"mean_v={best_overall['mean_velocity']:.6f}  "
          f"std_v={best_overall['std_dev_velocity']:.6f}  "
          f"bits={best_overall['final_bit_count']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
