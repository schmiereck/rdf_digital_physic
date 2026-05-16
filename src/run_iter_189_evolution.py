#!/usr/bin/env python3
"""
run_iter_189_evolution.py  —  iter_189.2.1 evolutionary search using
``MarginalDynamicCollisionFitness`` on a 128x128 hex torus.

Setup
-----
* Population : 100 random C2-symmetric rules
* Generations: up to 10 (early-stop the moment any rule scores 1.0)
* Seed       : two 3-bit L-tromino particles placed on a 128x128 torus
* Simulation : 400 steps, midpoint check at step 200
* Fitness    : MarginalDynamicCollisionFitness with margin = 1.0

If a champion (fitness == 1.0) is found, the rule JSON is saved to
``archive/iter_189/results/champion_rule.json`` and a collision GIF is
written to ``archive/iter_189/results/collision.gif``.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass

sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule, rule_dict_to_lut, step_grid


# ── Configuration: ca_config_2d_hex_128_torus_2_particles_3_bit_ltromino ────

_DYN_GRID_SIZE       = 128
_DYN_OBJECT_A        = [(60, 40), (61, 40), (60, 41)]
_DYN_OBJECT_B        = [(67, 87), (68, 87), (67, 88)]
_DYN_INITIAL_BITS    = len(_DYN_OBJECT_A) + len(_DYN_OBJECT_B)  # 6
_DYN_INITIAL_OBJECTS = 2
_DYN_LABEL_STRUCTURE = np.ones((3, 3), dtype=np.uint8)


def _make_dynamic_collision_grid(grid_size: int = _DYN_GRID_SIZE) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _DYN_OBJECT_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _DYN_OBJECT_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


def _two_object_com_distance(grid: np.ndarray) -> float | None:
    labels, n = label(grid, structure=_DYN_LABEL_STRUCTURE)
    if n != 2:
        return None
    coms = center_of_mass(grid, labels, [1, 2])
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


# ── MarginalDynamicCollisionFitness (copied from iter_189 validation) ────────

class MarginalDynamicCollisionFitness:
    """Fitness function that rewards a dynamic bit-conserving collision with a
    minimum displacement margin in each phase.

    Fitness is 1.0 iff ALL four conditions hold, else 0.0:
      1. Approach  : midpoint_distance < initial_distance  - margin
      2. Recession : final_distance    > midpoint_distance + margin
      3. Bit cons. : final live cells  == initial bits
      4. Obj cons. : final components  == 2
    """

    name = "MarginalDynamicCollisionFitness"

    def __init__(
        self,
        horizon: int = 400,
        midpoint: int | None = None,
        grid_size: int = _DYN_GRID_SIZE,
        margin: float = 1.0,
        rule: dict | None = None,
    ) -> None:
        self.horizon   = int(horizon)
        self.midpoint  = int(midpoint) if midpoint is not None else self.horizon // 2
        self.grid_size = int(grid_size)
        self.margin    = float(margin)
        self.rule      = rule

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("MarginalDynamicCollisionFitness: no rule supplied")

        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_dynamic_collision_grid(self.grid_size)

        initial_distance = _two_object_com_distance(grid)
        if initial_distance is None:
            return self._fail({
                "initial_distance":   None,
                "midpoint_distance":  None,
                "final_distance":     None,
                "final_bit_count":    int(grid.sum()),
                "final_object_count": 0,
            })

        midpoint_distance: float | None = None
        for step in range(1, self.horizon + 1):
            grid = step_grid(grid, lut)
            if step == self.midpoint:
                midpoint_distance = _two_object_com_distance(grid)

        final_bit_count = int(grid.sum())
        _, final_object_count = label(grid, structure=_DYN_LABEL_STRUCTURE)
        final_object_count    = int(final_object_count)
        final_distance        = _two_object_com_distance(grid)

        metrics = {
            "initial_distance":   float(initial_distance),
            "midpoint_distance":  (
                float(midpoint_distance) if midpoint_distance is not None else None
            ),
            "final_distance":     (
                float(final_distance) if final_distance is not None else None
            ),
            "final_bit_count":    final_bit_count,
            "final_object_count": final_object_count,
            "margin":             self.margin,
        }

        if midpoint_distance is None or final_distance is None:
            return self._fail(metrics)

        approach   = midpoint_distance < initial_distance  - self.margin
        recession  = final_distance    > midpoint_distance + self.margin
        bits_ok    = final_bit_count   == _DYN_INITIAL_BITS
        objects_ok = final_object_count == _DYN_INITIAL_OBJECTS

        metrics["approach"]   = bool(approach)
        metrics["recession"]  = bool(recession)
        metrics["bits_ok"]    = bool(bits_ok)
        metrics["objects_ok"] = bool(objects_ok)

        fitness = 1.0 if (approach and recession and bits_ok and objects_ok) else 0.0
        metrics["fitness"] = float(fitness)
        return metrics

    @staticmethod
    def _fail(metrics: dict) -> dict:
        metrics.setdefault("approach",   False)
        metrics.setdefault("recession",  False)
        metrics.setdefault("bits_ok",    False)
        metrics.setdefault("objects_ok", False)
        metrics["fitness"] = 0.0
        return metrics

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)


# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).parent.parent
OUTPUT_DIR    = PROJECT_ROOT / "archive" / "iter_189" / "results"
CHAMPION_JSON = OUTPUT_DIR / "champion_rule.json"
CHAMPION_GIF  = OUTPUT_DIR / "collision.gif"


# ── GA hyper-parameters ─────────────────────────────────────────────────────

POPULATION_SIZE = 100
NUM_GENERATIONS = 10
ELITE_FRACTION  = 0.10
DENSITY         = 8
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.01
LUT_SIZE        = 128
RNG_SEED        = 189_201
MAX_WORKERS     = 4
HORIZON         = 400
MIDPOINT        = 200
MARGIN          = 1.0

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
    metrics   = MarginalDynamicCollisionFitness(
        horizon=HORIZON, midpoint=MIDPOINT, margin=MARGIN,
    ).evaluate(rule_dict)
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

def render_collision_gif(rule_dict: dict, gif_path: Path,
                          steps: int = HORIZON, frame_ms: int = 50) -> None:
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
    ax.set_title("iter_189.2.1 MarginalDynamicCollisionFitness champion")
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


# ── Evolutionary search ─────────────────────────────────────────────────────

def run_search() -> dict:
    print("=== iter_189.2.1 Evolutionary Search ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"  Config: ca_config_2d_hex_128_torus_2_particles_3_bit_ltromino")
    print(f"  Population : {POPULATION_SIZE}   Generations(max): {NUM_GENERATIONS}")
    print(f"  Density    : {DENSITY}           Elite: {ELITE_COUNT}")
    print(f"  Horizon    : {HORIZON}           Midpoint: {MIDPOINT}   Margin: {MARGIN}")
    print(f"  Fitness    : MarginalDynamicCollisionFitness\n")

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
    generations_ran = 0

    n_nonzero = sum(1 for f in fitnesses if f > 0.0)
    print(f"  Gen 0: best={best_fitness:.4f}  mean={float(np.mean(fitnesses)):.4f}  "
          f"non_zero={n_nonzero}")

    champion_found = best_fitness >= 1.0

    for gen in range(1, NUM_GENERATIONS + 1):
        if champion_found:
            break
        generations_ran = gen
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
        "champion_found":  bool(champion_found),
        "best_fitness":    float(best_fitness),
        "best_chrom":      best_chrom,
        "best_metrics":    best_metrics,
        "best_generation": int(best_generation),
        "generations_ran": int(generations_ran),
    }


# ── Reporting ───────────────────────────────────────────────────────────────

def write_results(result: dict) -> list:
    print("\n=== Results ===")
    artifacts: list[str] = []

    if not result["champion_found"]:
        print(f"  No champion found. Best fitness = {result['best_fitness']:.4f}")
        if result["best_metrics"] is not None:
            print(f"  Best metrics: {result['best_metrics']}")
        return artifacts

    rule_dict = chromosome_to_rule_dict(result["best_chrom"])
    payload = {
        "iteration":          "iter_189.2.1",
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
        "margin":             MARGIN,
        "grid_size":          _DYN_GRID_SIZE,
        "object_a":           _DYN_OBJECT_A,
        "object_b":           _DYN_OBJECT_B,
        "fitness_function":   "MarginalDynamicCollisionFitness",
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
    return artifacts


def main() -> int:
    result    = run_search()
    artifacts = write_results(result)

    print("\n=== Summary ===")
    print(f"  champion_found  = {result['champion_found']}")
    print(f"  generations_ran = {result['generations_ran']}")
    print(f"  best_fitness    = {result['best_fitness']:.4f}")
    if result["champion_found"]:
        print(f"  champion_generation = {result['best_generation']}")
    print(f"  artifacts = {artifacts}")
    return 0 if result["champion_found"] else 2


if __name__ == "__main__":
    sys.exit(main())
