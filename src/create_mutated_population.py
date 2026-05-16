"""
Create a warm-start population by mutating a known glider rule.

Each population member is a mutated clone of the parent rule. Mutations
are swaps of two randomly chosen output states, preserving bijectivity.
"""

import argparse
import json
import random


def mutate(chromosome: list, num_swaps: int) -> list:
    clone = chromosome[:]
    for _ in range(num_swaps):
        i, j = random.sample(range(len(clone)), 2)
        clone[i], clone[j] = clone[j], clone[i]
    return clone


def main():
    parser = argparse.ArgumentParser(description="Create a warm-start mutated population.")
    parser.add_argument("--parent_rule_path", required=True, help="Path to the parent rule JSON file.")
    parser.add_argument("--population_size", type=int, required=True)
    parser.add_argument("--mutation_rate", type=float, required=True)
    parser.add_argument("--output_path", required=True, help="Path to write the output JSON file.")
    args = parser.parse_args()

    with open(args.parent_rule_path) as f:
        parent = json.load(f)

    chromosome = parent.get("chromosome", parent.get("lookup_table"))
    if chromosome is None:
        raise ValueError("Parent rule file must contain a 'chromosome' or 'lookup_table' key.")

    num_swaps = max(1, round(args.mutation_rate * len(chromosome)))
    print(f"Parent rule: {parent.get('rule_id', 'unknown')}")
    print(f"Chromosome length: {len(chromosome)}")
    print(f"Mutation rate: {args.mutation_rate} -> {num_swaps} swaps per clone")
    print(f"Generating {args.population_size} members...")

    population = []
    for i in range(args.population_size):
        mutated = mutate(chromosome, num_swaps)
        population.append({
            "rule_id": f"mutant_{i:04d}",
            "parent_rule_id": parent.get("rule_id", "unknown"),
            "chromosome": mutated,
        })

    import os
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)

    with open(args.output_path, "w") as f:
        json.dump(population, f, indent=2)

    print(f"Saved {len(population)} rules to {args.output_path}")


if __name__ == "__main__":
    main()
