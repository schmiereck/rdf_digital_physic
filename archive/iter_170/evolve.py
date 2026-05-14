#!/usr/bin/env python3
"""
iter_170 evolve.py  -  Asymmetric L-Tromino Glider Nursery

Strategy: place an asymmetric 3-bit L-tromino at cells (63,63), (64,63),
(64,64) of an empty 128x128 grid and evaluate C2-symmetric rules.

Hypothesis: breaking the C2-symmetry of the seed allows motion, unlike
the symmetric 2x2 block used in iter_167.

Fitness = displacement / (1 + final_bit_count)
Output:   archive/iter_170/results/gen_0_results.json
"""

import concurrent.futures
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

OUTPUT_DIR = Path(__file__).parent / "results"

POPULATION_SIZE = 100
GRID_SIZE       = 128
STEPS           = 200
RULE_SEED       = 170
MAX_ATTEMPTS    = 10000
INITIAL_BITS    = 3

# L-tromino: (row, col) pairs
LTROMINO_CELLS  = [(63, 63), (64, 63), (64, 64)]


# ── C2-symmetric rule helpers ──────────────────────────────────────────────────

def rotate60(state: int) -> int:
    """Rotate hex neighbourhood 60 deg CW (MSB: bit6=center, bit5=E ... bit0=NE)."""
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1   # E
    b2 = (state >> 4) & 1   # SE
    b3 = (state >> 3) & 1   # SW
    b4 = (state >> 2) & 1   # W
    b5 = (state >> 1) & 1   # NW
    b6 = (state >> 0) & 1   # NE
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    """180 deg rotation = three 60 deg steps."""
    return rotate60(rotate60(rotate60(state)))


def try_build_c2_rule(pairs: list) -> dict | None:
    """Build a C2-symmetric rule from kernel pairs; return None on conflict."""
    rule: dict = {}
    for a, b in pairs:
        rot_a = rotate_c2(a)
        rot_b = rotate_c2(b)
        for src, dst in [(a, b), (b, a), (rot_a, rot_b), (rot_b, rot_a)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def generate_random_c2_rule(rng: random.Random) -> tuple[dict, list]:
    """Generate a random C2-symmetric rule with 2-4 kernel pairs."""
    for _ in range(MAX_ATTEMPTS):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))

        rule = try_build_c2_rule(pairs)
        if rule is not None:
            return rule, pairs

    raise RuntimeError("Failed to generate a valid C2 rule after many attempts")


# ── Simulation ─────────────────────────────────────────────────────────────────

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
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
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


def _center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def initialize_ltromino(grid_size: int, cells: list) -> np.ndarray:
    """Place L-tromino at the specified (row, col) positions."""
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in cells:
        grid[r, c] = 1
    return grid


def evaluate_rule_fitness(
    final_grid: np.ndarray,
    initial_com: tuple[float, float],
) -> dict:
    """Fitness = displacement / (1 + final_bit_count)."""
    final_com       = _center_of_mass(final_grid)
    final_bit_count = int(final_grid.sum())
    dx              = final_com[0] - initial_com[0]
    dy              = final_com[1] - initial_com[1]
    displacement    = math.sqrt(dx * dx + dy * dy)
    fitness         = displacement / (1.0 + final_bit_count)
    return {
        "fitness":         fitness,
        "displacement":    displacement,
        "final_bit_count": final_bit_count,
        "final_com":       list(final_com),
    }


def evaluate_rule(rule_dict: dict) -> dict:
    lut         = _rule_to_lut(rule_dict)
    grid        = initialize_ltromino(GRID_SIZE, LTROMINO_CELLS)
    initial_com = _center_of_mass(grid)

    for _ in range(STEPS):
        grid = _step_grid(grid, lut)

    return {
        "initial_com": list(initial_com),
        **evaluate_rule_fitness(grid, initial_com),
    }


def _evaluate_worker(args: tuple) -> dict:
    rule_id, rule_dict = args
    result = evaluate_rule(rule_dict)
    return {"rule_id": rule_id, "rule_dict": rule_dict, **result}


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"=== iter_170: Asymmetric L-Tromino Glider Nursery ===")
    print(f"L-tromino cells: {LTROMINO_CELLS}")
    print(f"Generating {POPULATION_SIZE} C2 rules (seed={RULE_SEED}) ===")
    rng   = random.Random(RULE_SEED)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict, _ = generate_random_c2_rule(rng)
        rules.append((f"rule_{i:03d}", rule_dict))
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE}")

    print(f"\n=== Evaluating ({STEPS} steps, {GRID_SIZE}x{GRID_SIZE}, L-tromino seed) ===")

    population = []
    workers    = min(4, POPULATION_SIZE)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_evaluate_worker, r): r[0] for r in rules}
        done    = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            print(
                f"  [{done:3d}/{POPULATION_SIZE}] {result['rule_id']}: "
                f"fitness={result['fitness']:.6f}  "
                f"disp={result['displacement']:.4f}  "
                f"bits={result['final_bit_count']:5d}"
            )

    population.sort(key=lambda e: e["fitness"], reverse=True)
    champion    = population[0]

    fitnesses    = [e["fitness"] for e in population]
    mean_fitness = float(np.mean(fitnesses))
    max_fitness  = float(champion["fitness"])

    print(f"\n=== Summary ===")
    print(f"  mean_fitness:          {mean_fitness:.8f}")
    print(f"  max_fitness:           {max_fitness:.8f}")
    print(f"  top_rule_id:           {champion['rule_id']}")
    print(f"  top_rule_displacement: {champion['displacement']:.6f}")
    print(f"  top_rule_final_bits:   {champion['final_bit_count']}")
    print(f"  initial_bits:          {INITIAL_BITS}")
    hypothesis_met = max_fitness > 0.1
    print(f"  hypothesis_met (>0.1): {hypothesis_met}")

    summary = {
        "experiment":            "iter_170_ltromino_nursery",
        "hypothesis":            "asymmetric_seed_enables_motion",
        "grid_size":             GRID_SIZE,
        "steps":                 STEPS,
        "rule_seed":             RULE_SEED,
        "initial_bits":          INITIAL_BITS,
        "ltromino_cells":        LTROMINO_CELLS,
        "fitness_formula":       "displacement / (1 + final_bit_count)",
        "mean_fitness":          round(mean_fitness, 10),
        "max_fitness":           round(max_fitness, 10),
        "hypothesis_met":        hypothesis_met,
        "top_rule_id":           champion["rule_id"],
        "top_rule_displacement": round(champion["displacement"], 8),
        "top_rule_final_bits":   champion["final_bit_count"],
        "top_rule_initial_com":  [round(x, 4) for x in champion["initial_com"]],
        "top_rule_final_com":    [round(x, 4) for x in champion["final_com"]],
        "population": [
            {
                "rule_id":         e["rule_id"],
                "rule":            {str(k): v for k, v in e["rule_dict"].items()},
                "fitness":         round(e["fitness"], 10),
                "displacement":    round(e["displacement"], 8),
                "final_bit_count": e["final_bit_count"],
                "final_com":       [round(x, 4) for x in e["final_com"]],
                "initial_com":     [round(x, 4) for x in e["initial_com"]],
            }
            for e in population
        ],
    }

    json_path = OUTPUT_DIR / "gen_0_results.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
