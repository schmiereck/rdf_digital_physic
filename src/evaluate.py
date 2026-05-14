#!/usr/bin/env python3
"""
evaluate.py — General-purpose rule evaluator.

Usage:
    python evaluate.py [--fitness-metric METRIC] rule.json [rule2.json ...]

Fitness metrics:
    conservation        displacement * (final_bits / initial_bits)  [default]
    velocity_stability  1 / (1 + std_dev_velocity)  over 3 windows
    StableVelocityFitness
                        (mean_v / (1 + std_v)) * (initial_bits / final_bits)
                        over 4 post-settling windows of 2000 total steps
"""

import argparse
import json
import sys
from pathlib import Path


def _load_rule(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _run_conservation(rule_dict: dict) -> dict:
    from evolution import evaluate_rule
    return evaluate_rule(rule_dict)


def _run_velocity_stability(rule_dict: dict) -> dict:
    import numpy as np
    from evolution import make_ltromino_grid
    from fitness import calculate_velocity_stability

    grid = make_ltromino_grid()
    fitness, velocities, std_dev = calculate_velocity_stability(rule_dict, grid)
    return {
        "fitness":           fitness,
        "velocities":        velocities,
        "std_dev_velocity":  std_dev,
    }


def _run_stable_velocity(rule_dict: dict) -> dict:
    import fitness_stable_velocity
    return fitness_stable_velocity.evaluate(rule_dict)


_METRICS = {
    "conservation":         _run_conservation,
    "velocity_stability":   _run_velocity_stability,
    "StableVelocityFitness": _run_stable_velocity,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate CA rules with a selectable fitness metric."
    )
    parser.add_argument(
        "--fitness-metric",
        choices=list(_METRICS),
        default="conservation",
        help="Fitness metric to apply (default: conservation)",
    )
    parser.add_argument(
        "rules",
        nargs="+",
        metavar="RULE_JSON",
        help="One or more rule JSON files to evaluate",
    )
    args = parser.parse_args(argv)

    evaluator = _METRICS[args.fitness_metric]

    print(f"Fitness metric: {args.fitness_metric}\n")

    for rule_path_str in args.rules:
        rule_path = Path(rule_path_str)
        if not rule_path.exists():
            print(f"ERROR: {rule_path} not found", file=sys.stderr)
            return 1

        rule_dict = _load_rule(rule_path)
        metrics   = evaluator(rule_dict)

        fitness = metrics.get("fitness", float("nan"))
        print(f"{rule_path.name}:")
        print(f"  fitness = {fitness:.6f}")
        for key, val in metrics.items():
            if key == "fitness":
                continue
            if isinstance(val, float):
                print(f"  {key} = {val:.6f}")
            else:
                print(f"  {key} = {val}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
