#!/usr/bin/env python3
"""
evolve_rules.py

Generation 0 of an evolutionary algorithm for discovering complex CA rules.
Steps: generate 100 random rules, evaluate fitness, select top 10 elites.

Fitness = mean(bit_count_last_100_steps) * stddev(bit_count_all_steps)
"""

import csv
import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_083" / "population"
ELITES_DIR = PROJECT_ROOT / "archive" / "iter_083" / "elites"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_083" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_083" / "result.yaml"

POPULATION_SIZE = 100
ELITE_COUNT = 10
GRID_SIZE = 100
STEPS = 500
FILL_RATE = 0.5
MAX_ATTEMPTS = 10000

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


# --- Rule generation ---

def rotate60(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def apply_n_rotations(state: int, n: int) -> int:
    for _ in range(n):
        state = rotate60(state)
    return state


def try_build_rule(pairs: list) -> dict | None:
    rule = {}
    for a, b in pairs:
        for rot in range(6):
            a_rot = apply_n_rotations(a, rot)
            b_rot = apply_n_rotations(b, rot)
            for src, dst in [(a_rot, b_rot), (b_rot, a_rot)]:
                if src in rule:
                    if rule[src] != dst:
                        return None
                else:
                    rule[src] = dst
    return rule


def is_nonconserving(pairs: list) -> bool:
    return any(bin(a).count('1') != bin(b).count('1') for a, b in pairs)


def generate_random_rule(rng: random.Random) -> tuple[dict, list]:
    for _ in range(MAX_ATTEMPTS):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))

        if not is_nonconserving(pairs):
            continue

        rule = try_build_rule(pairs)
        if rule is not None:
            return rule, pairs

    raise RuntimeError("Failed to generate valid rule after many attempts")


# --- Simulation & fitness ---

def load_rule_array(rule_dict: dict) -> np.ndarray:
    rule = np.arange(128, dtype=np.int32)
    for k, v in rule_dict.items():
        rule[int(k)] = int(v)
    return rule


def step_ca(grid: np.ndarray, rule: np.ndarray) -> np.ndarray:
    state = grid.astype(np.int32) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        neighbor = np.roll(np.roll(grid, -dq, axis=0), -dr, axis=1)
        state |= neighbor.astype(np.int32) << (5 - i)
    return ((rule[state] >> 6) & 1).astype(np.int8)


def evaluate_rule(rule_dict: dict, rng: np.random.Generator) -> dict:
    rule = load_rule_array(rule_dict)
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
    }


# --- Main ---

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    ELITES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_rng = random.Random(42)
    sim_rng = np.random.default_rng(42)

    # Generation
    print(f"Generating {POPULATION_SIZE} random C6-symmetric non-conserving rules...")
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict, pairs = generate_random_rule(rule_rng)
        rule_path = POPULATION_DIR / f"rule_{i:03d}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        rules.append((i, rule_dict, rule_path))
        if i % 10 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE}")

    print(f"\nEvaluating {POPULATION_SIZE} rules ({STEPS} steps on "
          f"{GRID_SIZE}x{GRID_SIZE} grid)...")

    rows = []
    for i, rule_dict, rule_path in rules:
        rule_id = f"rule_{i:03d}"
        metrics = evaluate_rule(rule_dict, sim_rng)
        print(f"  {rule_id}: fitness={metrics['fitness']:10.1f}  "
              f"final={metrics['final_bit_count']:5d}  "
              f"mean={metrics['mean_bit_count']:7.1f}  "
              f"std={metrics['stddev_bit_count']:7.2f}")
        rows.append({
            "rule_id": rule_id,
            "fitness_score": round(metrics["fitness"], 4),
            "final_bit_count": metrics["final_bit_count"],
            "mean_bit_count": round(metrics["mean_bit_count"], 4),
            "stddev_bit_count": round(metrics["stddev_bit_count"], 4),
        })

    # Save CSV
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

    # Selection: top 10 elites
    sorted_rows = sorted(rows, key=lambda r: r["fitness_score"], reverse=True)
    elites = sorted_rows[:ELITE_COUNT]
    elite_ids = {r["rule_id"] for r in elites}

    for i, rule_dict, rule_path in rules:
        rule_id = f"rule_{i:03d}"
        if rule_id in elite_ids:
            shutil.copy(rule_path, ELITES_DIR / rule_path.name)

    print(f"\nTop {ELITE_COUNT} elites:")
    for r in elites:
        print(f"  {r['rule_id']}: fitness={r['fitness_score']:.1f}")

    # Metrics
    all_scores = np.array([r["fitness_score"] for r in rows])
    elite_scores = np.array([r["fitness_score"] for r in elites])

    pop_mean = float(np.mean(all_scores))
    elite_mean = float(np.mean(elite_scores))
    top_fitness = float(elite_scores.max())
    ratio = elite_mean / pop_mean if pop_mean > 0 else float("inf")

    print(f"\n=== Summary ===")
    print(f"  population_fitness_mean:  {pop_mean:.2f}")
    print(f"  elite_fitness_mean:       {elite_mean:.2f}")
    print(f"  top_elite_fitness:        {top_fitness:.2f}")
    print(f"  selection_pressure_ratio: {ratio:.2f}")

    result = {
        "population_size": POPULATION_SIZE,
        "elite_count": ELITE_COUNT,
        "population_fitness_mean": round(pop_mean, 4),
        "elite_fitness_mean": round(elite_mean, 4),
        "top_elite_fitness": round(top_fitness, 4),
        "selection_pressure_ratio": round(ratio, 4),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
