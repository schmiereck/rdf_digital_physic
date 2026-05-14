#!/usr/bin/env python3
"""
evolve_velocity_stability.py

Evolutionary search using the late-displacement fitness metric validated in iter_156.
Fitness = Euclidean distance of center-of-mass between t=1200 and t=2000.

Generates a fresh population of 100 C2-symmetric rules (seed=157), evaluates each
for 2000 steps, and saves the full evaluated population to:
  archive/iter_157/results/population_gen1.json
"""

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent

GRID_SIZE       = 150
SOUP_DENSITY    = 0.25
SOUP_SEED       = 42
RULE_SEED       = 157
POPULATION_SIZE = 100
TOTAL_STEPS     = 2000
LATE_START      = 1200
MAX_ATTEMPTS    = 50000
KERNEL_PAIRS    = 8


# ── HEX / C2 rule helpers ──────────────────────────────────────────────────────

def _rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def _rotate_c2(state: int) -> int:
    return _rotate60_msb(_rotate60_msb(_rotate60_msb(state)))


def _is_valid_c2_pair(a: int, b: int) -> bool:
    if a == b or a == 0 or b == 0:
        return False
    ra = _rotate_c2(a)
    rb = _rotate_c2(b)
    return len({a, b, ra, rb}) == 4


def _try_build_c2_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        ra = _rotate_c2(a)
        rb = _rotate_c2(b)
        for src, dst in [(a, b), (b, a), (ra, rb), (rb, ra)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def generate_random_c2_rule(rng: random.Random, n_pairs: int = KERNEL_PAIRS) -> dict:
    for _ in range(MAX_ATTEMPTS):
        pairs = []
        ok = True
        for _ in range(n_pairs):
            found = False
            for _ in range(300):
                a = rng.randint(1, 127)
                b = rng.randint(1, 127)
                if _is_valid_c2_pair(a, b):
                    pairs.append((a, b))
                    found = True
                    break
            if not found:
                ok = False
                break
        if not ok:
            continue
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate valid C2 rule with {n_pairs} pairs")


# ── Simulation helpers ─────────────────────────────────────────────────────────

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
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
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


def make_soup() -> np.ndarray:
    rng = np.random.default_rng(SOUP_SEED)
    return (rng.random((GRID_SIZE, GRID_SIZE)) < SOUP_DENSITY).astype(np.uint8)


# ── Fitness evaluation ─────────────────────────────────────────────────────────

def evaluate_late_displacement(rule_dict: dict, soup: np.ndarray) -> dict:
    """Fitness = Euclidean distance of COM between t=1200 and t=2000."""
    lut  = _rule_to_lut(rule_dict)
    grid = np.copy(soup)

    for _ in range(LATE_START):
        grid = _step_grid(grid, lut)
    com_1200 = _center_of_mass(grid)

    for _ in range(TOTAL_STEPS - LATE_START):
        grid = _step_grid(grid, lut)
    com_2000 = _center_of_mass(grid)

    dx = com_2000[0] - com_1200[0]
    dy = com_2000[1] - com_1200[1]
    fitness = math.sqrt(dx * dx + dy * dy)

    return {
        "fitness":    round(fitness, 8),
        "com_t1200":  [round(com_1200[0], 4), round(com_1200[1], 4)],
        "com_t2000":  [round(com_2000[0], 4), round(com_2000[1], 4)],
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    output_dir = PROJECT_ROOT / "archive" / "iter_157" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {POPULATION_SIZE} random C2-symmetric rules (seed={RULE_SEED}) ...")
    rng = random.Random(RULE_SEED)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_id   = f"rule_{i:03d}"
        rule_dict = generate_random_c2_rule(rng)
        rules.append((rule_id, rule_dict))
        if i % 10 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE} rules ...")

    soup = make_soup()
    print(f"\nEvaluating {POPULATION_SIZE} rules "
          f"({TOTAL_STEPS} steps, fitness=COM displacement t={LATE_START}->{TOTAL_STEPS}, "
          f"grid={GRID_SIZE}x{GRID_SIZE}) ...")

    population = {}
    for rule_id, rule_dict in rules:
        metrics   = evaluate_late_displacement(rule_dict, soup)
        fitness   = metrics["fitness"]
        print(f"  {rule_id}: fitness={fitness:.6f}  "
              f"com_1200={metrics['com_t1200']}  com_2000={metrics['com_t2000']}")
        population[rule_id] = {
            "fitness":   fitness,
            "com_t1200": metrics["com_t1200"],
            "com_t2000": metrics["com_t2000"],
            "rule_dict": rule_dict,
        }

    out_json = output_dir / "population_gen1.json"
    with open(out_json, "w") as f:
        json.dump(population, f, indent=2)
    print(f"\nSaved: {out_json}")

    fitnesses        = [v["fitness"] for v in population.values()]
    max_fitness      = float(max(fitnesses))
    mean_fitness     = float(np.mean(fitnesses))
    num_viable       = sum(1 for f in fitnesses if f > 0.1)
    threshold_met    = any(f > 0.2 for f in fitnesses)
    best_rule        = max(population, key=lambda k: population[k]["fitness"])

    print("\n=== Generation 1 Summary ===")
    print(f"  max_fitness:      {max_fitness:.6f}")
    print(f"  mean_fitness:     {mean_fitness:.6f}")
    print(f"  num_viable_rules: {num_viable}  (fitness > 0.1)")
    print(f"  threshold_met:    {threshold_met}  (any fitness > 0.2)")
    print(f"  best_rule:        {best_rule}")

    experimenter_view = (
        f"Late-displacement fitness (COM Euclidean distance t=1200->t=2000) applied to "
        f"a fresh population of {POPULATION_SIZE} random C2-symmetric rules (seed={RULE_SEED}). "
        f"Grid: {GRID_SIZE}x{GRID_SIZE}, soup density=0.25, soup seed=42. "
        f"max_fitness={max_fitness:.4f}, mean_fitness={mean_fitness:.4f}, "
        f"num_viable={num_viable} (>0.1). "
        f"Best rule: {best_rule} (fitness={max_fitness:.4f}). "
        + ("SUCCESS: At least one rule exceeded the 0.2 threshold." if threshold_met
           else "BELOW THRESHOLD: No rule exceeded the 0.2 fitness threshold.")
    )

    yaml_block = {
        "status": "ok",
        "artifacts": [
            str(out_json.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        ],
        "metrics": {
            "max_fitness":      round(max_fitness,  6),
            "mean_fitness":     round(mean_fitness, 6),
            "num_viable_rules": num_viable,
        },
        "log_excerpt": (
            f"  max_fitness:      {max_fitness:.6f}\n"
            f"  mean_fitness:     {mean_fitness:.6f}\n"
            f"  num_viable_rules: {num_viable}\n"
            f"  threshold_met:    {threshold_met}\n"
            f"  best_rule:        {best_rule}\n"
            f"  Saved: {out_json}\n"
        ),
        "experimenter_view": experimenter_view,
        "notes": (
            f"Gen-1 late-displacement search; "
            f"max={max_fitness:.4f}, viable={num_viable}, "
            f"threshold_met={threshold_met}"
        ),
    }

    yaml_str = yaml.dump(yaml_block, default_flow_style=False, sort_keys=False,
                         allow_unicode=True)
    print("\n---\n")
    print(yaml_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
