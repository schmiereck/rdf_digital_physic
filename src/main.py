#!/usr/bin/env python3
"""
main.py

Single-rule simulation with composite fitness metric.

Composite fitness = late_displacement / (1 + final_bit_count)
where late_displacement = Euclidean distance of center-of-mass between t=1200 and t=2000.

Usage:
    python main.py --rule-key rule_058 \
                   --population-file archive/iter_158/results/population_gen1.json \
                   [--steps 2000] [--grid-size 128] [--seed 42] [--density 0.25] \
                   [--output-dir archive/iter_159/results]
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml

PROJECT_ROOT = Path(__file__).parent.parent

COM_T1 = 1200
COM_T2 = 2000


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
    se = np.roll(e,   1, axis=1)
    nw = np.roll(w,  -1, axis=1)
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


def calculate_composite_fitness(
    rule_dict: dict,
    grid_size: int = 128,
    steps: int = 2000,
    seed: int = 42,
    density: float = 0.25,
) -> dict:
    lut  = _rule_to_lut(rule_dict)
    rng  = np.random.default_rng(seed)
    grid = (rng.random((grid_size, grid_size)) < density).astype(np.uint8)

    com_t1 = None
    com_t2 = None
    final_grid = None

    for t in range(1, steps + 1):
        grid = _step_grid(grid, lut)
        if t == COM_T1:
            com_t1 = _center_of_mass(grid)
            print(f"  t={COM_T1}: CoM = ({com_t1[0]:.4f}, {com_t1[1]:.4f})", flush=True)
        if t == COM_T2:
            com_t2 = _center_of_mass(grid)
            final_grid = grid.copy()
            print(f"  t={COM_T2}: CoM = ({com_t2[0]:.4f}, {com_t2[1]:.4f})", flush=True)

    dx = com_t2[0] - com_t1[0]
    dy = com_t2[1] - com_t1[1]
    late_displacement = math.sqrt(dx * dx + dy * dy)
    final_bit_count   = int(final_grid.sum())
    composite_fitness = late_displacement / (1.0 + final_bit_count)

    return {
        "late_displacement":        late_displacement,
        "final_bit_count":          final_bit_count,
        "composite_fitness":        composite_fitness,
        "late_displacement_fitness": late_displacement,
        "com_at_t1200":             com_t1,
        "com_at_t2000":             com_t2,
        "final_grid":               final_grid,
    }


def save_grid_image(grid: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap="binary", interpolation="nearest", origin="upper")
    ax.set_title(f"Final grid state (t={COM_T2})")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Single-rule composite fitness evaluation")
    parser.add_argument("--rule-key",        required=True, help="Rule key in population JSON")
    parser.add_argument("--population-file", required=True, help="Path to population JSON file")
    parser.add_argument("--steps",      type=int,   default=2000,  help="Simulation steps")
    parser.add_argument("--grid-size",  type=int,   default=128,   help="Grid width/height")
    parser.add_argument("--seed",       type=int,   default=42,    help="Random seed")
    parser.add_argument("--density",    type=float, default=0.25,  help="Initial soup density")
    parser.add_argument("--output-dir", default=None,
                        help="Directory for outputs (default: archive/iter_159/results)")
    args = parser.parse_args()

    pop_path = Path(args.population_file)
    if not pop_path.is_absolute():
        pop_path = PROJECT_ROOT / pop_path

    output_dir = Path(args.output_dir) if args.output_dir else \
        PROJECT_ROOT / "archive" / "iter_159" / "results"
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    print(f"Loading population from {pop_path}")
    with open(pop_path) as f:
        population = json.load(f)

    rule_key = args.rule_key
    if rule_key not in population:
        print(f"[error] {rule_key} not found in {pop_path}", file=sys.stderr)
        return 1

    rule_dict = population[rule_key]
    print(f"Rule {rule_key}: {len(rule_dict)} entries")
    print(f"Grid: {args.grid_size}x{args.grid_size}, density={args.density}, seed={args.seed}")
    print(f"Running {args.steps} steps, recording CoM at t={COM_T1} and t={COM_T2} ...")

    result = calculate_composite_fitness(
        rule_dict,
        grid_size=args.grid_size,
        steps=args.steps,
        seed=args.seed,
        density=args.density,
    )

    png_path = output_dir / f"final_grid_{rule_key}.png"
    save_grid_image(result["final_grid"], png_path)

    print(f"\n=== Results for {rule_key} ===")
    print(f"  late_displacement:        {result['late_displacement']:.6f}")
    print(f"  final_bit_count:          {result['final_bit_count']}")
    print(f"  composite_fitness:        {result['composite_fitness']:.8f}")
    print(f"  late_displacement_fitness:{result['late_displacement_fitness']:.6f}")

    yaml_result = {
        "rule_key":                   rule_key,
        "late_displacement":          round(result["late_displacement"],        6),
        "final_bit_count":            result["final_bit_count"],
        "composite_fitness":          round(result["composite_fitness"],        8),
        "late_displacement_fitness":  round(result["late_displacement_fitness"], 6),
        "com_at_t1200":               [round(result["com_at_t1200"][0], 4),
                                       round(result["com_at_t1200"][1], 4)],
        "com_at_t2000":               [round(result["com_at_t2000"][0], 4),
                                       round(result["com_at_t2000"][1], 4)],
        "grid_size":                  args.grid_size,
        "density":                    args.density,
        "seed":                       args.seed,
        "steps":                      args.steps,
        "png_path":                   str(png_path.relative_to(PROJECT_ROOT)),
    }

    results_yaml = output_dir / f"results_{rule_key}.yaml"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(results_yaml, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved: {results_yaml}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
