#!/usr/bin/env python3
"""
breed_next_generation.py

Generation 2 of the evolutionary algorithm:
- Load Gen-1 elites from iter_083/elites/
- Extract kernel pairs from each elite rule
- Apply crossover + mutation to breed 100 Gen-2 rules
- Evaluate fitness (same metric as iter_082/083)
- Report comparison with Gen-1 mean fitness

Fitness = mean(bit_count_last_100_steps) * stddev(bit_count_all_steps)
"""

import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
ELITES_DIR   = PROJECT_ROOT / "archive" / "iter_083" / "elites"
ELITES_CSV   = PROJECT_ROOT / "archive" / "iter_083" / "results" / "fitness_scores.csv"
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_084" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_084" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_084" / "result.yaml"

POPULATION_SIZE = 100
ELITE_CARRY = 2
GRID_SIZE = 100
STEPS = 500
MAX_BREED_ATTEMPTS = 200
GEN1_MEAN = 226850.54

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


# --- Rule building helpers (identical to evolve_rules.py) ---

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
    """Build C6-symmetric involution rule from kernel pairs. Returns None on conflict."""
    rule = {}
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


# --- Kernel pair extraction ---

def _canonical_pair(a: int, b: int) -> tuple:
    """Canonical form of a bidirectional pair under C6 rotation."""
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
    """Extract canonical kernel pairs from a rule dict (inverse of try_build_rule)."""
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


# --- Genetic operators ---

