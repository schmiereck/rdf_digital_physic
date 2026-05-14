#!/usr/bin/env python3
"""
main.py

Generate and evaluate a population of 100 random C2-symmetric rules.

Composite fitness = late_displacement / (1 + final_bit_count)
where late_displacement = Euclidean distance of CoM between t=1200 and t=2000.

Outputs:
  archive/iter_166/results/population_gen1.json   -- full population with fitness scores
  archive/iter_166/results/champion_final_grid.png -- grid viz for the top rule
"""

import concurrent.futures
import json
import math
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_166" / "results"

POPULATION_SIZE = 100
GRID_SIZE       = 128
STEPS           = 2000
SEED            = 42
DENSITY         = 0.25
COM_T1          = 1200
COM_T2          = 2000
MAX_ATTEMPTS    = 10000
RULE_SEED       = 166


# ── C2-symmetric rule helpers ─────────────────────────────────────────────────

def rotate60(state: int) -> int:
    """Rotate hex neighbourhood 60° CW (MSB: bit6=center, bit5=E … bit0=NE)."""
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1   # E
    b2 = (state >> 4) & 1   # SE
    b3 = (state >> 3) & 1   # SW
    b4 = (state >> 2) & 1   # W
    b5 = (state >> 1) & 1   # NW
    b6 = (state >> 0) & 1   # NE
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    """180° rotation = three 60° steps."""
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


# ── Simulation ────────────────────────────────────────────────────────────────

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


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def evaluate_rule(rule_dict: dict) -> dict:
    lut  = _rule_to_lut(rule_dict)
    rng  = np.random.default_rng(SEED)
    grid = (rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)

    com_t1     = None
    com_t2     = None
    final_grid = None

    for t in range(1, STEPS + 1):
        grid = _step_grid(grid, lut)
        if t == COM_T1:
            com_t1 = _center_of_mass(grid)
        if t == COM_T2:
            com_t2     = _center_of_mass(grid)
            final_grid = grid.copy()

    dx = com_t2[0] - com_t1[0]
    dy = com_t2[1] - com_t1[1]
    late_displacement = math.sqrt(dx * dx + dy * dy)
    final_bit_count   = int(final_grid.sum())
    composite_fitness = late_displacement / (1.0 + final_bit_count)

    return {
        "composite_fitness": composite_fitness,
        "late_displacement": late_displacement,
        "final_bit_count":   final_bit_count,
        "com_at_t1200":      list(com_t1),
        "com_at_t2000":      list(com_t2),
        "final_grid":        final_grid,
    }


def _evaluate_worker(args: tuple) -> dict:
    rule_id, rule_dict = args
    result = evaluate_rule(rule_dict)
    return {
        "rule_id":           rule_id,
        "rule_dict":         rule_dict,
        "composite_fitness": result["composite_fitness"],
        "late_displacement": result["late_displacement"],
        "final_bit_count":   result["final_bit_count"],
        "com_at_t1200":      result["com_at_t1200"],
        "com_at_t2000":      result["com_at_t2000"],
        "final_grid":        result["final_grid"],
    }


# ── Visualisation ─────────────────────────────────────────────────────────────

def save_grid_image(grid: np.ndarray, path: Path, title: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap="binary", interpolation="nearest", origin="upper")
    ax.set_title(title or f"Final grid state (t={COM_T2})")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"=== Generating {POPULATION_SIZE} random C2-symmetric rules (seed={RULE_SEED}) ===")
    rng = random.Random(RULE_SEED)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict, _ = generate_random_c2_rule(rng)
        rules.append((f"rule_{i:03d}", rule_dict))
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE}")

    print(f"\n=== Evaluating {POPULATION_SIZE} rules "
          f"({STEPS} steps, {GRID_SIZE}x{GRID_SIZE}, seed={SEED}) ===")

    population = []
    workers = min(4, POPULATION_SIZE)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_evaluate_worker, r): r[0] for r in rules}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            print(f"  [{done:3d}/{POPULATION_SIZE}] {result['rule_id']}: "
                  f"fitness={result['composite_fitness']:.8f}  "
                  f"bits={result['final_bit_count']:5d}  "
                  f"disp={result['late_displacement']:.4f}")

    population.sort(key=lambda e: e["composite_fitness"], reverse=True)
    champion = population[0]

    # Champion visualisation
    png_path = OUTPUT_DIR / "champion_final_grid.png"
    save_grid_image(
        champion["final_grid"],
        png_path,
        title=(f"Champion: {champion['rule_id']} "
               f"(fitness={champion['composite_fitness']:.6f})"),
    )

    # Serialisable population list
    population_json = [
        {
            "rule_id":           e["rule_id"],
            "rule":              {str(k): v for k, v in e["rule_dict"].items()},
            "composite_fitness": round(e["composite_fitness"], 10),
            "late_displacement": round(e["late_displacement"], 8),
            "final_bit_count":   e["final_bit_count"],
            "com_at_t1200":      [round(x, 4) for x in e["com_at_t1200"]],
            "com_at_t2000":      [round(x, 4) for x in e["com_at_t2000"]],
            "generation":        1,
        }
        for e in population
    ]

    json_path = OUTPUT_DIR / "population_gen1.json"
    with open(json_path, "w") as f:
        json.dump(population_json, f, indent=2)
    print(f"\nSaved: {json_path}")

    fitnesses     = [e["composite_fitness"] for e in population_json]
    mean_fitness  = float(np.mean(fitnesses))
    max_fitness   = fitnesses[0]

    print(f"\n=== Summary ===")
    print(f"  mean_fitness:          {mean_fitness:.8f}")
    print(f"  max_fitness:           {max_fitness:.8f}")
    print(f"  top_rule_id:           {champion['rule_id']}")
    print(f"  top_rule_displacement: {champion['late_displacement']:.6f}")
    print(f"  top_rule_final_bits:   {champion['final_bit_count']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
