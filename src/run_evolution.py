#!/usr/bin/env python3
"""
run_evolution.py

Evolutionary search framework for hexagonal CA rules.

Supports two initialisation modes:
  * Random C2-symmetric population (legacy behaviour).
  * Warm-start population loaded from a JSON file (each rule given as a
    128-element binary chromosome).

Fitness metric: StagedCollisionFitness from src/fitness.py (discrete 0/1/2),
which strictly enforces bit conservation between the initial, midpoint and
final snapshots.

Chromosome representation: a 128-element list of bits.  Entry i is the
new "center" output bit when the local hex neighbourhood evaluates to state
i.  The chromosome is converted to a rule_dict before evaluation.

Mutation operator: swap two randomly chosen positions in the chromosome.
A swap that exchanges two identical bits has no effect, matching the
behaviour used to construct the warm-start population in iter_191.1.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule  # noqa: E402  (path setup needed first)
from fitness import StagedCollisionFitness  # noqa: E402

PROJECT_ROOT = Path(__file__).parent.parent

LUT_SIZE = 128


# ── Chromosome <-> rule_dict conversion ──────────────────────────────────────


def chromosome_to_rule_dict(chrom) -> dict:
    """Map a 128-element binary chromosome to a sparse rule_dict.

    Only states whose mapped center bit differs from the identity LUT are
    stored, matching the convention used by iter_190.2.
    """
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Population initialisation ────────────────────────────────────────────────


def load_initial_population(path: Path) -> list[np.ndarray]:
    with open(path, "r") as f:
        members = json.load(f)
    if not isinstance(members, list):
        raise ValueError(
            f"Expected a JSON list of rule dicts in {path}, got {type(members)}"
        )
    population: list[np.ndarray] = []
    for i, m in enumerate(members):
        chrom = m.get("chromosome", m.get("lookup_table"))
        if chrom is None:
            raise ValueError(
                f"Population member {i} in {path} lacks 'chromosome'/'lookup_table'"
            )
        arr = np.asarray(chrom, dtype=np.uint8)
        if arr.shape != (LUT_SIZE,):
            raise ValueError(
                f"Member {i} chromosome has shape {arr.shape}, expected ({LUT_SIZE},)"
            )
        population.append(arr)
    return population


def generate_random_population(size: int, rng: random.Random) -> list[np.ndarray]:
    population: list[np.ndarray] = []
    for _ in range(size):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))
        rule = _try_build_c2_rule(pairs)
        if rule is None:
            continue
        population.append(rule_dict_to_chromosome(rule))
    while len(population) < size:
        chrom = np.array(
            [rng.randint(0, 1) for _ in range(LUT_SIZE)], dtype=np.uint8
        )
        population.append(chrom)
    return population[:size]


# ── Genetic operators ────────────────────────────────────────────────────────


def swap_mutate(chrom: np.ndarray, num_swaps: int, rng: random.Random) -> np.ndarray:
    """Mutate a chromosome by `num_swaps` random index swaps."""
    out = chrom.copy()
    n = len(out)
    for _ in range(num_swaps):
        i, j = rng.sample(range(n), 2)
        out[i], out[j] = out[j], out[i]
    return out


def select_top_k(
    population: list[np.ndarray], scores: list[float], k: int
) -> list[np.ndarray]:
    order = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Evolutionary loop ────────────────────────────────────────────────────────


def evolve(
    *,
    initial_population_path: Path | None,
    generations: int,
    population_size: int,
    elite_size: int,
    mutation_rate: float,
    horizon: int,
    midpoint: int,
    grid_size: int,
    rng_seed: int,
    champion_output_path: Path,
    log_csv_path: Path,
) -> dict:
    rng = random.Random(rng_seed)
    fitness = StagedCollisionFitness(
        horizon=horizon, midpoint=midpoint, grid_size=grid_size
    )

    if initial_population_path is not None:
        print(f"Loading warm-start population from {initial_population_path} ...")
        population = load_initial_population(initial_population_path)
        if len(population) != population_size:
            print(
                f"  WARNING: loaded {len(population)} members, "
                f"requested population_size={population_size}. Using loaded count."
            )
            population_size = len(population)
    else:
        print(f"Generating random population of {population_size} rules ...")
        population = generate_random_population(population_size, rng)

    num_swaps = max(1, round(mutation_rate * LUT_SIZE))
    print(
        f"Configuration: generations={generations} pop={population_size} "
        f"elite={elite_size} swaps/child={num_swaps} "
        f"horizon={horizon} midpoint={midpoint} grid={grid_size}"
    )

    champion_chrom: np.ndarray | None = None
    champion_fitness = -1.0
    champion_metrics: dict | None = None
    champion_generation = 0

    gen_log: list[dict] = []

    for gen in range(0, generations + 1):
        # Evaluate population.
        scores: list[float] = []
        metrics_l: list[dict] = []
        for chrom in population:
            rule_dict = chromosome_to_rule_dict(chrom)
            m = fitness.evaluate(rule_dict)
            scores.append(float(m["fitness"]))
            metrics_l.append(m)

        scores_np = np.asarray(scores)
        gen_min = float(scores_np.min())
        gen_mean = float(scores_np.mean())
        gen_max = float(scores_np.max())
        gen_std = float(scores_np.std())
        n_nonzero = int(np.sum(scores_np > 0.0))
        n_one = int(np.sum(scores_np >= 1.0))
        n_two = int(np.sum(scores_np >= 2.0))

        best_idx = int(scores_np.argmax())
        if scores[best_idx] > champion_fitness:
            champion_fitness = scores[best_idx]
            champion_chrom = population[best_idx].copy()
            champion_metrics = metrics_l[best_idx]
            champion_generation = gen
            new_champ_msg = "  ** new champion **"
        else:
            new_champ_msg = ""

        print(
            f"  Gen {gen:2d}: max={gen_max:.4f}  mean={gen_mean:.4f}  "
            f"std={gen_std:.4f}  non_zero={n_nonzero}  "
            f"n>=1={n_one}  n>=2={n_two}{new_champ_msg}"
        )

        gen_log.append(
            {
                "generation": gen,
                "min": round(gen_min, 6),
                "mean": round(gen_mean, 6),
                "max": round(gen_max, 6),
                "std": round(gen_std, 6),
                "non_zero": n_nonzero,
                "n_ge_1": n_one,
                "n_ge_2": n_two,
                "champion_fitness": round(champion_fitness, 6),
            }
        )

        if gen >= generations:
            break

        # Procreate next generation: keep elites, fill rest with mutated children.
        elites = select_top_k(population, scores, elite_size)
        next_pop = [e.copy() for e in elites]
        while len(next_pop) < population_size:
            parent = rng.choice(elites)
            child = swap_mutate(parent, num_swaps, rng)
            next_pop.append(child)
        population = next_pop

    # ── Persist results ─────────────────────────────────────────────────────
    if champion_chrom is not None:
        rule_dict = chromosome_to_rule_dict(champion_chrom)
        payload = {
            "iteration": "iter_191.2",
            "fitness": float(champion_fitness),
            "champion_generation": int(champion_generation),
            "num_generations": int(generations),
            "population_size": int(population_size),
            "elite_size": int(elite_size),
            "mutation_rate": float(mutation_rate),
            "swaps_per_child": int(num_swaps),
            "rng_seed": int(rng_seed),
            "horizon": int(horizon),
            "midpoint": int(midpoint),
            "grid_size": int(grid_size),
            "fitness_function": "StagedCollisionFitness",
            "initial_population_path": (
                str(initial_population_path)
                if initial_population_path is not None
                else None
            ),
            "metrics": _coerce_metrics(champion_metrics or {}),
            "rule_dict": {str(k): int(v) for k, v in rule_dict.items()},
            "chromosome": [int(b) for b in champion_chrom],
        }
        champion_output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(champion_output_path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved champion rule -> {champion_output_path}")

    log_csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "generation",
        "min",
        "mean",
        "max",
        "std",
        "non_zero",
        "n_ge_1",
        "n_ge_2",
        "champion_fitness",
    ]
    with open(log_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(gen_log)
    print(f"Saved evolution log  -> {log_csv_path}")

    return {
        "champion_fitness": float(champion_fitness),
        "champion_generation": int(champion_generation),
        "gen_log": gen_log,
        "champion_metrics": _coerce_metrics(champion_metrics or {}),
    }


def _coerce_metrics(m: dict) -> dict:
    """Cast numpy/None values to JSON-safe Python types."""
    out: dict = {}
    for k, v in m.items():
        if v is None:
            out[k] = None
        elif isinstance(v, (bool, int, float, str)):
            out[k] = v
        else:
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                out[k] = str(v)
    return out


# ── CLI ──────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evolutionary search with StagedCollisionFitness."
    )
    parser.add_argument(
        "--initial_population_path",
        type=str,
        default=None,
        help=(
            "Optional path to a JSON file containing a list of rule entries "
            "with 'chromosome' arrays. When omitted, a random population is "
            "generated."
        ),
    )
    parser.add_argument("--generations", type=int, default=20)
    parser.add_argument("--population_size", type=int, default=100)
    parser.add_argument("--elite_size", type=int, default=10)
    parser.add_argument("--mutation_rate", type=float, default=0.01)
    parser.add_argument("--horizon", type=int, default=400)
    parser.add_argument("--midpoint", type=int, default=200)
    parser.add_argument("--grid_size", type=int, default=128)
    parser.add_argument("--rng_seed", type=int, default=191_002)
    parser.add_argument(
        "--champion_output_path",
        type=str,
        default=str(
            PROJECT_ROOT / "archive" / "iter_191" / "results" / "champion_rule.json"
        ),
    )
    parser.add_argument(
        "--log_csv_path",
        type=str,
        default=str(
            PROJECT_ROOT / "archive" / "iter_191" / "results" / "evolution_log.csv"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    initial_path = (
        Path(args.initial_population_path)
        if args.initial_population_path
        else None
    )
    if initial_path is not None and not initial_path.is_absolute():
        initial_path = (PROJECT_ROOT / initial_path).resolve()

    champion_output_path = Path(args.champion_output_path)
    if not champion_output_path.is_absolute():
        champion_output_path = (PROJECT_ROOT / champion_output_path).resolve()

    log_csv_path = Path(args.log_csv_path)
    if not log_csv_path.is_absolute():
        log_csv_path = (PROJECT_ROOT / log_csv_path).resolve()

    result = evolve(
        initial_population_path=initial_path,
        generations=args.generations,
        population_size=args.population_size,
        elite_size=args.elite_size,
        mutation_rate=args.mutation_rate,
        horizon=args.horizon,
        midpoint=args.midpoint,
        grid_size=args.grid_size,
        rng_seed=args.rng_seed,
        champion_output_path=champion_output_path,
        log_csv_path=log_csv_path,
    )

    print("\n=== Evolution complete ===")
    print(f"  champion_fitness     = {result['champion_fitness']:.4f}")
    print(f"  champion_generation  = {result['champion_generation']}")
    if result["champion_metrics"]:
        m = result["champion_metrics"]
        print(f"  approach_score       = {m.get('approach_score', 'n/a')}")
        print(f"  recession_score      = {m.get('recession_score', 'n/a')}")
        print(f"  bits_conserved       = {m.get('bits_conserved', 'n/a')}")
        print(f"  d_initial            = {m.get('d_initial', 'n/a')}")
        print(f"  d_mid                = {m.get('d_mid', 'n/a')}")
        print(f"  d_final              = {m.get('d_final', 'n/a')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
