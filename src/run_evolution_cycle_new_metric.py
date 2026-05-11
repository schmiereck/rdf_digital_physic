#!/usr/bin/env python3
"""
run_evolution_cycle_new_metric.py

Full generation, selection, and breeding cycle using the stability-rewarding
fitness metric (fitness = 1 / (1 + final_bit_count) from a 4-bit T-shape seed
on a 150x150 toroidal grid over 500 steps).

Steps:
  1. Re-evaluate Gen-2 population (iter_084) under the new metric.
  2. Select top 10 new elites.
  3. Breed Gen-3 (100 rules) via elitism + crossover + mutation.
  4. Evaluate Gen-3 under the same metric.
  5. Write archive/iter_088/result.yaml with comparison metrics.
"""

import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT   = Path(__file__).parent.parent
GEN2_POP_DIR   = PROJECT_ROOT / "archive" / "iter_084" / "population"
GEN3_POP_DIR   = PROJECT_ROOT / "archive" / "iter_088" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_088" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_088" / "result.yaml"

POPULATION_SIZE  = 100
ELITE_COUNT      = 10
ELITE_CARRY      = 2
GRID_SIZE        = 150
STEPS            = 500
MUTATION_PROB    = 0.10
MAX_BREED_ATTEMPTS = 200

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


# ---------------------------------------------------------------------------
# Rule helpers (C6-symmetric involution)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Genetic operators
# ---------------------------------------------------------------------------

