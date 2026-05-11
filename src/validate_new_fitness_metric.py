#!/usr/bin/env python3
"""
validate_new_fitness_metric.py

Tests a new fitness function: fitness = 1 / (1 + final_bit_count) after 500
steps from a single 4-bit T-shape seed on a 150x150 toroidal grid.

Rules evaluated:
  rule_023.json  – chaotic high-fitness rule (top from iter_084/iter_085)
  rule_056.json  – chaotic medium-fitness rule (median from iter_084/iter_086)
  symmetric_rule_nonconserving_A3_B14.json – stabilizing rule from iter_069
"""

import json
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT  = Path(__file__).parent.parent
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_084" / "population"
STABILIZING_RULE = PROJECT_ROOT / "src" / "symmetric_rule_nonconserving_A3_B14.json"
RESULTS_DIR   = PROJECT_ROOT / "archive" / "iter_087" / "results"
RESULT_YAML   = PROJECT_ROOT / "archive" / "iter_087" / "result.yaml"

GRID_SIZE = 150
STEPS     = 500

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


def load_rule_array(path: Path) -> np.ndarray:
    with open(path) as f:
        raw = json.load(f)
    rule = np.arange(128, dtype=np.int32)
    for k, v in raw.items():
        rule[int(k)] = int(v)
    return rule


def step_ca(grid: np.ndarray, rule: np.ndarray) -> np.ndarray:
    state = grid.astype(np.int32) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        neighbor = np.roll(np.roll(grid, -dq, axis=0), -dr, axis=1)
        state |= neighbor.astype(np.int32) << (5 - i)
    return ((rule[state] >> 6) & 1).astype(np.int8)


def make_t_shape_grid() -> np.ndarray:
    """150x150 grid with a single 4-bit T-shape at the center."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
    cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
    # T-shape: center + SW (r-1) + NE (r+1) + E (q+1)
    grid[cx, cy]     = 1  # center
    grid[cx, cy - 1] = 1  # SW arm
    grid[cx, cy + 1] = 1  # NE arm
    grid[cx + 1, cy] = 1  # E arm (stem of T)
    return grid


def evaluate_from_seed(rule_path: Path) -> dict:
    rule = load_rule_array(rule_path)
    grid = make_t_shape_grid()

    for _ in range(STEPS):
        grid = step_ca(grid, rule)

    final_bit_count = int(grid.sum())
    fitness = 1.0 / (1.0 + final_bit_count)
    return {"final_bit_count": final_bit_count, "fitness": fitness}


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rules = [
        ("chaotic_high",   POPULATION_DIR / "rule_023.json"),
        ("chaotic_medium", POPULATION_DIR / "rule_056.json"),
        ("stabilizing",    STABILIZING_RULE),
    ]

    results = {}
    for label, path in rules:
        print(f"Evaluating {label} ({path.name}) ...", flush=True)
        res = evaluate_from_seed(path)
        results[label] = res
        print(f"  final_bit_count = {res['final_bit_count']:6d}   "
              f"fitness = {res['fitness']:.6f}")

    chaotic_high_score   = results["chaotic_high"]["fitness"]
    chaotic_medium_score = results["chaotic_medium"]["fitness"]
    stabilizing_score    = results["stabilizing"]["fitness"]

    ratio_vs_high   = stabilizing_score / chaotic_high_score   if chaotic_high_score   > 0 else float("inf")
    ratio_vs_medium = stabilizing_score / chaotic_medium_score if chaotic_medium_score > 0 else float("inf")

    metric_is_discriminating = (ratio_vs_high >= 10.0 and ratio_vs_medium >= 10.0)

    print(f"\n=== Summary ===")
    print(f"  chaotic_high_fitness_rule_score:   {chaotic_high_score:.6f}")
    print(f"  chaotic_medium_fitness_rule_score: {chaotic_medium_score:.6f}")
    print(f"  stabilizing_rule_score:            {stabilizing_score:.6f}")
    print(f"  ratio stabilizing/chaotic_high:    {ratio_vs_high:.2f}x")
    print(f"  ratio stabilizing/chaotic_medium:  {ratio_vs_medium:.2f}x")
    print(f"  metric_is_discriminating:          {metric_is_discriminating}")

    yaml_result = {
        "chaotic_high_fitness_rule_score":   round(chaotic_high_score,   8),
        "chaotic_medium_fitness_rule_score": round(chaotic_medium_score, 8),
        "stabilizing_rule_score":            round(stabilizing_score,    8),
        "chaotic_high_final_bit_count":      results["chaotic_high"]["final_bit_count"],
        "chaotic_medium_final_bit_count":    results["chaotic_medium"]["final_bit_count"],
        "stabilizing_final_bit_count":       results["stabilizing"]["final_bit_count"],
        "ratio_stabilizing_vs_chaotic_high":   round(ratio_vs_high,   4),
        "ratio_stabilizing_vs_chaotic_medium": round(ratio_vs_medium, 4),
        "metric_is_discriminating":          bool(metric_is_discriminating),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved: {RESULT_YAML}")

    return 0 if metric_is_discriminating else 1


if __name__ == "__main__":
    sys.exit(main())
