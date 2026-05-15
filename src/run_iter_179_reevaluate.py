#!/usr/bin/env python3
"""
run_iter_179_reevaluate.py

Re-evaluate the population from iter_176's evolutionary run using CheckpointFitness.
Since archive/iter_176/results/final_population.json was never saved (only the champion
rule was persisted), we use the last complete population from iter_174 (gen_13) plus the
iter_176 champion as the effective "final population of iter_176".

CheckpointFitness: L-tromino seed, bit-count stability checked at steps 50, 100, 150, 200.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fitness import CheckpointFitness
from rule import Rule

# L-tromino seed matching LTROMINO_CELLS in evolution.py
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]

ARCHIVE_ROOT = Path(__file__).parent.parent / "archive"
OUTPUT_DIR   = ARCHIVE_ROOT / "iter_179" / "results"

FINAL_POP_PATH    = ARCHIVE_ROOT / "iter_176" / "results" / "final_population.json"
ITER174_POP_PATH  = ARCHIVE_ROOT / "iter_174" / "results" / "gen_13_population.json"
ITER176_CHAMP_PATH = ARCHIVE_ROOT / "iter_176" / "results" / "gen_5" / "rule_019.json"


def _rule_hash(rule_dict: dict) -> str:
    encoded = json.dumps(rule_dict, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def load_population() -> list[dict]:
    """Load rules from the best available source."""
    if FINAL_POP_PATH.exists():
        print(f"Loading population from {FINAL_POP_PATH}")
        with open(FINAL_POP_PATH) as f:
            data = json.load(f)
        return [entry["rule"] for entry in data["population"]]

    print(f"[WARNING] {FINAL_POP_PATH} not found. Falling back to iter_174 gen_13 population.")
    rules = []

    if ITER174_POP_PATH.exists():
        with open(ITER174_POP_PATH) as f:
            data = json.load(f)
        for entry in data["population"]:
            rules.append(entry["rule"])
        print(f"  Loaded {len(rules)} rules from iter_174 gen_13 population.")
    else:
        print(f"[ERROR] iter_174 population not found at {ITER174_POP_PATH}")

    # Also include the iter_176 champion
    if ITER176_CHAMP_PATH.exists():
        with open(ITER176_CHAMP_PATH) as f:
            champ = json.load(f)
        rules.append(champ["rule"])
        print(f"  Added iter_176 champion rule (gen_5/rule_019).")

    return rules


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metric = CheckpointFitness(
        checkpoints=[50, 100, 150, 200],
        simulation_steps=200,
    )

    rules = load_population()
    if not rules:
        print("[ERROR] No rules to evaluate.")
        sys.exit(1)

    print(f"\nEvaluating {len(rules)} rules with CheckpointFitness (L-tromino seed)...")
    print(f"Checkpoints: {sorted(metric.checkpoints)}, Steps: {metric.simulation_steps}\n")

    results = []
    for i, rule_dict in enumerate(rules):
        rule_obj = Rule(rule_dict)
        score = metric.evaluate(rule_obj, LTROMINO_CELLS)
        h = _rule_hash(rule_dict)
        results.append((h, score))
        if (i + 1) % 10 == 0 or score > 0.0:
            print(f"  [{i+1}/{len(rules)}] hash={h} score={score:.6f}")

    # Sort by descending score
    results.sort(key=lambda x: x[1], reverse=True)

    out_csv = OUTPUT_DIR / "reevaluation_scores.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rule_hash", "fitness_score"])
        for h, score in results:
            writer.writerow([h, f"{score:.8f}"])

    print(f"\nResults saved to {out_csv}")

    top_score = results[0][1] if results else 0.0
    print(f"\nTop fitness score:  {top_score:.8f}")
    print(f"Rules scoring > 0: {sum(1 for _, s in results if s > 0.0)}")
    print(f"Total rules:       {len(results)}")

    return top_score


if __name__ == "__main__":
    main()