def crossover(p1: list, p2: list, rng: random.Random) -> list:
    a, b = p1.copy(), p2.copy()
    rng.shuffle(a)
    rng.shuffle(b)
    n1 = max(1, len(a) // 2)
    n2 = max(1, len(b) // 2)
    return a[:n1] + b[:n2]


def mutate(kernels: list, rng: random.Random) -> list:
    if rng.random() >= MUTATION_PROB:
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


def breed_child(p1: list, p2: list, rng: random.Random) -> tuple[dict, list] | None:
    for _ in range(MAX_BREED_ATTEMPTS):
        child_kernels = crossover(p1, p2, rng)
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


# ---------------------------------------------------------------------------
# Simulation & fitness
# ---------------------------------------------------------------------------

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


def make_t_shape_grid() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
    cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
    grid[cx, cy]     = 1
    grid[cx, cy - 1] = 1
    grid[cx, cy + 1] = 1
    grid[cx + 1, cy] = 1
    return grid


def evaluate_new_metric(rule_dict: dict) -> dict:
    rule = load_rule_array(rule_dict)
    grid = make_t_shape_grid()
    for _ in range(STEPS):
        grid = step_ca(grid, rule)
    final_bit_count = int(grid.sum())
    fitness = 1.0 / (1.0 + final_bit_count)
    return {"fitness": fitness, "final_bit_count": final_bit_count}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    GEN3_POP_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Re-evaluate Gen-2 population under the new metric
    # ------------------------------------------------------------------
    print("=== Step 1: Re-evaluating Gen-2 population ===")
    gen2_rules = []
    for path in sorted(GEN2_POP_DIR.glob("rule_*.json")):
        with open(path) as f:
            rule_dict = json.load(f)
        gen2_rules.append({"rule_id": path.stem, "path": path, "rule_dict": rule_dict})

    print(f"  Loaded {len(gen2_rules)} rules from {GEN2_POP_DIR}")

    gen2_rows = []
    for entry in gen2_rules:
        m = evaluate_new_metric(entry["rule_dict"])
        entry["fitness"] = m["fitness"]
        entry["final_bit_count"] = m["final_bit_count"]
        gen2_rows.append({
            "rule_id": entry["rule_id"],
            "fitness": round(m["fitness"], 8),
            "final_bit_count": m["final_bit_count"],
        })
        print(f"  {entry['rule_id']}: fitness={m['fitness']:.8f}  "
              f"final_bits={m['final_bit_count']:6d}")

    csv_path = RESULTS_DIR / "gen2_rescored.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rule_id", "fitness", "final_bit_count"])
        writer.writeheader()
        writer.writerows(gen2_rows)
    print(f"  Saved: {csv_path}")

    gen2_scores = np.array([e["fitness"] for e in gen2_rules])
    gen2_mean = float(np.mean(gen2_scores))
    gen2_chaotic = int(np.sum(gen2_scores < 0.001))
    print(f"\n  gen2_rescored_fitness_mean = {gen2_mean:.8f}")
    print(f"  gen2_chaotic_rules (fitness < 0.001) = {gen2_chaotic}")

    # ------------------------------------------------------------------
    # Step 2: Select new Gen-2 elites (top 10)
    # ------------------------------------------------------------------
    print("\n=== Step 2: Selecting top-10 Gen-2 elites ===")
    gen2_rules.sort(key=lambda e: e["fitness"], reverse=True)
    elites = gen2_rules[:ELITE_COUNT]
    for rank, e in enumerate(elites):
        print(f"  #{rank+1:2d}  {e['rule_id']}: fitness={e['fitness']:.8f}  "
              f"final_bits={e['final_bit_count']}")

    # Pre-extract kernel pairs from elites
    for e in elites:
        e["pairs"] = extract_kernel_pairs(e["rule_dict"])

    # ------------------------------------------------------------------
    # Step 3: Breed Gen-3 population
    # ------------------------------------------------------------------
    print(f"\n=== Step 3: Breeding Gen-3 population ({POPULATION_SIZE} rules) ===")
    rng = random.Random(88)

    gen3_rules = []

    # Elitism: carry top-2 directly
    for rank, elite in enumerate(elites[:ELITE_CARRY]):
        rule_id_num = rank + 1
        out_path = GEN3_POP_DIR / f"rule_{rule_id_num:03d}.json"
        rule_str = {str(k): v for k, v in elite["rule_dict"].items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        gen3_rules.append({"rule_id": f"rule_{rule_id_num:03d}",
                            "rule_dict": elite["rule_dict"]})
        print(f"  [elite] rule_{rule_id_num:03d} from {elite['rule_id']} "
              f"(fitness={elite['fitness']:.8f})")

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
        out_path = GEN3_POP_DIR / f"rule_{rule_id_num:03d}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        gen3_rules.append({"rule_id": f"rule_{rule_id_num:03d}",
                            "rule_dict": rule_dict})
        bred += 1
        rule_id_num += 1
        if bred % 10 == 0:
            print(f"  Bred {bred}/{POPULATION_SIZE - ELITE_CARRY} children ...")

    print(f"  Done. ({failed_breeds} failed breed attempts)")

    # ------------------------------------------------------------------
    # Step 4: Evaluate Gen-3 population
    # ------------------------------------------------------------------
    print(f"\n=== Step 4: Evaluating Gen-3 population ===")
    gen3_rows = []
    for entry in gen3_rules:
        m = evaluate_new_metric(entry["rule_dict"])
        entry["fitness"] = m["fitness"]
        entry["final_bit_count"] = m["final_bit_count"]
        gen3_rows.append({
            "rule_id": entry["rule_id"],
            "fitness": round(m["fitness"], 8),
            "final_bit_count": m["final_bit_count"],
        })
        print(f"  {entry['rule_id']}: fitness={m['fitness']:.8f}  "
              f"final_bits={m['final_bit_count']:6d}")

    csv_path2 = RESULTS_DIR / "gen3_fitness.csv"
    with open(csv_path2, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rule_id", "fitness", "final_bit_count"])
        writer.writeheader()
        writer.writerows(gen3_rows)
    print(f"  Saved: {csv_path2}")

    gen3_scores = np.array([e["fitness"] for e in gen3_rules])
    gen3_mean = float(np.mean(gen3_scores))
    gen3_top  = float(np.max(gen3_scores))
    gen3_chaotic = int(np.sum(gen3_scores < 0.001))

    # ------------------------------------------------------------------
    # Step 5: Report & Compare
    # ------------------------------------------------------------------
    fitness_improvement_pct = (gen3_mean - gen2_mean) / gen2_mean * 100.0 if gen2_mean > 0 else float("inf")

    print(f"\n=== Step 5: Summary ===")
    print(f"  gen2_rescored_fitness_mean = {gen2_mean:.8f}")
    print(f"  gen3_fitness_mean          = {gen3_mean:.8f}")
    print(f"  fitness_improvement_pct    = {fitness_improvement_pct:+.2f}%")
    print(f"  gen3_top_fitness           = {gen3_top:.8f}")
    print(f"  gen2_chaotic_rules         = {gen2_chaotic}")
    print(f"  gen3_chaotic_rules         = {gen3_chaotic}")

    # Success criteria
    improvement_ok = gen3_mean >= gen2_mean * 1.50
    chaotic_ok     = gen3_chaotic < gen2_chaotic / 2.0
    print(f"\n  improvement_ok (gen3_mean >= 1.5 * gen2_mean): {improvement_ok}")
    print(f"  chaotic_ok     (gen3_chaotic < gen2_chaotic/2): {chaotic_ok}")

    yaml_result = {
        "gen2_rescored_fitness_mean": round(gen2_mean, 8),
        "gen3_fitness_mean":          round(gen3_mean, 8),
        "fitness_improvement_pct":    round(fitness_improvement_pct, 4),
        "gen3_top_fitness":           round(gen3_top, 8),
        "gen2_chaotic_rules":         gen2_chaotic,
        "gen3_chaotic_rules":         gen3_chaotic,
        "improvement_ok":             bool(improvement_ok),
        "chaotic_ok":                 bool(chaotic_ok),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved: {RESULT_YAML}")

    return 0 if (improvement_ok and chaotic_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
