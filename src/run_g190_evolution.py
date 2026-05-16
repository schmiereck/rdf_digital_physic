#!/usr/bin/env python3
"""
run_g190_evolution.py  —  iter_190 evolutionary search using GradedCollisionFitness.

Setup
-----
* Population : 100 random C2-symmetric rules
* Generations: up to 20 (continuous fitness — no binary early-stop)
* Seed       : two 3-bit L-tromino particles on a 128x128 torus
* Simulation : 400 steps, midpoint snapshot at step 200
* Fitness    : GradedCollisionFitness (continuous, rewards partial progress)

Rationale: MarginalDynamicCollisionFitness produced a flat landscape (all zeros).
GradedCollisionFitness creates a gradient so selection pressure guides the search
toward rules that approach, interact, and recede — even if imperfectly.

If a best rule is found it is saved to archive/iter_190/results/best_rule.json.
If that rule achieves a verified collision (approach + recession + conservation),
a GIF is also written to archive/iter_190/results/collision.gif.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label

sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule, rule_dict_to_lut, step_grid
from fitness_g190 import GradedCollisionFitness, _LABEL_STRUCTURE


# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_190" / "results"
BEST_JSON    = OUTPUT_DIR / "best_rule.json"
BEST_GIF     = OUTPUT_DIR / "collision.gif"

# ── Grid constants (must match fitness_g190 seed positions) ──────────────────

_DYN_GRID_SIZE = 128
_DYN_OBJECT_A  = [(60, 40), (61, 40), (60, 41)]
_DYN_OBJECT_B  = [(67, 87), (68, 87), (67, 88)]


def _make_grid(grid_size: int = _DYN_GRID_SIZE) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _DYN_OBJECT_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _DYN_OBJECT_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


# ── GA hyper-parameters ──────────────────────────────────────────────────────

POPULATION_SIZE = 100
NUM_GENERATIONS = 20
ELITE_FRACTION  = 0.10
DENSITY         = 8
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.01
LUT_SIZE        = 128
RNG_SEED        = 190_001
MAX_WORKERS     = 4
HORIZON         = 400
MIDPOINT        = 200

ELITE_COUNT = max(2, int(POPULATION_SIZE * ELITE_FRACTION))


# ── Chromosome <-> rule_dict conversions ─────────────────────────────────────

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


# ── Random C2-symmetric rule generation ──────────────────────────────────────

def generate_c2_rule_density(
    rng: random.Random, density: int = DENSITY, max_attempts: int = 10_000,
) -> dict:
    for _ in range(max_attempts):
        pairs = [(rng.randint(1, 127), rng.randint(1, 127)) for _ in range(density)]
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate C2 rule with density {density}")


# ── Fitness evaluation (process-pool parallel) ────────────────────────────────

def _eval_worker(task: tuple) -> tuple:
    idx, chrom_list = task
    chrom     = np.asarray(chrom_list, dtype=np.uint8)
    rule_dict = chromosome_to_rule_dict(chrom)
    metrics   = GradedCollisionFitness(horizon=HORIZON, midpoint=MIDPOINT).evaluate(rule_dict)
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


# ── Genetic operators ─────────────────────────────────────────────────────────

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


# ── Champion-rule animation ───────────────────────────────────────────────────

def render_collision_gif(
    rule_dict: dict, gif_path: Path, steps: int = HORIZON, frame_ms: int = 50,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut    = rule_dict_to_lut(rule_dict)
    grid   = _make_grid(_DYN_GRID_SIZE)
    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title("iter_190 GradedCollisionFitness best rule")
    ax.set_xlabel("col")
    ax.set_ylabel("row")
    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest", cmap="hot", vmin=0, vmax=1,
    )
    step_text = ax.text(
        0.02, 0.97, f"step={frames[0][0]}", transform=ax.transAxes,
        color="white", fontsize=10, va="top",
    )

    def update(i):
        step, g = frames[i]
        img.set_data(g)
        step_text.set_text(f"step={step}")
        return img, step_text

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=frame_ms, blit=True)
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=1000 // frame_ms)
    plt.close(fig)


# ── Evolutionary search ───────────────────────────────────────────────────────

def run_search() -> dict:
    print("=== iter_190 Evolutionary Search (GradedCollisionFitness) ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"  Config: ca_config_2d_hex_128_torus_2_particles_3_bit_ltromino")
    print(f"  Population : {POPULATION_SIZE}   Generations(max): {NUM_GENERATIONS}")
    print(f"  Density    : {DENSITY}           Elite: {ELITE_COUNT}")
    print(f"  Horizon    : {HORIZON}           Midpoint: {MIDPOINT}")
    print(f"  Fitness    : GradedCollisionFitness (continuous)\n")

    population = [
        rule_dict_to_chromosome(generate_c2_rule_density(rng, density=DENSITY))
        for _ in range(POPULATION_SIZE)
    ]

    fitnesses, metrics_l = evaluate_population(population)
    best_idx        = int(np.argmax(fitnesses))
    best_fitness    = float(fitnesses[best_idx])
    best_chrom      = population[best_idx].copy()
    best_metrics    = metrics_l[best_idx]
    best_generation = 0

    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    print(
        f"  Gen  0: best={best_fitness:.4f}  mean={float(np.mean(fitnesses)):.4f}  "
        f"non_zero={n_nonzero}"
    )

    for gen in range(1, NUM_GENERATIONS + 1):
        elite  = select_top_k(population, fitnesses, ELITE_COUNT)
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
        print(
            f"  Gen {gen:2d}: best={gen_best:.4f}  mean={gen_mean:.4f}  "
            f"non_zero={n_nonzero}"
        )

    return {
        "best_fitness":    float(best_fitness),
        "best_chrom":      best_chrom,
        "best_metrics":    best_metrics,
        "best_generation": int(best_generation),
        "generations_ran": NUM_GENERATIONS,
    }


# ── Reporting ─────────────────────────────────────────────────────────────────

def write_results(result: dict) -> list:
    print("\n=== Results ===")
    artifacts: list[str] = []

    rule_dict = chromosome_to_rule_dict(result["best_chrom"])
    m         = result["best_metrics"] or {}

    payload = {
        "iteration":          "iter_190",
        "fitness":            result["best_fitness"],
        "generation_of_best": result["best_generation"],
        "num_generations":    NUM_GENERATIONS,
        "population_size":    POPULATION_SIZE,
        "elite_count":        ELITE_COUNT,
        "crossover_rate":     CROSSOVER_RATE,
        "mutation_rate":      MUTATION_RATE,
        "rng_seed":           RNG_SEED,
        "horizon":            HORIZON,
        "midpoint":           MIDPOINT,
        "grid_size":          _DYN_GRID_SIZE,
        "object_a":           _DYN_OBJECT_A,
        "object_b":           _DYN_OBJECT_B,
        "fitness_function":   "GradedCollisionFitness",
        "metrics":            m,
        "rule_dict":          {str(k): int(v) for k, v in rule_dict.items()},
        "chromosome":         result["best_chrom"].tolist(),
    }
    BEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(BEST_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Best rule saved: {BEST_JSON}")
    artifacts.append(str(BEST_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    # Verify whether the best rule achieves a real collision (approach + recession).
    collision_verified = (
        m.get("approach_score", 0.0) > 0.0
        and m.get("recede_score", 0.0) > 0.0
        and m.get("conservation_score", 0.0) > 0.9
    )
    if collision_verified:
        print(f"  Collision verified! Rendering animation ({HORIZON} steps) ...")
        render_collision_gif(rule_dict, BEST_GIF, steps=HORIZON)
        print(f"  GIF saved: {BEST_GIF}")
        artifacts.append(str(BEST_GIF.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    else:
        print(f"  No verified collision (approach={m.get('approach_score', 0):.2f}, "
              f"recede={m.get('recede_score', 0):.2f}, "
              f"conservation={m.get('conservation_score', 0):.3f})")

    print(f"\n  best_fitness    = {result['best_fitness']:.4f}")
    print(f"  best_generation = {result['best_generation']}")
    if m:
        print(f"  conservation    = {m.get('conservation_score', 'n/a'):.3f}")
        print(f"  approach_score  = {m.get('approach_score', 'n/a'):.3f}")
        print(f"  recede_score    = {m.get('recede_score', 'n/a'):.3f}")
        print(f"  displacement    = {m.get('total_displacement', 'n/a'):.3f}")
    return artifacts


def main() -> int:
    result    = run_search()
    artifacts = write_results(result)

    print("\n=== Summary ===")
    print(f"  best_fitness    = {result['best_fitness']:.4f}")
    print(f"  best_generation = {result['best_generation']}")
    print(f"  artifacts       = {artifacts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
