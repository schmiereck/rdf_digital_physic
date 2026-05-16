#!/usr/bin/env python3
"""
run_iter_192_leaky_evolution.py  —  iter_192 leaky-conservation evolutionary search.

Strategy A: Evolve a motion-first population towards bit conservation using a
soft penalty (LeakyConservationCollisionFitness).

Setup
-----
* Warm start : archive/iter_191/results/warm_start_population.json
               (100 mutants of g10_rule_001)
* Fitness    : LeakyConservationCollisionFitness
               fitness = staged_score / (1.0 + bit_error)
* Generations: 10
* Elite      : 10% (== 10 individuals)
* Simulation : 400 steps, midpoint at 200, 128x128 torus

Outputs (under archive/iter_192/iter_001/results/):
  - generation_stats.json   : per-gen mean / max / std fitness + non_zero counts
  - final_population.json   : every rule + fitness at the final generation
  - champion_rule.json      : champion rule with fitness, staged_score, bit_error
  - fitness_plot.png        : max + mean fitness vs generation
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import rule_dict_to_lut, step_grid
from fitness import LeakyConservationCollisionFitness, _make_staged_grid


# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT   = Path(__file__).parent.parent
WARM_START     = PROJECT_ROOT / "archive" / "iter_191" / "results" / "warm_start_population.json"
OUTPUT_DIR     = PROJECT_ROOT / "archive" / "iter_192" / "iter_001" / "results"
GEN_STATS      = OUTPUT_DIR / "generation_stats.json"
FINAL_POP      = OUTPUT_DIR / "final_population.json"
CHAMPION_JSON  = OUTPUT_DIR / "champion_rule.json"
FIT_PLOT       = OUTPUT_DIR / "fitness_plot.png"


# ── GA hyper-parameters ──────────────────────────────────────────────────────

POPULATION_SIZE = 100
NUM_GENERATIONS = 10
ELITE_FRACTION  = 0.10
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.01
LUT_SIZE        = 128
RNG_SEED        = 192_001
HORIZON         = 400
MIDPOINT        = 200
GRID_SIZE       = 128

ELITE_COUNT = max(2, int(POPULATION_SIZE * ELITE_FRACTION))


# ── Chromosome <-> rule_dict conversions ─────────────────────────────────────

def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Population loading ────────────────────────────────────────────────────────

def load_warm_start(path: Path) -> list[np.ndarray]:
    with open(path) as f:
        data = json.load(f)
    population = []
    for entry in data:
        chrom = np.asarray(entry["chromosome"], dtype=np.uint8)
        population.append(chrom)
    return population


# ── Fitness evaluation ────────────────────────────────────────────────────────

_FITNESS = LeakyConservationCollisionFitness(
    horizon=HORIZON, midpoint=MIDPOINT, grid_size=GRID_SIZE,
)


def evaluate_population(population: list) -> tuple[list, list]:
    n         = len(population)
    fitnesses = [0.0] * n
    metrics_l = [None] * n
    for i, chrom in enumerate(population):
        rule_dict    = chromosome_to_rule_dict(chrom)
        m            = _FITNESS.evaluate(rule_dict)
        fitnesses[i] = float(m["fitness"])
        metrics_l[i] = m
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


# ── Rendering helpers ─────────────────────────────────────────────────────────

def render_fitness_plot(stats: list[dict], plot_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gens = [s["generation"] for s in stats]
    max_ = [s["max"]        for s in stats]
    mean = [s["mean"]       for s in stats]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    ax.plot(gens, max_,  marker="o", label="max")
    ax.plot(gens, mean,  marker="s", label="mean")
    ax.set_xlabel("generation")
    ax.set_ylabel("fitness")
    ax.set_title("iter_192 — LeakyConservationCollisionFitness population fitness")
    ax.set_ylim(-0.05, 2.1)
    ax.grid(True, alpha=0.3)
    ax.legend()
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(plot_path), bbox_inches="tight")
    plt.close(fig)


def render_collision_gif(
    rule_dict: dict, gif_path: Path, steps: int = HORIZON, frame_stride: int = 4,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut    = rule_dict_to_lut(rule_dict)
    grid   = _make_staged_grid(GRID_SIZE)
    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        if step % frame_stride == 0 or step == steps:
            frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title("iter_192 LeakyConservationCollisionFitness champion")
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

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=80, blit=True,
    )
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=12)
    plt.close(fig)


# ── Evolutionary search ───────────────────────────────────────────────────────

def run_search() -> dict:
    print("=== iter_192 Leaky-Conservation Evolutionary Search ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"  Warm start : {WARM_START}")
    print(f"  Population : {POPULATION_SIZE}   Generations: {NUM_GENERATIONS}")
    print(f"  Elite      : {ELITE_COUNT}        Crossover: {CROSSOVER_RATE}")
    print(f"  Mutation   : {MUTATION_RATE}      Horizon: {HORIZON}")
    print(f"  Grid size  : {GRID_SIZE}x{GRID_SIZE} torus")
    print(f"  Fitness    : LeakyConservationCollisionFitness\n")

    population = load_warm_start(WARM_START)
    print(f"  Loaded {len(population)} warm-start individuals from iter_191.\n")

    fitnesses, metrics_l = evaluate_population(population)
    best_idx        = int(np.argmax(fitnesses))
    best_fitness    = float(fitnesses[best_idx])
    best_chrom      = population[best_idx].copy()
    best_metrics    = metrics_l[best_idx]
    best_generation = 0

    stats: list[dict] = []
    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    stats.append({
        "generation": 0,
        "max":        float(np.max(fitnesses)),
        "mean":       float(np.mean(fitnesses)),
        "std":        float(np.std(fitnesses)),
        "non_zero":   int(n_nonzero),
    })
    print(
        f"  Gen  0: max={stats[-1]['max']:.4f}  mean={stats[-1]['mean']:.4f}  "
        f"std={stats[-1]['std']:.4f}  non_zero={n_nonzero}"
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
        gen_std      = float(np.std(fitnesses))

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_chrom      = population[gen_best_idx].copy()
            best_metrics    = metrics_l[gen_best_idx]
            best_generation = gen

        n_nonzero = sum(1 for f in fitnesses if f > 0.0)
        stats.append({
            "generation": gen,
            "max":        gen_best,
            "mean":       gen_mean,
            "std":        gen_std,
            "non_zero":   int(n_nonzero),
        })
        print(
            f"  Gen {gen:2d}: max={gen_best:.4f}  mean={gen_mean:.4f}  "
            f"std={gen_std:.4f}  non_zero={n_nonzero}"
        )

    return {
        "best_fitness":     float(best_fitness),
        "best_chrom":       best_chrom,
        "best_metrics":     best_metrics,
        "best_generation":  int(best_generation),
        "generations_ran":  NUM_GENERATIONS,
        "stats":            stats,
        "final_population": [c.tolist() for c in population],
        "final_fitnesses":  [float(f) for f in fitnesses],
        "final_metrics":    metrics_l,
    }


# ── Reporting ─────────────────────────────────────────────────────────────────

def write_results(result: dict) -> list[str]:
    print("\n=== Results ===")
    artifacts: list[str] = []

    # 1. generation_stats.json
    with open(GEN_STATS, "w") as f:
        json.dump(result["stats"], f, indent=2)
    print(f"  Generation stats  : {GEN_STATS}")
    artifacts.append(str(GEN_STATS.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    # 2. final_population.json
    final_pop_payload = []
    for i, (chrom, fit) in enumerate(zip(result["final_population"], result["final_fitnesses"])):
        rule_dict = chromosome_to_rule_dict(np.asarray(chrom, dtype=np.uint8))
        final_pop_payload.append({
            "index":     i,
            "fitness":   fit,
            "rule_dict": {str(k): int(v) for k, v in rule_dict.items()},
        })
    with open(FINAL_POP, "w") as f:
        json.dump(final_pop_payload, f, indent=2)
    print(f"  Final population  : {FINAL_POP}")
    artifacts.append(str(FINAL_POP.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    # 3. champion_rule.json
    rule_dict = chromosome_to_rule_dict(result["best_chrom"])
    m         = result["best_metrics"] or {}
    payload   = {
        "iteration":          "iter_192.1",
        "fitness_function":   "LeakyConservationCollisionFitness",
        "warm_start":         str(WARM_START.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "fitness":            result["best_fitness"],
        "staged_score":       m.get("staged_score"),
        "bit_error":          m.get("bit_error"),
        "generation_of_best": result["best_generation"],
        "num_generations":    NUM_GENERATIONS,
        "population_size":    POPULATION_SIZE,
        "elite_count":        ELITE_COUNT,
        "crossover_rate":     CROSSOVER_RATE,
        "mutation_rate":      MUTATION_RATE,
        "rng_seed":           RNG_SEED,
        "horizon":            HORIZON,
        "midpoint":           MIDPOINT,
        "grid_size":          GRID_SIZE,
        "metrics":            m,
        "rule_dict":          {str(k): int(v) for k, v in rule_dict.items()},
        "chromosome":         result["best_chrom"].tolist(),
    }
    with open(CHAMPION_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Champion rule     : {CHAMPION_JSON}")
    artifacts.append(str(CHAMPION_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    # 4. fitness_plot.png
    render_fitness_plot(result["stats"], FIT_PLOT)
    print(f"  Fitness plot      : {FIT_PLOT}")
    artifacts.append(str(FIT_PLOT.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    # 5. collision.gif — only if champion scored any motion
    if result["best_fitness"] > 0.0:
        gif_path = OUTPUT_DIR / "collision.gif"
        print(f"  Champion fitness {result['best_fitness']:.4f} > 0 — rendering GIF ...")
        render_collision_gif(rule_dict, gif_path, steps=HORIZON)
        print(f"  Collision GIF     : {gif_path}")
        artifacts.append(str(gif_path.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    else:
        print(f"  Champion fitness {result['best_fitness']:.4f} == 0 — no GIF generated.")

    print(f"\n  best_fitness    = {result['best_fitness']:.4f}")
    print(f"  best_generation = {result['best_generation']}")
    if m:
        print(f"  staged_score    = {m.get('staged_score', 'n/a')}")
        print(f"  approach_score  = {m.get('approach_score', 'n/a')}")
        print(f"  recession_score = {m.get('recession_score', 'n/a')}")
        print(f"  bit_error       = {m.get('bit_error', 'n/a')}")
        print(f"  initial_bits    = {m.get('initial_bits', 'n/a')}")
        print(f"  final_bits      = {m.get('final_bits', 'n/a')}")
        print(f"  d_initial       = {m.get('d_initial', 'n/a')}")
        print(f"  d_mid           = {m.get('d_mid', 'n/a')}")
        print(f"  d_final         = {m.get('d_final', 'n/a')}")

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
