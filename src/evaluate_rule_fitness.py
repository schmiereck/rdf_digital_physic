#!/usr/bin/env python3
"""
evaluate_rule_fitness.py

Evaluates 20 random rules from archive/iter_082/rules/ using a 100x100
toroidal hexagonal grid initialized with 50% random noise, simulated for
500 steps. Computes a fitness score that rewards sustained complexity.

Fitness = mean(bit_count_last_100_steps) * stddev(bit_count_all_steps)
A rule that dies or freezes will have stddev ~ 0, yielding fitness ~ 0.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RULES_DIR = PROJECT_ROOT / "archive" / "iter_082" / "rules"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_082" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_082" / "result.yaml"

GRID_SIZE = 100
STEPS = 500
FILL_RATE = 0.5
RNG_SEED = 42

# Hex directions (MSB encoding): b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE
HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


def load_rule_array(path: Path) -> np.ndarray:
    with open(path) as f:
        raw = json.load(f)
    rule = np.arange(128, dtype=np.int32)
    for k, v in raw.items():
        rule[int(k)] = int(v)
    return rule


def step_ca(grid: np.ndarray, rule: np.ndarray) -> np.ndarray:
    """One synchronous CA step on a toroidal grid using the rule lookup array."""
    state = grid.astype(np.int32) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        neighbor = np.roll(np.roll(grid, -dq, axis=0), -dr, axis=1)
        state |= neighbor.astype(np.int32) << (5 - i)
    return ((rule[state] >> 6) & 1).astype(np.int8)


def classify(final_count: int, stddev: float, mean_all: float) -> str:
    if final_count == 0:
        return "death"
    if stddev == 0.0:
        return "static"      # grid freezes instantly, no change at all
    if stddev < 50:
        return "low_dynamic"  # slow drift, limited variability
    return "high_dynamic"    # sustained, complex activity


def evaluate_rule(rule_path: Path, rng: np.random.Generator) -> dict:
    rule = load_rule_array(rule_path)
    grid = rng.integers(0, 2, (GRID_SIZE, GRID_SIZE), dtype=np.int8)

    bit_counts = np.empty(STEPS + 1, dtype=np.int32)
    bit_counts[0] = int(grid.sum())

    for t in range(1, STEPS + 1):
        grid = step_ca(grid, rule)
        bit_counts[t] = int(grid.sum())

    last_100 = bit_counts[-100:]
    mean_last_100 = float(np.mean(last_100))
    mean_all = float(np.mean(bit_counts))
    stddev_all = float(np.std(bit_counts))
    final_count = int(bit_counts[-1])

    fitness = mean_last_100 * stddev_all if stddev_all > 0 else 0.0

    return {
        "fitness": fitness,
        "final_bit_count": final_count,
        "mean_bit_count": mean_all,
        "stddev_bit_count": stddev_all,
        "behavior_class": classify(final_count, stddev_all, mean_all),
    }


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_files = sorted(RULES_DIR.glob("random_rule_*.json"))
    if not rule_files:
        print(f"ERROR: no rule files found in {RULES_DIR}", file=sys.stderr)
        return 1
    print(f"Found {len(rule_files)} rule files. Simulating {STEPS} steps on "
          f"{GRID_SIZE}x{GRID_SIZE} grid ({FILL_RATE*100:.0f}% fill).\n")

    rng = np.random.default_rng(RNG_SEED)
    rows = []

    for rule_path in rule_files:
        rule_id = rule_path.stem
        metrics = evaluate_rule(rule_path, rng)
        print(f"  {rule_id}: fitness={metrics['fitness']:10.1f}  "
              f"final={metrics['final_bit_count']:5d}  "
              f"mean={metrics['mean_bit_count']:7.1f}  "
              f"std={metrics['stddev_bit_count']:7.2f}  "
              f"class={metrics['behavior_class']}")
        rows.append({
            "rule_id": rule_id,
            "fitness_score": round(metrics["fitness"], 4),
            "final_bit_count": metrics["final_bit_count"],
            "mean_bit_count": round(metrics["mean_bit_count"], 4),
            "stddev_bit_count": round(metrics["stddev_bit_count"], 4),
        })

    csv_path = RESULTS_DIR / "fitness_scores.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["rule_id", "fitness_score", "final_bit_count",
                        "mean_bit_count", "stddev_bit_count"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {csv_path}")

    scores = np.array([r["fitness_score"] for r in rows])
    min_fitness = float(scores.min())
    max_fitness = float(scores.max())
    variance = float(np.var(scores))

    # Classify behaviors for summary
    class_counts: dict[str, int] = {"death": 0, "static": 0, "low_dynamic": 0, "high_dynamic": 0}
    for rule_path in rule_files:
        rule_id = rule_path.stem
        row = next(r for r in rows if r["rule_id"] == rule_id)
        final = row["final_bit_count"]
        std = row["stddev_bit_count"]
        cls = classify(final, std, row["mean_bit_count"])
        class_counts[cls] += 1

    distinct_classes = sum(1 for v in class_counts.values() if v > 0)

    print(f"\n=== Summary ===")
    print(f"  min_fitness:       {min_fitness:.2f}")
    print(f"  max_fitness:       {max_fitness:.2f}")
    print(f"  variance_of_scores: {variance:.2f}")
    print(f"  class distribution: {class_counts}")
    print(f"  distinct_classes:  {distinct_classes}")
    print(f"  significant_variance (>1.0): {variance > 1.0}")

    result = {
        "min_fitness": float(min_fitness),
        "max_fitness": float(max_fitness),
        "variance_of_scores": float(variance),
        "class_distribution": class_counts,
        "distinct_classes_found": distinct_classes,
        "significant_variance": bool(variance > 1.0),
        "num_rules_evaluated": len(rows),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