def crossover(parent1_kernels: list, parent2_kernels: list,
              rng: random.Random) -> list:
    """Create child kernel set: random half from each parent."""
    p1 = parent1_kernels.copy()
    p2 = parent2_kernels.copy()
    rng.shuffle(p1)
    rng.shuffle(p2)
    n1 = max(1, len(p1) // 2)
    n2 = max(1, len(p2) // 2)
    return p1[:n1] + p2[:n2]


def mutate(kernels: list, rng: random.Random, probability: float = 0.1) -> list:
    """With given probability, apply one random mutation to the kernel set."""
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

    else:  # flip
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
    """Remove duplicate kernel pairs (same canonical form)."""
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
    """Try to breed a valid child rule. Returns (rule_dict, kernel_pairs) or None."""
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


# --- Simulation & fitness (identical to evolve_rules.py) ---

def load_rule_array(rule_dict: dict) -> np.ndarray:
    rule = np.arange(128, dtype=np.int32)
    for k, v in rule_dict.items():
        rule[int(k)] = int(v)
    return rule


def step_ca(grid: np.ndarray, rule: np.ndarray) -> np.ndarray:
    state = grid.astype(np.int32) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        neighbor = np.roll(np.roll(grid, -dq, axis=0), -dr, axis=1)
        state |= neighbor.astype(np.int32) << (5 - i)
    return ((rule[state] >> 6) & 1).astype(np.int8)


def evaluate_rule(rule_dict: dict, rng: np.random.Generator) -> dict:
    rule = load_rule_array(rule_dict)
    grid = rng.integers(0, 2, (GRID_SIZE, GRID_SIZE), dtype=np.int8)

    bit_counts = np.empty(STEPS + 1, dtype=np.int32)
    bit_counts[0] = int(grid.sum())
    for t in range(1, STEPS + 1):
        grid = step_ca(grid, rule)
        bit_counts[t] = int(grid.sum())

    last_100 = bit_counts[-100:]
    mean_last = float(np.mean(last_100))
    std_all   = float(np.std(bit_counts))
    fitness   = mean_last * std_all if std_all > 0 else 0.0

    return {
        "fitness": fitness,
        "final_bit_count": int(bit_counts[-1]),
        "mean_bit_count": float(np.mean(bit_counts)),
        "stddev_bit_count": std_all,
    }


# --- Main ---

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load Gen-1 elite fitness scores for ordering
    elite_fitness: dict[str, float] = {}
    with open(ELITES_CSV) as f:
        for row in csv.DictReader(f):
            elite_fitness[row["rule_id"]] = float(row["fitness_score"])

    # Load elite rule files and extract kernel pairs
    print("Loading Gen-1 elites from iter_083/elites/ ...")
    elites = []
    for path in sorted(ELITES_DIR.glob("rule_*.json")):
        with open(path) as f:
            rule_dict = json.load(f)
        rule_id = path.stem
        fitness = elite_fitness.get(rule_id, 0.0)
        pairs = extract_kernel_pairs(rule_dict)
        elites.append({
            "rule_id": rule_id,
            "rule_dict": rule_dict,
            "pairs": pairs,
            "fitness": fitness,
            "path": path,
        })

    elites.sort(key=lambda e: e["fitness"], reverse=True)
    print(f"Loaded {len(elites)} elites:")
    for e in elites:
        print(f"  {e['rule_id']}: fitness={e['fitness']:,.1f}  kernels={len(e['pairs'])}")

    rng = random.Random(84)
    sim_rng = np.random.default_rng(84)

    # --- Build Gen-2 population ---
    print(f"\nBuilding Gen-2 population ({POPULATION_SIZE} rules) ...")

    rules: list[tuple[int, dict]] = []

    # Elitism: carry top-2 directly
    for rank, elite in enumerate(elites[:ELITE_CARRY]):
        rule_id_num = rank + 1
        rule_path = POPULATION_DIR / f"rule_{rule_id_num:03d}.json"
        rule_str = {str(k): v for k, v in elite["rule_dict"].items()}
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        rules.append((rule_id_num, elite["rule_dict"]))
        print(f"  [elite] rule_{rule_id_num:03d} from {elite['rule_id']} "
              f"(fitness={elite['fitness']:,.1f})")

    # Breed remaining 98 children
    bred = 0
    rule_id_num = ELITE_CARRY + 1
    failed_breeds = 0
    while bred < (POPULATION_SIZE - ELITE_CARRY):
        p1, p2 = rng.sample(elites, 2)
        result = breed_child(p1["pairs"], p2["pairs"], rng)
        if result is None:
            failed_breeds += 1
            continue

        rule_dict, _ = result
        rule_path = POPULATION_DIR / f"rule_{rule_id_num:03d}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        rules.append((rule_id_num, rule_dict))

        bred += 1
        rule_id_num += 1
        if bred % 10 == 0:
            print(f"  Bred {bred}/{POPULATION_SIZE - ELITE_CARRY} children ...")

    print(f"  (failed breed attempts: {failed_breeds})")

    # --- Evaluate Gen-2 population ---
    print(f"\nEvaluating {POPULATION_SIZE} rules ({STEPS} steps on "
          f"{GRID_SIZE}x{GRID_SIZE} grid) ...")

    rows = []
    for rule_num, rule_dict in rules:
        rule_id = f"rule_{rule_num:03d}"
        m = evaluate_rule(rule_dict, sim_rng)
        print(f"  {rule_id}: fitness={m['fitness']:10.1f}  "
              f"final={m['final_bit_count']:5d}  "
              f"std={m['stddev_bit_count']:7.2f}")
        rows.append({
            "rule_id": rule_id,
            "fitness_score": round(m["fitness"], 4),
            "final_bit_count": m["final_bit_count"],
            "mean_bit_count": round(m["mean_bit_count"], 4),
            "stddev_bit_count": round(m["stddev_bit_count"], 4),
        })

    # Save CSV
    csv_path = RESULTS_DIR / "fitness_scores.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["rule_id", "fitness_score", "final_bit_count",
                        "mean_bit_count", "stddev_bit_count"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {csv_path}")

    # --- Metrics ---
    all_scores = np.array([r["fitness_score"] for r in rows])
    gen2_mean = float(np.mean(all_scores))
    gen2_top  = float(np.max(all_scores))
    pct_change = (gen2_mean - GEN1_MEAN) / GEN1_MEAN * 100.0

    print(f"\n=== Summary ===")
    print(f"  gen1_fitness_mean:    {GEN1_MEAN:,.2f}")
    print(f"  gen2_fitness_mean:    {gen2_mean:,.2f}")
    print(f"  fitness_improvement:  {pct_change:+.2f}%")
    print(f"  gen2_top_fitness:     {gen2_top:,.2f}")

    result = {
        "gen1_fitness_mean": GEN1_MEAN,
        "gen2_fitness_mean": round(gen2_mean, 4),
        "fitness_improvement": round(pct_change, 4),
        "gen2_top_fitness": round(gen2_top, 4),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved: {RESULT_YAML}")

    if gen2_mean > GEN1_MEAN:
        print(f"\nHypothesis CONFIRMED: Gen-2 mean {gen2_mean:,.2f} > Gen-1 mean {GEN1_MEAN:,.2f}")
        return 0
    else:
        print(f"\nHypothesis NOT confirmed: Gen-2 mean {gen2_mean:,.2f} <= Gen-1 mean {GEN1_MEAN:,.2f}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
