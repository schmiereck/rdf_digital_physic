#!/usr/bin/env python3
"""
run_dynamic_evolution.py  —  iter_188.2 evolutionary search using
``DynamicCollisionFitness``.

Three-part workflow
-------------------
A. Validation
   Load the iter_187 champion rule (saved as ``best_elastic_rule.json``)
   and evaluate it with ``DynamicCollisionFitness``. The expected score
   is 0.0, demonstrating that the new metric correctly rejects the
   static-still-life rule that gamed the end-state-only check.

B. Evolutionary search
   If validation passes, evolve C2-symmetric rules with the new
   fitness:
     * Population : 100
     * Generations: 10
     * Rule type  : C2-symmetric, 8 kernel pairs
     * Fitness    : DynamicCollisionFitness(horizon=100)
   The search stops early as soon as any individual scores 1.0.

C. Reporting
   If a champion is found, save the rule JSON and a 100-step collision
   GIF under ``archive/iter_188/results/``. Otherwise, report that no
   champion was found.
"""

from __future__ import annotations

import concurrent.futures
import json
import random
import sys
from pathlib import Path

import numpy as np

# Ensure src/ is importable when run as a script
sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule, rule_dict_to_lut, step_grid
from fitness import (
    DynamicCollisionFitness,
    _make_dynamic_collision_grid,
    _DYN_GRID_SIZE,
)


# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).parent.parent
ITER187_RULE  = PROJECT_ROOT / "archive" / "iter_187" / "results" / "best_elastic_rule.json"
OUTPUT_DIR    = PROJECT_ROOT / "archive" / "iter_188" / "results"
CHAMPION_JSON = OUTPUT_DIR / "dynamic_champion_rule.json"
CHAMPION_GIF  = OUTPUT_DIR / "dynamic_champion_collision.gif"


# ── GA hyper-parameters ─────────────────────────────────────────────────────

POPULATION_SIZE = 100
NUM_GENERATIONS = 10
ELITE_FRACTION  = 0.10
DENSITY         = 8
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.01
LUT_SIZE        = 128
RNG_SEED        = 188_201
MAX_WORKERS     = 4
HORIZON         = 100

ELITE_COUNT = max(2, int(POPULATION_SIZE * ELITE_FRACTION))


# ── Chromosome <-> rule_dict conversions ────────────────────────────────────

def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


# ── Random C2-symmetric rule generation ─────────────────────────────────────

def generate_c2_rule_density(
    rng: random.Random, density: int = DENSITY, max_attempts: int = 10_000,
) -> dict:
    for _ in range(max_attempts):
        pairs = []
        for _ in range(density):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate C2 rule with density {density}")


# ── Fitness evaluation (process-pool parallel) ──────────────────────────────

def _eval_worker(task: tuple) -> tuple:
    idx, chrom_list = task
    chrom     = np.asarray(chrom_list, dtype=np.uint8)
    rule_dict = chromosome_to_rule_dict(chrom)
    metrics   = DynamicCollisionFitness(horizon=HORIZON).evaluate(rule_dict)
    return idx, float(metrics["fitness"]), metrics


def evaluate_population(population: list) -> tuple[list, list]:
    n         = len(population)
    fitnesses = [0.0] * n
    metrics_l = [None] * n
    tasks     = [(i, chrom.tolist()) for i, chrom in enumerate(population)]

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_eval_worker, t): t[0] for t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            idx, fitness, metrics = fut.result()
            fitnesses[idx] = fitness
            metrics_l[idx] = metrics

    return fitnesses, metrics_l


# ── Genetic operators ───────────────────────────────────────────────────────

def two_point_crossover(p1, p2, rng):
    n      = len(p1)
    a, b   = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(chrom, rate, rng):
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


def select_top_k(population, fitnesses, k):
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Champion-rule animation ─────────────────────────────────────────────────

def render_collision_gif(rule_dict: dict, gif_path: Path, steps: int = HORIZON,
                          frame_ms: int = 80) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut  = rule_dict_to_lut(rule_dict)
    grid = _make_dynamic_collision_grid(_DYN_GRID_SIZE)
    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title("iter_188.2 DynamicCollisionFitness champion")
    ax.set_xlabel("col")
    ax.set_ylabel("row")
    img = ax.imshow(frames[0][1], origin="upper", interpolation="nearest",
                    cmap="hot", vmin=0, vmax=1)
    step_text = ax.text(0.02, 0.97, f"step={frames[0][0]}",
                        transform=ax.transAxes,
                        color="white", fontsize=10, va="top")

    def update(i):
        step, g = frames[i]
        img.set_data(g)
        step_text.set_text(f"step={step}")
        return img, step_text

    ani = animation.FuncAnimation(fig, update, frames=len(frames),
                                  interval=frame_ms, blit=True)
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=1000 // frame_ms)
    plt.close(fig)


# ── Main ────────────────────────────────────────────────────────────────────

