#!/usr/bin/env python3
"""
generate_warm_start_215.py — Build a 100-rule warm-start population for iter_215.

Seeds:
  1. iter_213 champion  (transient drift oscillator)  → archive/iter_213.10/results/champion_rule.json
  2. iter_177 champion  (transient bloomer, iter_176 gen5 rule_019) → archive/iter_176/results/gen_5/rule_019.json
  3. iter_153 rule_021  (fast puffer)  → archive/iter_153/results/population_gen3.json

Output: archive/iter_215/results/warm_start_population.json
  {
    "description": "...",
    "seeds": [ {rule_id, source, rule_dict, chromosome}, ... ],
    "population": [ {rule_id, parent, rule_dict, chromosome}, ... ]
  }
The outer "population" list has all 100 entries (3 seeds + 97 mutants).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
LUT_SIZE = 128


# ── Chromosome helpers (matches run_vc_search.py) ──────────────────────────────

def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[str(s)] = int(v)
    return out


def per_bit_mutation(chrom: np.ndarray, rate: float, rng: random.Random) -> np.ndarray:
    result = chrom.copy()
    for i in range(len(result)):
        if rng.random() < rate:
            result[i] ^= 1
    return result


# ── Load seed rules ────────────────────────────────────────────────────────────

def load_iter213_champion() -> dict:
    path = PROJECT_ROOT / "archive" / "iter_213.10" / "results" / "champion_rule.json"
    with open(path) as f:
        data = json.load(f)
    return {str(k): int(v) for k, v in data["rule_dict"].items()}


def load_iter177_champion() -> dict:
    path = PROJECT_ROOT / "archive" / "iter_176" / "results" / "gen_5" / "rule_019.json"
    with open(path) as f:
        data = json.load(f)
    return {str(k): int(v) for k, v in data["rule"].items()}


def load_iter153_champion() -> dict:
    path = PROJECT_ROOT / "archive" / "iter_153" / "results" / "population_gen3.json"
    with open(path) as f:
        population = json.load(f)
    return {str(k): int(v) for k, v in population["rule_021"].items()}


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    rng = random.Random(215_001)
    output_path = PROJECT_ROOT / "archive" / "iter_215" / "results" / "warm_start_population.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load the three seed rules
    seeds_raw = [
        ("iter_213_champion",  "transient_drift_oscillator", load_iter213_champion()),
        ("iter_177_champion",  "transient_bloomer",          load_iter177_champion()),
        ("iter_153_rule_021",  "fast_puffer",                load_iter153_champion()),
    ]

    seeds = []
    for rule_id, source, rule_dict in seeds_raw:
        chrom = rule_dict_to_chromosome(rule_dict)
        seeds.append({
            "rule_id": rule_id,
            "source": source,
            "rule_dict": rule_dict,
            "chromosome": chrom.tolist(),
            "non_identity_entries": int(np.sum(chrom != ((np.arange(LUT_SIZE) >> 6) & 1))),
        })
        print(f"  Seed: {rule_id:30s}  non_identity_entries={seeds[-1]['non_identity_entries']}")

    # Generate 97 mutants: ~33 from seed 0, ~32 from seed 1, ~32 from seed 2
    mutant_counts = [33, 32, 32]
    # Use a graduated mutation rate: mix of subtle and aggressive
    # rates sampled from [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]
    mutation_rates = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]

    population = []

    # First 3 entries: the seeds themselves
    for i, seed in enumerate(seeds):
        population.append({
            "rule_id": f"rule_{i+1:03d}",
            "parent": seed["rule_id"],
            "mutation_rate": 0.0,
            "rule_dict": seed["rule_dict"],
            "chromosome": seed["chromosome"],
        })

    # Remaining 97: mutants
    rule_idx = 4
    for seed_i, n_mutants in enumerate(mutant_counts):
        seed_chrom = np.array(seeds[seed_i]["chromosome"], dtype=np.uint8)
        parent_id = seeds[seed_i]["rule_id"]
        for _ in range(n_mutants):
            rate = rng.choice(mutation_rates)
            mutant_chrom = per_bit_mutation(seed_chrom, rate, rng)
            mutant_rule_dict = chromosome_to_rule_dict(mutant_chrom)
            population.append({
                "rule_id": f"rule_{rule_idx:03d}",
                "parent": parent_id,
                "mutation_rate": rate,
                "rule_dict": mutant_rule_dict,
                "chromosome": mutant_chrom.tolist(),
            })
            rule_idx += 1

    assert len(population) == 100, f"Expected 100, got {len(population)}"

    payload = {
        "description": (
            "Warm-start population for iter_215 evolutionary search. "
            "Rules 1-3 are champions from iter_213 (transient drift oscillator), "
            "iter_177 (transient bloomer), and iter_153 (fast puffer). "
            "Rules 4-100 are per-bit mutations of those seeds."
        ),
        "seed_sources": {
            "rule_001": "archive/iter_213.10/results/champion_rule.json",
            "rule_002": "archive/iter_176/results/gen_5/rule_019.json",
            "rule_003": "archive/iter_153/results/population_gen3.json::rule_021",
        },
        "mutation_rates_used": mutation_rates,
        "population_size": len(population),
        "population": population,
    }

    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nWrote {len(population)} rules to {output_path}")
    print(f"  Seeds:   3")
    print(f"  Mutants: {len(population) - 3}")
    print(f"  Mutation rate distribution (mutants only):")
    rate_counts: dict[float, int] = {}
    for entry in population[3:]:
        r = entry["mutation_rate"]
        rate_counts[r] = rate_counts.get(r, 0) + 1
    for r, cnt in sorted(rate_counts.items()):
        print(f"    rate={r:.2f}  count={cnt}")


if __name__ == "__main__":
    main()
