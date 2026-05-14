#!/usr/bin/env python3
"""
run_iter_171_evo.py  —  3-generation evolutionary search using conservation-aware fitness

Uses the same initial random population seed (171) as iter_171.1.
Top 10% of each generation (10 individuals) breed the next 100.
Breeding: elitism + mutation + crossover, all preserving C2 symmetry.

Fitness = displacement * (final_bit_count / (initial_bit_count + EPS))
"""

import concurrent.futures
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import (
    EPS,
    GRID_SIZE,
    LTROMINO_CELLS,
    STEPS,
    _rotate_c2,
    _try_build_c2_rule,
    evaluate_rule,
    generate_random_c2_rule,
)

PROJECT_ROOT     = Path(__file__).parent.parent
OUTPUT_BASE      = PROJECT_ROOT / "archive" / "iter_171" / "results"
GEN3_OUTPUT_DIR  = OUTPUT_BASE / "gen3_population"

POPULATION_SIZE  = 100
ELITE_FRACTION   = 0.10          # top 10%
ELITE_SIZE       = int(POPULATION_SIZE * ELITE_FRACTION)   # 10
N_GENERATIONS    = 3
RULE_SEED        = 171           # same seed as iter_171.1
MAX_WORKERS      = 4


# ── Breeding helpers ──────────────────────────────────────────────────────────

def extract_base_pairs(rule_dict: dict) -> list:
    """Unique swap-pairs from a C2 rule (canonical a < b form)."""
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
    """Child = kept subset of parent pairs + fresh random pairs."""
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
    """Child = randomly sampled pairs from two parent rules."""
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
    """Return list of POPULATION_SIZE rule dicts for the next generation."""
    elite_rules = [e["rule_dict"] for e in elite]
    children    = list(elite_rules)            # elitism: carry forward top 10

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
    result = evaluate_rule(rule_dict)
    return {"rule_id": rule_id, "rule_dict": rule_dict, **result}


def evaluate_population(rule_pairs: list) -> list:
    """Evaluate (rule_id, rule_dict) pairs in parallel; return sorted results."""
    population = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_eval_worker, r): r[0] for r in rule_pairs}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            if done % 20 == 0 or done == len(rule_pairs):
                print(
                    f"    [{done:3d}/{len(rule_pairs)}] last: {result['rule_id']} "
                    f"fit={result['fitness']:.6f} "
                    f"disp={result['displacement']:.4f} "
                    f"bits={result['final_bit_count']}"
                )
    population.sort(key=lambda e: e["fitness"], reverse=True)
    return population


# ── Serialisation helpers ─────────────────────────────────────────────────────