def part_a_validation() -> bool:
    """Load iter_187 champion and verify DynamicCollisionFitness == 0.0."""
    print("=== Part A: Validation ===")
    if not ITER187_RULE.exists():
        print(f"  ERROR: iter_187 champion rule not found at {ITER187_RULE}")
        return False
    with open(ITER187_RULE) as f:
        payload = json.load(f)
    rule_dict = {int(k): int(v) for k, v in payload["rule_dict"].items()}
    print(f"  Loaded iter_187 champion ({len(rule_dict)} non-identity entries)")

    fit = DynamicCollisionFitness(horizon=HORIZON)
    metrics = fit.evaluate(rule_dict)
    print(f"  DynamicCollisionFitness score: {metrics['fitness']:.4f}")
    print(f"  Detailed: initial_d={metrics['initial_distance']:.3f}  "
          f"mid_d={metrics['midpoint_distance']}  final_d={metrics['final_distance']}  "
          f"bits={metrics['final_bit_count']}  objs={metrics['final_object_count']}")

    if metrics["fitness"] != 0.0:
        print("  FAILURE: expected 0.0, got non-zero. Aborting search.")
        return False

    print("  Validation OK — iter_187 champion correctly scores 0.0\n")
    return True


def part_b_search() -> dict:
    """Run the evolutionary search. Stops early if fitness 1.0 is found."""
    print("=== Part B: Evolutionary Search ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"Population: {POPULATION_SIZE}  Generations: {NUM_GENERATIONS}  "
          f"Density: {DENSITY}  Elite: {ELITE_COUNT}")
    print(f"Fitness: DynamicCollisionFitness(horizon={HORIZON})\n")

    population = [
        rule_dict_to_chromosome(generate_c2_rule_density(rng, density=DENSITY))
        for _ in range(POPULATION_SIZE)
    ]

    fitnesses, metrics_l = evaluate_population(population)
    best_idx       = int(np.argmax(fitnesses))
    best_fitness   = float(fitnesses[best_idx])
    best_chrom     = population[best_idx].copy()
    best_metrics   = metrics_l[best_idx]
    best_generation = 0

    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    print(f"  Gen 0: best={best_fitness:.4f}  mean={float(np.mean(fitnesses)):.4f}  "
          f"non_zero={n_nonzero}")

    champion_found = best_fitness >= 1.0

    for gen in range(1, NUM_GENERATIONS + 1):
        if champion_found:
            break
        elite = select_top_k(population, fitnesses, ELITE_COUNT)
        new_pop = [e.copy() for e in elite]
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = rng.sample(elite, 2)
            if rng.random() < CROSSOVER_RATE:
                c1, c2 = two_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            c1 = per_bit_mutation(c1, MUTATION_RATE, rng)
            c2 = per_bit_mutation(c2, MUTATION_RATE, rng)
            new_pop.append(c1)
            if len(new_pop) < POPULATION_SIZE:
                new_pop.append(c2)

        population = new_pop
        fitnesses, metrics_l = evaluate_population(population)
        gen_best_idx = int(np.argmax(fitnesses))
        gen_best     = float(fitnesses[gen_best_idx])
        gen_mean     = float(np.mean(fitnesses))

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_chrom      = population[gen_best_idx].copy()
            best_metrics    = metrics_l[gen_best_idx]
            best_generation = gen

        n_nonzero = sum(1 for f in fitnesses if f > 0.0)
        print(f"  Gen {gen:2d}: best={gen_best:.4f}  mean={gen_mean:.4f}  "
              f"non_zero={n_nonzero}")

        if best_fitness >= 1.0:
            champion_found = True

    return {
        "champion_found":   bool(champion_found),
        "best_fitness":     float(best_fitness),
        "best_chrom":       best_chrom,
        "best_metrics":     best_metrics,
        "best_generation":  int(best_generation),
    }


def part_c_report(result: dict) -> dict:
    """Persist champion artifacts (or report no champion)."""
    print("\n=== Part C: Results ===")
    artifacts: list[str] = []

    if not result["champion_found"]:
        print(f"  No champion found. Best fitness = {result['best_fitness']:.4f}")
        return {"champion_found": False, "artifacts": artifacts}

    rule_dict = chromosome_to_rule_dict(result["best_chrom"])
    payload = {
        "iteration":          "iter_188.2",
        "fitness":            result["best_fitness"],
        "generation_of_best": result["best_generation"],
        "num_generations":    NUM_GENERATIONS,
        "population_size":    POPULATION_SIZE,
        "elite_count":        ELITE_COUNT,
        "crossover_rate":     CROSSOVER_RATE,
        "mutation_rate":      MUTATION_RATE,
        "rng_seed":           RNG_SEED,
        "horizon":            HORIZON,
        "fitness_function":   "DynamicCollisionFitness",
        "metrics":            result["best_metrics"],
        "rule_dict":          {str(k): int(v) for k, v in rule_dict.items()},
        "chromosome":         result["best_chrom"].tolist(),
    }
    CHAMPION_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAMPION_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Champion saved: {CHAMPION_JSON}")
    artifacts.append(str(CHAMPION_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    print(f"  Rendering animation ({HORIZON} steps) ...")
    render_collision_gif(rule_dict, CHAMPION_GIF, steps=HORIZON)
    print(f"  GIF saved: {CHAMPION_GIF}")
    artifacts.append(str(CHAMPION_GIF.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    print(f"\n  Champion fitness    : {result['best_fitness']:.4f}")
    print(f"  Champion generation : {result['best_generation']}")
    print(f"  Champion metrics    : {result['best_metrics']}")
    return {"champion_found": True, "artifacts": artifacts}


def main() -> int:
    ok = part_a_validation()
    if not ok:
        print("Validation failed — aborting.")
        return 1

    result = part_b_search()
    summary = part_c_report(result)

    print("\n=== Summary ===")
    print(f"  champion_found = {summary['champion_found']}")
    print(f"  best_fitness   = {result['best_fitness']:.4f}")
    if summary["champion_found"]:
        print(f"  champion_generation = {result['best_generation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
