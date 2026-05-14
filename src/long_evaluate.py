#!/usr/bin/env python3
"""
long_evaluate.py

Evaluate a single CA rule over a longer time horizon to detect transient behaviour.
Calculates composite fitness: total_displacement / (1 + std_dev) over multiple windows.

Usage:
  python src/long_evaluate.py \
      --rule_file archive/iter_153/results/population_gen3.json \
      --rule_id rule_021 \
      --steps 2000 \
      --num_windows 8 \
      --grid_size 150 \
      --density 0.25 \
      --seed 21 \
      --output_dir archive/iter_155/results/
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent


def _rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def _rotate_c2(state: int) -> int:
    return _rotate60_msb(_rotate60_msb(_rotate60_msb(state)))


def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def make_soup(grid_size: int, density: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return (rng.random((grid_size, grid_size)) < density).astype(np.uint8)


def evaluate_long(rule_dict: dict, soup: np.ndarray,
                  num_windows: int, steps_per_window: int) -> dict:
    lut  = _rule_to_lut(rule_dict)
    grid = np.copy(soup)

    checkpoints = [_center_of_mass(grid)]
    for w in range(num_windows):
        for _ in range(steps_per_window):
            grid = _step_grid(grid, lut)
        checkpoints.append(_center_of_mass(grid))
        print(f"  Window {w+1}/{num_windows} done, CoM={checkpoints[-1]}", flush=True)

    velocities = []
    for i in range(num_windows):
        sq, sr = checkpoints[i]
        eq, er = checkpoints[i + 1]
        velocities.append(math.sqrt((eq - sq)**2 + (er - sr)**2))

    total_disp = sum(velocities)
    std_dev    = float(np.std(velocities))
    composite  = total_disp / (1.0 + std_dev) if total_disp > 1e-9 else 0.0

    return {
        "composite_fitness": round(composite, 6),
        "total_displacement": round(total_disp, 6),
        "std_dev": round(std_dev, 8),
        "velocities": velocities,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule_file",   type=str,
                        default="archive/iter_153/results/population_gen3.json")
    parser.add_argument("--rule_id",     type=str, default="rule_021")
    parser.add_argument("--steps",       type=int, default=2000)
    parser.add_argument("--num_windows", type=int, default=8)
    parser.add_argument("--grid_size",   type=int, default=150)
    parser.add_argument("--density",     type=float, default=0.25)
    parser.add_argument("--seed",        type=int, default=21)
    parser.add_argument("--output_dir",  type=str,
                        default="archive/iter_155/results/")
    args = parser.parse_args()

    steps_per_window = args.steps // args.num_windows
    if steps_per_window * args.num_windows != args.steps:
        print(f"[warn] steps={args.steps} not evenly divisible by "
              f"num_windows={args.num_windows}; using {steps_per_window} steps/window")

    rule_path = PROJECT_ROOT / args.rule_file
    print(f"Loading rule {args.rule_id} from {rule_path}")
    with open(rule_path) as f:
        population = json.load(f)

    if args.rule_id not in population:
        print(f"[error] {args.rule_id} not found in {rule_path}")
        return 1

    rule_dict = population[args.rule_id]
    print(f"Rule {args.rule_id}: {len(rule_dict)} entries")

    soup = make_soup(args.grid_size, args.density, args.seed)
    print(f"Soup: {args.grid_size}x{args.grid_size}, density={args.density}, seed={args.seed}")
    print(f"Simulation: {args.steps} steps, {args.num_windows} windows "
          f"x {steps_per_window} steps each")

    print("\nRunning simulation ...")
    result = evaluate_long(rule_dict, soup, args.num_windows, steps_per_window)

    velocities = result["velocities"]
    total_disp = result["total_displacement"]
    std_dev    = result["std_dev"]
    composite  = result["composite_fitness"]

    original_fitness = 3.465
    fitness_reduction_pct = round(
        (original_fitness - composite) / original_fitness * 100.0, 2
    )

    window_labels = {}
    for i in range(args.num_windows):
        start = i * steps_per_window
        end   = (i + 1) * steps_per_window
        key   = f"window_{start}_{end}"
        window_labels[key] = round(velocities[i], 6)

    print(f"\nDisplacement per window: {[round(v, 4) for v in velocities]}")
    print(f"Total displacement: {total_disp}")
    print(f"Velocity std dev: {std_dev}")
    print(f"New fitness score: {composite}")
    print(f"Original fitness score: {original_fitness}")
    print(f"Fitness reduction: {fitness_reduction_pct}%")

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "original_fitness_1000_steps": original_fitness,
        "new_fitness_2000_steps": composite,
        "fitness_reduction_pct": fitness_reduction_pct,
        "total_com_displacement": total_disp,
        "velocity_std_dev": std_dev,
    }
    results.update(window_labels)

    results_yaml_path = output_dir / "results.yaml"
    with open(results_yaml_path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved: {results_yaml_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