def pop_to_json(population: list, gen: int, extra: dict = None) -> dict:
    base = {
        "generation":       gen,
        "fitness_formula":  "displacement * (final_bit_count / (initial_bit_count + EPS))",
        "eps":              EPS,
        "grid_size":        GRID_SIZE,
        "steps":            STEPS,
        "rule_seed":        RULE_SEED,
        "ltromino_cells":   LTROMINO_CELLS,
        "population_size":  len(population),
        "max_fitness":      round(population[0]["fitness"],    10),
        "mean_fitness":     round(float(np.mean([e["fitness"] for e in population])), 10),
        "min_fitness":      round(population[-1]["fitness"],   10),
    }
    if extra:
        base.update(extra)
    base["population"] = [
        {
            "rule_id":           e["rule_id"],
            "rule":              {str(k): v for k, v in e["rule_dict"].items()},
            "fitness":           round(e["fitness"],        10),
            "displacement":      round(e["displacement"],    8),
            "final_bit_count":   e["final_bit_count"],
            "initial_bit_count": e["initial_bit_count"],
            "final_com":         [round(x, 4) for x in e["final_com"]],
            "initial_com":       [round(x, 4) for x in e["initial_com"]],
        }
        for e in population
    ]
    return base


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    GEN3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== iter_171 — 3-Generation Evolutionary Search ===")
    print(f"Fitness: displacement * (final_bit_count / (initial_bit_count + EPS={EPS}))")
    print(f"Seed: {RULE_SEED}  |  Pop: {POPULATION_SIZE}  |  Elite: {ELITE_SIZE}  |  Gens: {N_GENERATIONS}")

    rng = random.Random(RULE_SEED)

    # ── Generation 0 (same as 171.1) ──────────────────────────────────────────
    print(f"\n--- Generation 0: seeding {POPULATION_SIZE} random C2 rules ---")
    rules_gen0 = []
    for i in range(1, POPULATION_SIZE + 1):
        rd = generate_random_c2_rule(rng)
        rules_gen0.append((f"g0_rule_{i:03d}", rd))
    print(f"  Evaluating …")
    pop_gen0 = evaluate_population(rules_gen0)
    gen0_max  = pop_gen0[0]["fitness"]
    gen0_mean = float(np.mean([e["fitness"] for e in pop_gen0]))
    print(f"  Gen-0  max={gen0_max:.8f}  mean={gen0_mean:.8f}  top={pop_gen0[0]['rule_id']}")

    out0 = pop_to_json(pop_gen0, 0)
    with open(OUTPUT_BASE / "evo_gen0_results.json", "w") as f:
        json.dump(out0, f, indent=2)

    max_by_gen = [gen0_max]
    current_pop = pop_gen0

    # ── Generations 1–3 ───────────────────────────────────────────────────────
    for gen in range(1, N_GENERATIONS + 1):
        elite = current_pop[:ELITE_SIZE]
        print(f"\n--- Generation {gen}: breeding from top {ELITE_SIZE} ---")
        print(f"  Elite fitness range: [{elite[-1]['fitness']:.6f}, {elite[0]['fitness']:.6f}]")

        child_rules = breed_next_generation(elite, rng)
        rule_pairs  = [(f"g{gen}_rule_{i+1:03d}", rd)
                       for i, rd in enumerate(child_rules)]
        print(f"  Evaluating {len(rule_pairs)} rules …")
        current_pop = evaluate_population(rule_pairs)

        gen_max  = current_pop[0]["fitness"]
        gen_mean = float(np.mean([e["fitness"] for e in current_pop]))
        print(f"  Gen-{gen}  max={gen_max:.8f}  mean={gen_mean:.8f}  top={current_pop[0]['rule_id']}")
        max_by_gen.append(gen_max)

        out = pop_to_json(current_pop, gen)
        path = OUTPUT_BASE / f"evo_gen{gen}_results.json"
        with open(path, "w") as f:
            json.dump(out, f, indent=2)

    # ── Final save: gen3 population ───────────────────────────────────────────
    print(f"\n--- Saving final population to {GEN3_OUTPUT_DIR} ---")
    final_pop = current_pop   # already gen 3

    final_out = pop_to_json(final_pop, N_GENERATIONS,
                             extra={"evolution_max_by_gen": max_by_gen})
    with open(GEN3_OUTPUT_DIR / "gen3_population.json", "w") as f:
        json.dump(final_out, f, indent=2)

    # Top rule standalone file
    top = final_pop[0]
    top_rule_out = {
        "rule_id":           top["rule_id"],
        "rule":              {str(k): v for k, v in top["rule_dict"].items()},
        "fitness":           round(top["fitness"],        10),
        "displacement":      round(top["displacement"],    8),
        "final_bit_count":   top["final_bit_count"],
        "initial_bit_count": top["initial_bit_count"],
        "final_com":         [round(x, 4) for x in top["final_com"]],
        "initial_com":       [round(x, 4) for x in top["initial_com"]],
        "generation":        N_GENERATIONS,
        "evolution_max_by_gen": max_by_gen,
    }
    with open(GEN3_OUTPUT_DIR / "top_rule.json", "w") as f:
        json.dump(top_rule_out, f, indent=2)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n=== Evolution Summary ===")
    for g, mx in enumerate(max_by_gen):
        print(f"  Gen {g}: max_fitness = {mx:.8f}")
    print(f"  Final top rule: {top['rule_id']}")
    print(f"  Final top fitness:    {top['fitness']:.8f}")
    print(f"  Final top disp:       {top['displacement']:.6f}")
    print(f"  Final top bits:       {top['final_bit_count']}")
    print(f"\nSaved: {GEN3_OUTPUT_DIR}/gen3_population.json")
    print(f"Saved: {GEN3_OUTPUT_DIR}/top_rule.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
