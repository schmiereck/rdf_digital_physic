#!/usr/bin/env python3
"""
run_iter_163.py

Gen-2 Evolutionary Breeding with Composite Fitness Metric.

Step 1: Generate Gen-1 (100 random C6-symmetric non-conserving rules) and
        evaluate each with composite fitness: late_displacement / (1 + final_bit_count)
        Save to archive/iter_159/results/population/rule_XXX.json
Step 2: Select top 10 elites from Gen-1.
Step 3: Breed Gen-2 (100 rules) via crossover + mutation on elites.
Step 4: Evaluate Gen-2 with the same fitness metric.
Step 5: Save Gen-2 to archive/iter_163/results/population/rule_XXX.json
Step 6: Create archive/iter_163/results/summary.json
"""

import concurrent.futures
import csv
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent

GEN1_POP_DIR   = PROJECT_ROOT / "archive" / "iter_159" / "results" / "population"
GEN2_POP_DIR   = PROJECT_ROOT / "archive" / "iter_163" / "results" / "population"
GEN2_RESULTS   = PROJECT_ROOT / "archive" / "iter_163" / "results"

POPULATION_SIZE = 100
ELITE_SIZE      = 10
ELITE_CARRY     = 2
MAX_ATTEMPTS    = 10000
MAX_BREED_ATTEMPTS = 300

GRID_SIZE   = 128
STEPS       = 2000
SEED        = 42
DENSITY     = 0.25
COM_T1      = 1200
COM_T2      = 2000

GEN1_RULE_SEED = 159  # rng seed for generating Gen-1 random rules

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


# ── C6-symmetric involution rule helpers ──────────────────────────────────────

def rotate60(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def apply_n_rotations(state: int, n: int) -> int:
    for _ in range(n):
        state = rotate60(state)
    return state


def try_build_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        for rot in range(6):
            a_rot = apply_n_rotations(a, rot)
            b_rot = apply_n_rotations(b, rot)
            for src, dst in [(a_rot, b_rot), (b_rot, a_rot)]:
                if src in rule:
                    if rule[src] != dst:
                        return None
                else:
                    rule[src] = dst
    return rule


def is_nonconserving(pairs: list) -> bool:
    return any(bin(a).count('1') != bin(b).count('1') for a, b in pairs)


def generate_random_rule(rng: random.Random) -> tuple[dict, list]:
    for _ in range(MAX_ATTEMPTS):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))

        if not is_nonconserving(pairs):
            continue

        rule = try_build_rule(pairs)
        if rule is not None:
            return rule, pairs

    raise RuntimeError("Failed to generate a valid rule after many attempts")


# ── Kernel pair extraction and breeding ───────────────────────────────────────

def _canonical_pair(a: int, b: int) -> tuple:
    best = None
    ca, cb = a, b
    for _ in range(6):
        for p in ((ca, cb), (cb, ca)):
            if best is None or p < best:
                best = p
        ca = rotate60(ca)
        cb = rotate60(cb)
    return best


def extract_kernel_pairs(rule_dict: dict) -> list:
    seen = set()
    pairs = []
    for a_str, b in rule_dict.items():
        a = int(a_str)
        b = int(b)
        if a == b:
            continue
        canon = _canonical_pair(a, b)
        if canon not in seen:
            seen.add(canon)
            pairs.append(canon)
    return pairs


