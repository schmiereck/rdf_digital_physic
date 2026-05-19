#!/usr/bin/env python3
"""
run_vc_search.py  —  Evolutionary search for v<c gliders using LeakySubLightFitness.

Setup
-----
* Fitness     : LeakySubLightFitness (leaky bit-conservation gate;
                rewards displacement with a continuous conservation penalty)
* Population  : 100 random C2-symmetric rules
* Generations : 10
* Seed        : 3-bit L-tromino [(0,0), (0,1), (1,1)] centred on 128x128 grid
* Simulation  : 200 steps, checkpoints at [50, 100, 150]

Outputs (archive/iter_218/results/):
  champion_vc_rule.json    : champion rule + metrics
  evolution_log.csv        : generation,champion_fitness per generation
  champion_vc_glider.gif   : 200-step animation of the champion pattern
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

from evolution import (
    _try_build_c2_rule,
    rule_dict_to_lut,
    step_grid,
)
# from fitness_functions import NetDisplacementFitness, _make_particle_grid
from leaky_fitness import LeakySubLightFitness


# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_218" / "results"
CHAMPION_JSON = OUTPUT_DIR / "champion_vc_rule.json"
EVOLUTION_CSV = OUTPUT_DIR / "evolution_log.csv"
CHAMPION_GIF  = OUTPUT_DIR / "champion_vc_glider.gif"


# ── Search hyper-parameters ───────────────────────────────────────────────────

POPULATION_SIZE  = 100
NUM_GENERATIONS  = 10
ELITE_FRACTION   = 0.10
CROSSOVER_RATE   = 0.8
MUTATION_RATE    = 0.01
LUT_SIZE         = 128
RNG_SEED         = 200_001
GRID_SIZE        = 128
SIMULATION_STEPS = 200
DENSITY          = 6

ELITE_COUNT = max(2, int(POPULATION_SIZE * ELITE_FRACTION))

# 3-bit L-tromino seed (relative offsets from grid centre)
SEED_PARTICLE = [(0, 0), (0, 1), (1, 1)]


# ── Simple rule wrapper (Simulator expects rule.rule_dict) ────────────────────

class _RuleDict:
    """Minimal wrapper so that `Simulator(rule)` finds `rule.rule_dict`."""
    __slots__ = ("rule_dict",)
    def __init__(self, d: dict):
        self.rule_dict = d


# ── Chromosome <-> rule_dict conversions ──────────────────────────────────────

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


def generate_c2_rule(rng: random.Random, density: int = DENSITY, max_attempts: int = 10_000) -> dict:
    for _ in range(max_attempts):
        pairs = [(rng.randint(1, 127), rng.randint(1, 127)) for _ in range(density)]
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate C2 rule with density {density}")


# ── Fitness evaluation ─────────────────────────────────────────────────────────

# Old fitness function (kept for reference — commented out):
# _FITNESS = NetDisplacementFitness(
#     grid_size=GRID_SIZE,
#     simulation_steps=SIMULATION_STEPS,
#     particle=SEED_PARTICLE,
# )

# NEW: LeakySubLightFitness with leaky bit-conservation gate
_FITNESS = LeakySubLightFitness(
    checkpoints=[50, 100, 150],
    simulation_steps=SIMULATION_STEPS,
    bits_per_cell=1,
    velocity_threshold=0.9,
)


def evaluate_population(population: list) -> tuple[list[float], list[dict]]:
    fitnesses: list[float] = []
    metrics_l: list[dict]  = []
    for chrom in population:
        rule_dict = chromosome_to_rule_dict(chrom)
        rule      = _RuleDict(rule_dict)           # wrap for Simulator
        fitness, metrics = _FITNESS(rule, SEED_PARTICLE)
        fitnesses.append(float(fitness))
        metrics_l.append(metrics)
    return fitnesses, metrics_l


# ── Genetic operators ─────────────────────────────────────────────────────────

def two_point_crossover(p1: np.ndarray, p2: np.ndarray, rng: random.Random):
    n    = len(p1)
    a, b = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(chrom: np.ndarray, rate: float, rng: random.Random) -> np.ndarray:
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


def select_top_k(population: list, fitnesses: list[float], k: int) -> list:
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Champion animation ────────────────────────────────────────────────────────

def render_champion_gif(rule_dict: dict, gif_path: Path, steps: int = SIMULATION_STEPS) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut    = rule_dict_to_lut(rule_dict)
    # Build particle grid from SEED_PARTICLE centred on grid centre
    centre = GRID_SIZE // 2
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    seed_offset = (centre + SEED_PARTICLE[0][0], centre + SEED_PARTICLE[0][1])
    for dr, dc in SEED_PARTICLE:
        r = seed_offset[0] + dr
        c = seed_offset[1] + dc
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            grid[r, c] = 1

    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        if step % 5 == 0 or step == steps:
            frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_title("iter_218 LeakySubLightFitness champion (v<c search)")
    ax.set_xlabel("col")
    ax.set_ylabel("row")
    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest", cmap="hot", vmin=0, vmax=1,
    )
    step_text = ax.text(
        0.02, 0.97, f"step={frames[0][0]}", transform=ax.transAxes,
        color="white", fontsize=9, va="top",
    )

    def update(i):
        s, g = frames[i]
        img.set_data(g)
        step_text.set_text(f"step={s}")
        return img, step_text

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=60, blit=True,
    )
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=15)
    plt.close(fig)
    print(f"  GIF saved: {gif_path}")


# ── Evolutionary search ────────────────────────────────────────────────────────

def run_search() -> dict:
    print("=== iter_218 v<c Glider Search (LeakySubLightFitness) ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"  Population      : {POPULATION_SIZE}")
    print(f"  Generations     : {NUM_GENERATIONS}")
    print(f"  Elite count     : {ELITE_COUNT}")
    print(f"  Grid size       : {GRID_SIZE}x{GRID_SIZE}")
    print(f"  Sim steps       : {SIMULATION_STEPS}")
    print(f"  Seed particle   : {SEED_PARTICLE}")
    print(f"  Fitness         : LeakySubLightFitness\n")

    # Initial random population
    population = [
        rule_dict_to_chromosome(generate_c2_rule(rng))
        for _ in range(POPULATION_SIZE)
    ]

    fitnesses, metrics_l = evaluate_population(population)
    best_idx        = int(np.argmax(fitnesses))
    best_fitness    = float(fitnesses[best_idx])
    best_chrom      = population[best_idx].copy()
    best_metrics    = metrics_l[best_idx]
    best_generation = 0
    max_ever        = best_fitness

    gen_log: list[tuple[int, float]] = [(0, best_fitness)]

    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    print(
        f"  Gen  0: champion={best_fitness:.4f}  mean={np.mean(fitnesses):.4f}"
        f"  non_zero={n_nonzero}"
    )

    for gen in range(1, NUM_GENERATIONS + 1):
        elite   = select_top_k(population, fitnesses, ELITE_COUNT)
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
        n_nonzero    = sum(1 for f in fitnesses if f > 0.0)

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_chrom      = population[gen_best_idx].copy()
            best_metrics    = metrics_l[gen_best_idx]
            best_generation = gen

        if best_fitness > max_ever:
            max_ever = best_fitness

        gen_log.append((gen, best_fitness))

        print(
            f"  Gen {gen:2d}: champion={best_fitness:.4f}  gen_best={gen_best:.4f}"
            f"  mean={gen_mean:.4f}  non_zero={n_nonzero}"
        )

    return {
        "best_fitness":    best_fitness,
        "max_ever":        max_ever,
        "best_chrom":      best_chrom,
        "best_metrics":    best_metrics,
        "best_generation": best_generation,
        "gen_log":         gen_log,
    }


# ── Reporting ─────────────────────────────────────────────────────────────────

def write_results(result: dict) -> list[str]:
    print("\n=== Writing artifacts ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    artifacts: list[str] = []

    # 1. champion_vc_rule.json
    rule_dict = chromosome_to_rule_dict(result["best_chrom"])
    m         = result["best_metrics"] or {}
    payload = {
        "iteration":          "iter_218",
        "fitness_function":   "LeakySubLightFitness",
        "fitness":            result["best_fitness"],
        "generation_of_best": result["best_generation"],
        "num_generations":    NUM_GENERATIONS,
        "population_size":    POPULATION_SIZE,
        "grid_size":          GRID_SIZE,
        "simulation_steps":   SIMULATION_STEPS,
        "seed_particle":      SEED_PARTICLE,
        "metrics":            m,
        "rule_dict":          {str(k): int(v) for k, v in rule_dict.items()},
        "chromosome":         result["best_chrom"].tolist(),
    }
    with open(CHAMPION_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    rel = str(CHAMPION_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/")
    print(f"  Champion rule saved: {CHAMPION_JSON}")
    artifacts.append(rel)

    # 2. evolution_log.csv
    with open(EVOLUTION_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["generation", "champion_fitness"])
        for gen, fit in result["gen_log"]:
            writer.writerow([gen, fit])
    rel = str(EVOLUTION_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/")
    print(f"  Evolution log saved: {EVOLUTION_CSV}")
    artifacts.append(rel)

    # 3. champion_vc_glider.gif  (always render, regardless of fitness)
    print("  Rendering champion GIF ...")
    render_champion_gif(rule_dict, CHAMPION_GIF, steps=SIMULATION_STEPS)
    rel = str(CHAMPION_GIF.relative_to(PROJECT_ROOT)).replace("\\", "/")
    artifacts.append(rel)

    print(f"\n  best_fitness    = {result['best_fitness']:.6f}")
    print(f"  max_ever        = {result['max_ever']:.6f}")
    print(f"  best_generation = {result['best_generation']}")
    if m:
        print(f"  base_fitness       = {m.get('base_fitness', 'n/a')}")
        print(f"  total_conservation = {m.get('total_conservation_score', 'n/a')}")
        print(f"  avg_velocity       = {m.get('avg_velocity', 'n/a')}")
        print(f"  net_displacement   = {m.get('net_displacement', 'n/a')}")
        print(f"  initial_bits       = {m.get('initial_bits', 'n/a')}")
        print(f"  conservation_factors = {m.get('conservation_factors', 'n/a')}")

    return artifacts


def main() -> int:
    global OUTPUT_DIR, CHAMPION_JSON, EVOLUTION_CSV, CHAMPION_GIF

    parser = argparse.ArgumentParser(description="v<c glider evolutionary search")
    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="Override champion output path (e.g. archive/iter_218/results/champion_rule.json)",
    )
    args = parser.parse_args()

    if args.output_file:
        champion_path = Path(args.output_file)
        if not champion_path.is_absolute():
            champion_path = PROJECT_ROOT / champion_path
        OUTPUT_DIR   = champion_path.parent
        CHAMPION_JSON = champion_path
        EVOLUTION_CSV = OUTPUT_DIR / "evolution_log.csv"
        CHAMPION_GIF  = OUTPUT_DIR / "champion_vc_glider.gif"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result    = run_search()
    artifacts = write_results(result)

    print("\n=== Summary ===")
    print(f"  best_fitness    = {result['best_fitness']:.6f}")
    print(f"  max_ever        = {result['max_ever']:.6f}")
    print(f"  best_generation = {result['best_generation']}")
    print(f"  artifacts       = {artifacts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
