#!/usr/bin/env python3
"""
run_v_less_than_c_search.py  —  Evolutionary search for a v<c glider.

Runs a 15-generation evolutionary search using SparseGliderFitness on a
128x128 toroidal hexagonal grid with a 3-bit L-tromino seed.

Population: 100 C2-symmetric rules.
Elitism   : 10% (top 10 rules survive each generation unchanged).
Fitness   : SparseGliderFitness (from fitness_v2.py).

Outputs:
  archive/iter_200.1/results/champion_v_lt_c_rule.json
  archive/iter_200.1/results/champion_v_lt_c_glider.gif
  archive/iter_200.1/results/evolution_summary.csv
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import (
    generate_random_c2_rule,
    rule_dict_to_lut,
    step_grid,
    _rotate_c2,
    _try_build_c2_rule,
)
from fitness_v2 import SparseGliderFitness, _make_particle_grid


# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_200.1" / "results"
CHAMPION_JSON = RESULTS_DIR / "champion_v_lt_c_rule.json"
CHAMPION_GIF  = RESULTS_DIR / "champion_v_lt_c_glider.gif"
SUMMARY_CSV   = RESULTS_DIR / "evolution_summary.csv"


# ── Hyper-parameters ──────────────────────────────────────────────────────────

POPULATION_SIZE  = 100
NUM_GENERATIONS  = 15
ELITE_FRACTION   = 0.10
ELITE_COUNT      = max(1, int(POPULATION_SIZE * ELITE_FRACTION))
GRID_SIZE        = 128
RNG_SEED         = 200_100
GIF_STEPS        = 500
GIF_FRAME_STRIDE = 5

# 3-bit L-Tromino: (dr, dc) offsets from grid centre
#   X .
#   X X
L_TROMINO: list[tuple[int, int]] = [(-1, -1), (0, -1), (0, 0)]


# ── Mutation helpers ──────────────────────────────────────────────────────────

def _extract_base_pairs(rule: dict) -> list[tuple[int, int]]:
    """Extract one (a, b) representative per C2-orbit from a rule dict."""
    visited: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for a, b in rule.items():
        if a not in visited and b not in visited:
            pairs.append((int(a), int(b)))
            visited.add(int(a))
            visited.add(int(b))
            ra, rb = _rotate_c2(int(a)), _rotate_c2(int(b))
            visited.add(ra)
            visited.add(rb)
    return pairs


def mutate_c2_rule(
    rule: dict,
    rng: random.Random,
    n_add: int = 1,
    n_remove: int = 1,
) -> dict:
    """Return a C2-symmetric mutation of *rule*.

    Adds *n_add* random pairs and removes *n_remove* existing pairs.
    Falls back to a fresh random rule if the modified pair list is
    inconsistent.
    """
    pairs = _extract_base_pairs(rule)

    # Remove
    for _ in range(n_remove):
        if pairs:
            idx = rng.randrange(len(pairs))
            pairs.pop(idx)

    # Add
    for _ in range(n_add):
        a = rng.randint(1, 127)
        b = rng.randint(1, 127)
        while b == a:
            b = rng.randint(1, 127)
        pairs.append((a, b))

    new_rule = _try_build_c2_rule(pairs)
    if new_rule is None:
        return generate_random_c2_rule(rng)
    return new_rule


# ── Evolutionary search ───────────────────────────────────────────────────────

def run_evolution() -> dict:
    rng = random.Random(RNG_SEED)
    fitness_fn = SparseGliderFitness(
        grid_size=GRID_SIZE,
        simulation_steps=200,
        checkpoint_every=50,
        particle=L_TROMINO,
    )

    print("=== v<c Glider Evolutionary Search ===")
    print(f"  Seed      : 3-bit L-Tromino {L_TROMINO}")
    print(f"  Grid      : {GRID_SIZE}x{GRID_SIZE} torus")
    print(f"  Pop size  : {POPULATION_SIZE}")
    print(f"  Elites    : {ELITE_COUNT}")
    print(f"  Fitness   : {fitness_fn.name}")
    print(f"  Gens      : {NUM_GENERATIONS}")
    print()

    # ── Initial population ─────────────────────────────────────────────────────
    print("Generating initial population...")
    population: list[dict] = [
        generate_random_c2_rule(rng) for _ in range(POPULATION_SIZE)
    ]
    print(f"  Generated {len(population)} rules.")

    best_rule: dict       = {}
    best_fitness: float   = -1.0
    best_generation: int  = -1
    summary_rows: list[dict] = []

    # ── Generation loop ────────────────────────────────────────────────────────
    for gen in range(NUM_GENERATIONS):
        # Evaluate
        fitnesses = []
        for rule in population:
            f, _ = fitness_fn(rule)
            fitnesses.append(f)

        fitnesses_arr = np.array(fitnesses, dtype=np.float64)
        gen_best_idx  = int(np.argmax(fitnesses_arr))
        gen_best      = float(fitnesses_arr[gen_best_idx])
        gen_mean      = float(np.mean(fitnesses_arr))

        print(
            f"  Gen {gen+1:2d}/{NUM_GENERATIONS}: "
            f"best={gen_best:.6f}  mean={gen_mean:.6f}  "
            f"non_zero={int(np.sum(fitnesses_arr > 0))}"
        )
        summary_rows.append({"generation": gen + 1, "best_fitness": gen_best})

        if gen_best > best_fitness:
            best_fitness    = gen_best
            best_rule       = population[gen_best_idx]
            best_generation = gen + 1

        # ── Breed next generation ──────────────────────────────────────────────
        order  = np.argsort(fitnesses_arr)[::-1]
        elites = [population[int(i)] for i in order[:ELITE_COUNT]]

        new_pop: list[dict] = list(elites)
        while len(new_pop) < POPULATION_SIZE:
            parent = rng.choice(elites)
            child  = mutate_c2_rule(parent, rng, n_add=1, n_remove=1)
            new_pop.append(child)

        population = new_pop

    return {
        "best_rule":       best_rule,
        "best_fitness":    best_fitness,
        "best_generation": best_generation,
        "summary_rows":    summary_rows,
    }


# ── GIF renderer ─────────────────────────────────────────────────────────────

def render_glider_gif(rule_dict: dict, gif_path: Path, steps: int = GIF_STEPS) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut    = rule_dict_to_lut(rule_dict)
    grid   = _make_particle_grid(L_TROMINO, GRID_SIZE)
    frames = [(0, grid.copy())]

    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        if step % GIF_FRAME_STRIDE == 0 or step == steps:
            frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_title("iter_200.1 — v<c glider champion")
    ax.set_xlabel("col")
    ax.set_ylabel("row")

    crop = 30  # show a 60×60 window around the centre
    c = GRID_SIZE // 2
    img = ax.imshow(
        frames[0][1][c - crop: c + crop, c - crop: c + crop],
        origin="upper", interpolation="nearest", cmap="hot", vmin=0, vmax=1,
    )
    step_text = ax.text(
        0.02, 0.97, f"step={frames[0][0]}",
        transform=ax.transAxes, color="white", fontsize=10, va="top",
    )

    def update(i):
        step, g = frames[i]
        img.set_data(g[c - crop: c + crop, c - crop: c + crop])
        step_text.set_text(f"step={step}")
        return img, step_text

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=80, blit=True,
    )
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=12)
    plt.close(fig)
    print(f"  GIF saved: {gif_path}  ({len(frames)} frames)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    result = run_evolution()

    champion     = result["best_rule"]
    champ_fit    = result["best_fitness"]
    champ_gen    = result["best_generation"]
    summary_rows = result["summary_rows"]

    # ── Save champion rule ─────────────────────────────────────────────────────
    payload = {
        "iteration":        "iter_200.1",
        "fitness_function": "SparseGliderFitness",
        "seed_particle":    "3-bit L-Tromino",
        "seed_cells":       L_TROMINO,
        "fitness":          champ_fit,
        "generation":       champ_gen,
        "num_generations":  NUM_GENERATIONS,
        "population_size":  POPULATION_SIZE,
        "elite_count":      ELITE_COUNT,
        "grid_size":        GRID_SIZE,
        "rule_dict":        {str(k): int(v) for k, v in champion.items()},
    }
    with open(CHAMPION_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nChampion rule saved : {CHAMPION_JSON}")
    print(f"  champion_fitness  = {champ_fit:.6f}")
    print(f"  found in gen      = {champ_gen}")

    # ── Save evolution summary CSV ─────────────────────────────────────────────
    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["generation", "best_fitness"])
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Evolution summary   : {SUMMARY_CSV}")

    # ── Render GIF ─────────────────────────────────────────────────────────────
    print(f"Rendering GIF ({GIF_STEPS} steps) ...")
    render_glider_gif(champion, CHAMPION_GIF, steps=GIF_STEPS)

    print("\n=== Done ===")
    print(f"  champion_fitness  = {champ_fit:.6f}")
    print(f"  best_generation   = {champ_gen}")
    print(f"  artifacts:")
    for p in [CHAMPION_JSON, CHAMPION_GIF, SUMMARY_CSV]:
        print(f"    {p.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