def crossover(parent1_kernels: list, parent2_kernels: list,
              rng: random.Random) -> list:
    p1 = parent1_kernels.copy()
    p2 = parent2_kernels.copy()
    rng.shuffle(p1)
    rng.shuffle(p2)
    n1 = max(1, len(p1) // 2)
    n2 = max(1, len(p2) // 2)
    return p1[:n1] + p2[:n2]


def mutate(kernels: list, rng: random.Random, probability: float = 0.15) -> list:
    if rng.random() >= probability:
        return kernels
    kernels = kernels.copy()
    choice = rng.choice(["add", "delete", "flip"])
    if choice == "add":
        for _ in range(1000):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            if a != b:
                kernels.append((a, b))
                break
    elif choice == "delete":
        if len(kernels) > 1:
            kernels.pop(rng.randrange(len(kernels)))
    else:
        if kernels:
            idx = rng.randrange(len(kernels))
            a, b = kernels[idx]
            if rng.random() < 0.5:
                a = max(1, (a ^ (1 << rng.randrange(7))) & 127)
            else:
                b = max(1, (b ^ (1 << rng.randrange(7))) & 127)
            kernels[idx] = (a, b)
    return kernels


def _dedup_kernels(kernels: list) -> list:
    seen = set()
    result = []
    for a, b in kernels:
        if a == b:
            continue
        canon = _canonical_pair(a, b)
        if canon not in seen:
            seen.add(canon)
            result.append((a, b))
    return result


def breed_child(parent1: list, parent2: list,
                rng: random.Random) -> tuple[dict, list] | None:
    for _ in range(MAX_BREED_ATTEMPTS):
        child_kernels = crossover(parent1, parent2, rng)
        child_kernels = mutate(child_kernels, rng)
        child_kernels = _dedup_kernels(child_kernels)
        if not child_kernels:
            continue
        if not is_nonconserving(child_kernels):
            continue
        rule = try_build_rule(child_kernels)
        if rule is not None:
            return rule, child_kernels
    return None


# ── Simulation & composite fitness ────────────────────────────────────────────

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

    com_t1 = None
    com_t2 = None
    final_bit_count = 0

    for t in range(1, STEPS + 1):
        grid = _step_grid(grid, lut)
        if t == COM_T1:
            com_t1 = _center_of_mass(grid)
        if t == COM_T2:
            com_t2 = _center_of_mass(grid)
            final_bit_count = int(grid.sum())

    dx = com_t2[0] - com_t1[0]
    dy = com_t2[1] - com_t1[1]
    late_displacement = math.sqrt(dx * dx + dy * dy)
    composite_fitness = late_displacement / (1.0 + final_bit_count)

    return {
        "composite_fitness":  composite_fitness,
        "late_displacement":  late_displacement,
        "final_bit_count":    final_bit_count,
    }


def evaluate_worker(args: tuple) -> dict:
    rule_id, rule_dict = args
    result = evaluate_rule(rule_dict)
    return {"rule_id": rule_id, "rule_dict": rule_dict, **result}


# ── Main ──────────────────────────────────────────────────────────────────────

def run_gen1() -> list[dict]:
    """Generate and evaluate Gen-1, saving to iter_159/results/population/."""
    GEN1_POP_DIR.mkdir(parents=True, exist_ok=True)

    existing = sorted(GEN1_POP_DIR.glob("rule_*.json"))
    if len(existing) == POPULATION_SIZE:
        print(f"[gen1] Found {POPULATION_SIZE} existing files in {GEN1_POP_DIR}, loading ...")
        population = []
        for path in existing:
            with open(path) as f:
                entry = json.load(f)
            population.append(entry)
        population.sort(key=lambda e: e["composite_fitness"], reverse=True)
        return population

    print(f"=== Step 1: Generating {POPULATION_SIZE} Gen-1 random rules ===")
    rng = random.Random(GEN1_RULE_SEED)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict, _ = generate_random_rule(rng)
        rules.append((f"rule_{i:03d}", rule_dict))
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE}")

    print(f"\n=== Step 2: Evaluating Gen-1 ({STEPS} steps, {GRID_SIZE}x{GRID_SIZE} grid) ===")
    population = []
    workers = min(4, POPULATION_SIZE)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(evaluate_worker, r): r[0] for r in rules}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            print(f"  [{done:3d}/{POPULATION_SIZE}] {result['rule_id']}: "
                  f"fitness={result['composite_fitness']:.8f}  "
                  f"bits={result['final_bit_count']:5d}  "
                  f"disp={result['late_displacement']:.4f}")

    for entry in population:
        path = GEN1_POP_DIR / f"{entry['rule_id']}.json"
        payload = {
            "rule_id":           entry["rule_id"],
            "rule":              {str(k): v for k, v in entry["rule_dict"].items()},
            "composite_fitness": round(entry["composite_fitness"], 10),
            "late_displacement": round(entry["late_displacement"], 8),
            "final_bit_count":   entry["final_bit_count"],
            "generation":        1,
        }
        with open(path, "w") as f:
            json.dump(payload, f, sort_keys=True, indent=2)

    print(f"\n  Saved {POPULATION_SIZE} Gen-1 files to {GEN1_POP_DIR}")
    population.sort(key=lambda e: e["composite_fitness"], reverse=True)
    return population


