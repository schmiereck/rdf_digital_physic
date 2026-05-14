#!/usr/bin/env python3
"""
run_iter_171.py  —  Single-generation validation of the conservation-aware fitness metric

Generates a fresh random population of 100 C2-symmetric rules and evaluates
each one with the new fitness function from evolution.py:

    fitness = displacement * (final_bit_count / (initial_bit_count + EPS))

Purpose: confirm that (a) the distribution of scores is meaningful (not
degenerate), and (b) annihilating rules are penalised with near-zero fitness.
"""

import concurrent.futures
import json
import sys
from pathlib import Path

import numpy as np

# project path so we can import sibling modules
sys.path.insert(0, str(Path(__file__).parent))

from evolution import (
    LTROMINO_CELLS,
    GRID_SIZE,
    STEPS,
    EPS,
    evaluate_rule,
    generate_random_c2_rule,
)
import random

PROJECT_ROOT   = Path(__file__).parent.parent
OUTPUT_DIR     = PROJECT_ROOT / "archive" / "iter_171" / "results"

POPULATION_SIZE = 100
RULE_SEED       = 171
FITNESS_THRESHOLD = 0.01


# ── Worker (must be importable at module level for ProcessPoolExecutor) ────────

def _eval_worker(args: tuple) -> dict:
    rule_id, rule_dict = args
    result = evaluate_rule(rule_dict)
    return {"rule_id": rule_id, "rule_dict": rule_dict, **result}


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== iter_171: Conservation-Aware Fitness Validation ===")
    print(f"Fitness formula: displacement * (final_bit_count / (initial_bit_count + {EPS}))")
    print(f"L-tromino seed:  {LTROMINO_CELLS}")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Steps: {STEPS}")
    print(f"\nGenerating {POPULATION_SIZE} C2 rules (seed={RULE_SEED}) ...")

    rng   = random.Random(RULE_SEED)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict = generate_random_c2_rule(rng)
        rules.append((f"rule_{i:03d}", rule_dict))
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE}")

    print(f"\nEvaluating {POPULATION_SIZE} rules ...")

    population = []
    workers    = min(4, POPULATION_SIZE)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_eval_worker, r): r[0] for r in rules}
        done    = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            print(
                f"  [{done:3d}/{POPULATION_SIZE}] {result['rule_id']}: "
                f"fitness={result['fitness']:.6f}  "
                f"disp={result['displacement']:.4f}  "
                f"bits={result['final_bit_count']:3d}"
            )

    population.sort(key=lambda e: e["fitness"], reverse=True)

    fitnesses          = [e["fitness"] for e in population]
    max_fitness        = float(max(fitnesses))
    mean_fitness       = float(np.mean(fitnesses))
    min_fitness        = float(min(fitnesses))
    rules_above_thresh = sum(1 for f in fitnesses if f > FITNESS_THRESHOLD)

    # Annihilating rules: final_bit_count == 0
    annihilated = [e for e in population if e["final_bit_count"] == 0]
    annihilated_fitnesses = [e["fitness"] for e in annihilated]
    max_annihilated_fitness = float(max(annihilated_fitnesses)) if annihilated else 0.0

    print(f"\n=== Summary ===")
    print(f"  max_fitness:            {max_fitness:.8f}")
    print(f"  mean_fitness:           {mean_fitness:.8f}")
    print(f"  min_fitness:            {min_fitness:.8f}")
    print(f"  rules_above_{FITNESS_THRESHOLD}: {rules_above_thresh}")
    print(f"  annihilating_rules:     {len(annihilated)}")
    print(f"  max_fitness_annihilat.: {max_annihilated_fitness:.8f}")
    print(f"  top_rule:               {population[0]['rule_id']}")
    print(f"  top_displacement:       {population[0]['displacement']:.6f}")
    print(f"  top_final_bits:         {population[0]['final_bit_count']}")

    results = {
        "experiment":           "iter_171_conservation_fitness_validation",
        "fitness_formula":      "displacement * (final_bit_count / (initial_bit_count + EPS))",
        "eps":                  EPS,
        "grid_size":            GRID_SIZE,
        "steps":                STEPS,
        "rule_seed":            RULE_SEED,
        "ltromino_cells":       LTROMINO_CELLS,
        "population_size":      POPULATION_SIZE,
        "max_fitness":          round(max_fitness,  10),
        "mean_fitness":         round(mean_fitness, 10),
        "min_fitness":          round(min_fitness,  10),
        "rules_above_threshold": rules_above_thresh,
        "fitness_threshold":    FITNESS_THRESHOLD,
        "annihilating_rules":   len(annihilated),
        "max_annihilated_fitness": round(max_annihilated_fitness, 10),
        "population": [
            {
                "rule_id":           e["rule_id"],
                "rule":              {str(k): v for k, v in e["rule_dict"].items()},
                "fitness":           round(e["fitness"],          10),
                "displacement":      round(e["displacement"],      8),
                "final_bit_count":   e["final_bit_count"],
                "initial_bit_count": e["initial_bit_count"],
                "final_com":         [round(x, 4) for x in e["final_com"]],
                "initial_com":       [round(x, 4) for x in e["initial_com"]],
            }
            for e in population
        ],
    }

    out_path = OUTPUT_DIR / "gen_0_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