def run_gen2(gen1_population: list[dict]) -> list[dict]:
    """Breed and evaluate Gen-2, saving to iter_163/results/population/."""
    GEN2_POP_DIR.mkdir(parents=True, exist_ok=True)
    GEN2_RESULTS.mkdir(parents=True, exist_ok=True)

    elites = gen1_population[:ELITE_SIZE]

    print(f"\n=== Step 3: Gen-1 top {ELITE_SIZE} elites ===")
    for i, e in enumerate(elites):
        print(f"  #{i+1:2d}  {e['rule_id']}: fitness={e['composite_fitness']:.8f}  "
              f"bits={e['final_bit_count']:5d}")

    elite_with_pairs = []
    for e in elites:
        pairs = extract_kernel_pairs(e["rule_dict"])
        elite_with_pairs.append({**e, "pairs": pairs})

    print(f"\n=== Step 4: Breeding Gen-2 ({POPULATION_SIZE} rules) ===")
    rng = random.Random(163)
    rules_gen2 = []

    for rank, elite in enumerate(elite_with_pairs[:ELITE_CARRY]):
        rule_num = rank + 1
        rules_gen2.append((f"rule_{rule_num:03d}", elite["rule_dict"]))
        print(f"  [elite] rule_{rule_num:03d} <- {elite['rule_id']} "
              f"(fitness={elite['composite_fitness']:.8f})")

    bred = 0
    failed = 0
    rule_num = ELITE_CARRY + 1
    while bred < POPULATION_SIZE - ELITE_CARRY:
        p1, p2 = rng.sample(elite_with_pairs, 2)
        result = breed_child(p1["pairs"], p2["pairs"], rng)
        if result is None:
            failed += 1
            continue
        rule_dict, _ = result
        rules_gen2.append((f"rule_{rule_num:03d}", rule_dict))
        bred += 1
        rule_num += 1
        if bred % 10 == 0:
            print(f"  Bred {bred}/{POPULATION_SIZE - ELITE_CARRY} ...")

    print(f"  Failed breed attempts: {failed}")

    print(f"\n=== Step 5: Evaluating Gen-2 ({STEPS} steps, {GRID_SIZE}x{GRID_SIZE} grid) ===")
    population = []
    workers = min(4, POPULATION_SIZE)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(evaluate_worker, r): r[0] for r in rules_gen2}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            population.append(result)
            done += 1
            print(f"  [{done:3d}/{POPULATION_SIZE}] {result['rule_id']}: "
                  f"fitness={result['composite_fitness']:.8f}  "
                  f"bits={result['final_bit_count']:5d}  "
                  f"disp={result['late_displacement']:.4f}")

    for entry in population:
        path = GEN2_POP_DIR / f"{entry['rule_id']}.json"
        payload = {
            "rule_id":           entry["rule_id"],
            "rule":              {str(k): v for k, v in entry["rule_dict"].items()},
            "composite_fitness": round(entry["composite_fitness"], 10),
            "late_displacement": round(entry["late_displacement"], 8),
            "final_bit_count":   entry["final_bit_count"],
            "generation":        2,
        }
        with open(path, "w") as f:
            json.dump(payload, f, sort_keys=True, indent=2)

    print(f"\n  Saved {POPULATION_SIZE} Gen-2 files to {GEN2_POP_DIR}")
    population.sort(key=lambda e: e["composite_fitness"], reverse=True)
    return population


def main() -> int:
    gen1 = run_gen1()

    gen1_scores = [e["composite_fitness"] for e in gen1]
    gen1_mean    = float(np.mean(gen1_scores))
    gen1_champion = gen1_scores[0]

    print(f"\n  Gen-1 mean fitness:     {gen1_mean:.8f}")
    print(f"  Gen-1 champion fitness: {gen1_champion:.8f}")
    print(f"  Gen-1 champion rule:    {gen1[0]['rule_id']}")

    gen2 = run_gen2(gen1)

    gen2_scores = [e["composite_fitness"] for e in gen2]
    gen2_mean    = float(np.mean(gen2_scores))
    gen2_champion = gen2_scores[0]

    improvement_pct = (gen2_mean - gen1_mean) / (gen1_mean + 1e-12) * 100.0

    print(f"\n=== Summary ===")
    print(f"  gen1_mean_fitness:      {gen1_mean:.8f}")
    print(f"  gen2_mean_fitness:      {gen2_mean:.8f}")
    print(f"  gen1_champion_fitness:  {gen1_champion:.8f}  ({gen1[0]['rule_id']})")
    print(f"  gen2_champion_fitness:  {gen2_champion:.8f}  ({gen2[0]['rule_id']})")
    print(f"  fitness_improvement_pct: {improvement_pct:+.2f}%")

    summary = {
        "gen1_mean_fitness":       round(gen1_mean,    10),
        "gen2_mean_fitness":       round(gen2_mean,    10),
        "gen1_champion_fitness":   round(gen1_champion, 10),
        "gen2_champion_fitness":   round(gen2_champion, 10),
        "fitness_improvement_pct": round(improvement_pct, 4),
        "gen1_champion_rule_id":   gen1[0]["rule_id"],
        "gen2_champion_rule_id":   gen2[0]["rule_id"],
        "gen1_champion_bits":      gen1[0]["final_bit_count"],
        "gen2_champion_bits":      gen2[0]["final_bit_count"],
        "gen1_champion_disp":      round(gen1[0]["late_displacement"], 8),
        "gen2_champion_disp":      round(gen2[0]["late_displacement"], 8),
    }

    summary_path = GEN2_RESULTS / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Saved: {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
