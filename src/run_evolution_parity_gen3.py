#!/usr/bin/env python3
"""
run_evolution_parity_gen3.py

Breeds a Gen-3 population from the 5 elite Gen-2 parity-conserving rules.
Elite parents: Gen-2 rules with fitness > Gen-1 top (0.36059001).

Breeding pool: 5 elite parents × 20 copies = 100 entries.
Each child: random one-point crossover on 8 kernel pairs, 10% mutation chance.

Fitness metric: identical to iter_138/iter_139
  initial state : ash_pattern.json (150x150, 325 bits)
  simulation    : 200 steps with wrapping
  displacement  : COM distance between step 100 and step 200
  bit_ratio     : final_bits / 325
  fitness       : displacement / (1 + (bit_ratio - 1)**2)
"""

import csv
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT     = Path(__file__).parent.parent
ASH_PATTERN_PATH = Path(__file__).parent / "ash_pattern.json"
GEN2_RESULTS_CSV = PROJECT_ROOT / "archive" / "iter_139" / "results" / "gen2_scores.csv"
GEN2_POP_DIR     = PROJECT_ROOT / "archive" / "iter_139" / "population"
ITER_DIR         = PROJECT_ROOT / "archive" / "iter_140"
POPULATION_DIR   = ITER_DIR / "population"
RESULTS_DIR      = ITER_DIR / "results"
CSV_PATH         = RESULTS_DIR / "results.csv"
SUMMARY_YAML     = RESULTS_DIR / "summary.yaml"

POPULATION_SIZE   = 100
STEPS             = 200
LATE_START        = 100
INITIAL_BITS      = 325
N_PAIRS           = 8
ELITE_POOL_COPIES = 20
MUTATION_RATE     = 0.10
GEN1_TOP_FITNESS  = 0.36059001
GEN2_TOP_FITNESS  = 0.73077873
BREED_SEED        = 140
MAX_BREED_RETRIES = 500
MAX_PAIR_TRIES    = 4000


# ── C2-symmetric rule helpers ─────────────────────────────────────────────────

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def is_valid_c2_pair(a: int, b: int) -> bool:
    if a == b or a == 0 or b == 0:
        return False
    ra = rotate_c2(a)
    rb = rotate_c2(b)
    return len({a, b, ra, rb}) == 4


def is_parity_conserving_pair(a: int, b: int) -> bool:
    return bin(a).count('1') % 2 == bin(b).count('1') % 2


def is_nonconserving(pairs: list) -> bool:
    return any(bin(a).count('1') != bin(b).count('1') for a, b in pairs)


def try_build_c2_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        for src, dst in [(a, b), (b, a), (ra, rb), (rb, ra)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def _pairs_have_conflict(pairs: list) -> bool:
    used: set = set()
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        states = {a, b, ra, rb}
        if states & used:
            return True
        used.update(states)
    return False


def extract_c2_generator_pairs(rule_dict: dict) -> list:
    seen  = set()
    pairs = []
    for a, b in rule_dict.items():
        if a == b or a in seen:
            continue
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        seen.update({a, b, ra, rb})
        pairs.append((a, b))
    return pairs


# ── Genetic operators ─────────────────────────────────────────────────────────

def one_point_crossover(p1_pairs: list, p2_pairs: list, rng: random.Random) -> list:
    p1 = list(p1_pairs)
    p2 = list(p2_pairs)
    rng.shuffle(p1)
    rng.shuffle(p2)
    cut = rng.randint(1, N_PAIRS - 1)
    return p1[:cut] + p2[cut:]


def generate_random_parity_conserving_pair(
    used_states: set, rng: random.Random, max_tries: int = MAX_PAIR_TRIES
) -> tuple | None:
    for _ in range(max_tries):
        a = rng.randint(1, 127)
        b = rng.randint(1, 127)
        if not is_valid_c2_pair(a, b):
            continue
        if not is_parity_conserving_pair(a, b):
            continue
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        if {a, b, ra, rb} & used_states:
            continue
        return (a, b)
    return None


def mutate(pairs: list, rng: random.Random) -> list:
    pairs = list(pairs)
    idx   = rng.randrange(len(pairs))
    used: set = set()
    for i, (a, b) in enumerate(pairs):
        if i == idx:
            continue
        used.update({a, b, rotate_c2(a), rotate_c2(b)})
    new_pair = generate_random_parity_conserving_pair(used, rng)
    if new_pair is not None:
        pairs[idx] = new_pair
    return pairs


def breed_child(
    p1_pairs: list, p2_pairs: list, rng: random.Random, do_mutate: bool
) -> dict | None:
    for _ in range(MAX_BREED_RETRIES):
        candidate = one_point_crossover(p1_pairs, p2_pairs, rng)
        if do_mutate:
            candidate = mutate(candidate, rng)
        if len(candidate) != N_PAIRS:
            continue
        if _pairs_have_conflict(candidate):
            continue
        if not is_nonconserving(candidate):
            continue
        rule = try_build_c2_rule(candidate)
        if rule is not None:
            return rule
    return None


# ── Grid simulation ───────────────────────────────────────────────────────────

def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lookup: np.ndarray) -> np.ndarray:
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
    return lookup[state]


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def evaluate_rule(rule_dict: dict, ash_grid: np.ndarray) -> dict:
    lut  = rule_to_lut(rule_dict)
    grid = ash_grid.copy()

    for _ in range(LATE_START):
        grid = step_grid(grid, lut)

    com_100 = center_of_mass(grid)

    for _ in range(STEPS - LATE_START):
        grid = step_grid(grid, lut)

    com_200    = center_of_mass(grid)
    final_bits = int(grid.sum())

    dq           = com_200[0] - com_100[0]
    dr           = com_200[1] - com_100[1]
    displacement = math.sqrt(dq * dq + dr * dr)
    bit_ratio    = final_bits / INITIAL_BITS
    fitness      = displacement / (1.0 + (bit_ratio - 1.0) ** 2)

    return {
        "displacement": displacement,
        "final_bits":   final_bits,
        "bit_ratio":    bit_ratio,
        "fitness":      fitness,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load ash pattern ──────────────────────────────────────────────────────
    print("Loading ash pattern ...", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    # ── Identify 5 elite Gen-2 parents ────────────────────────────────────────
    csv_path = GEN2_RESULTS_CSV
    if not csv_path.exists():
        csv_path = csv_path.parent / "results.csv"
    print(f"\nLoading Gen-2 scores from {csv_path} ...", flush=True)
    gen2_rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            gen2_rows.append({
                "rule_id": row["rule_id"],
                "fitness": float(row["fitness"]),
            })

    elite_rows = sorted(
        [r for r in gen2_rows if r["fitness"] > GEN1_TOP_FITNESS],
        key=lambda r: r["fitness"],
        reverse=True,
    )
    print(f"  Found {len(elite_rows)} elite Gen-2 rules (fitness > {GEN1_TOP_FITNESS})", flush=True)
    for r in elite_rows:
        print(f"    {r['rule_id']}: fitness={r['fitness']:.8f}", flush=True)

    # ── Load elite parent kernel pairs ────────────────────────────────────────
    print("\nLoading elite parent rules ...", flush=True)
    elite_parents = []
    for r in elite_rows:
        path = GEN2_POP_DIR / f"{r['rule_id']}.json"
        with open(path) as f:
            rule_dict = {int(k): int(v) for k, v in json.load(f).items()}
        pairs = extract_c2_generator_pairs(rule_dict)
        elite_parents.append({
            "rule_id":   r["rule_id"],
            "fitness":   r["fitness"],
            "rule_dict": rule_dict,
            "pairs":     pairs,
        })
        print(f"  {r['rule_id']}: {len(pairs)} generator pairs", flush=True)

    # ── Build breeding pool: 20 copies of each elite parent ───────────────────
    breeding_pool = []
    for parent in elite_parents:
        breeding_pool.extend([parent] * ELITE_POOL_COPIES)
    print(
        f"\nBreeding pool: {len(breeding_pool)} entries "
        f"({len(elite_parents)} parents × {ELITE_POOL_COPIES} copies)",
        flush=True,
    )

    # ── Breed Gen-3 population ────────────────────────────────────────────────
    rng = random.Random(BREED_SEED)
    print(
        f"Breeding {POPULATION_SIZE} Gen-3 rules "
        f"(one-point crossover, mutation_rate={MUTATION_RATE:.0%}) ...",
        flush=True,
    )

    population = []
    failed     = 0
    for i in range(POPULATION_SIZE):
        rule_id   = f"rule_{i:03d}"
        pa        = rng.choice(breeding_pool)
        pb        = rng.choice(breeding_pool)
        do_mutate = rng.random() < MUTATION_RATE

        rule_d = breed_child(pa["pairs"], pb["pairs"], rng, do_mutate)
        if rule_d is None:
            failed += 1
            print(
                f"  WARNING: breed failed for {rule_id} "
                f"({pa['rule_id']}x{pb['rule_id']}), cloning {pa['rule_id']}",
                flush=True,
            )
            rule_d = pa["rule_dict"]

        population.append({
            "rule_id":   rule_id,
            "rule_dict": rule_d,
            "parents":   f"{pa['rule_id']}x{pb['rule_id']}",
            "mutated":   do_mutate,
        })

        rule_str  = {str(k): v for k, v in rule_d.items()}
        rule_path = POPULATION_DIR / f"{rule_id}.json"
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True)

        if (i + 1) % 10 == 0:
            print(f"  Bred {i+1}/{POPULATION_SIZE}", flush=True)

    print(f"  Breed failures: {failed}", flush=True)

    # ── Evaluate Gen-3 population ─────────────────────────────────────────────
    print(f"\nEvaluating {POPULATION_SIZE} Gen-3 rules ({STEPS} steps) ...", flush=True)
    rows = []
    for entry in population:
        rule_id   = entry["rule_id"]
        rule_dict = entry["rule_dict"]
        res       = evaluate_rule(rule_dict, ash_grid)

        rows.append({
            "rule_id":              rule_id,
            "fitness":              round(res["fitness"], 8),
            "bit_ratio":            round(res["bit_ratio"], 6),
            "displacement_100_200": round(res["displacement"], 6),
        })

        if len(rows) % 10 == 0:
            r = rows[-1]
            print(
                f"  [{len(rows):3d}/{POPULATION_SIZE}] {r['rule_id']}: "
                f"fitness={r['fitness']:.6f}  disp={r['displacement_100_200']:.4f}  "
                f"bit_ratio={r['bit_ratio']:.3f}",
                flush=True,
            )

    # ── Summary statistics ────────────────────────────────────────────────────
    fitnesses  = [r["fitness"]   for r in rows]
    bit_ratios = [r["bit_ratio"] for r in rows]

    gen3_top           = float(np.max(fitnesses))
    gen3_mean          = float(np.mean(fitnesses))
    rules_beating_gen2 = sum(1 for f in fitnesses if f > GEN2_TOP_FITNESS)
    viable_rules       = sum(1 for r in rows if r["fitness"] > 0.01 and r["bit_ratio"] < 3.0)
    chaotic_rules      = sum(1 for r in rows if r["bit_ratio"] >= 3.0)
    dead_rules         = sum(1 for r in rows if r["fitness"] <= 0.01)

    print("\n=== Gen-2 vs Gen-3 Summary ===", flush=True)
    print(f"  gen2_top_fitness:        {GEN2_TOP_FITNESS:.8f}", flush=True)
    print(f"  gen3_top_fitness:        {gen3_top:.8f}", flush=True)
    print(f"  gen3_mean_fitness:       {gen3_mean:.8f}", flush=True)
    print(f"  rules_beating_gen2_top:  {rules_beating_gen2}", flush=True)
    print(f"  viable_rules:            {viable_rules}", flush=True)
    print(f"  chaotic_rules:           {chaotic_rules}", flush=True)
    print(f"  dead_rules:              {dead_rules}", flush=True)
    print(f"  breed_failures:          {failed}", flush=True)

    # ── Save CSV ──────────────────────────────────────────────────────────────
    fieldnames = ["rule_id", "fitness", "bit_ratio", "displacement_100_200"]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {CSV_PATH}", flush=True)

    # ── Save summary.yaml ─────────────────────────────────────────────────────
    summary = {
        "gen2_top_fitness":       GEN2_TOP_FITNESS,
        "gen3_top_fitness":       round(gen3_top, 8),
        "gen3_mean_fitness":      round(gen3_mean, 8),
        "rules_beating_gen2_top": int(rules_beating_gen2),
        "viable_rules":           int(viable_rules),
        "chaotic_rules":          int(chaotic_rules),
        "dead_rules":             int(dead_rules),
    }
    with open(SUMMARY_YAML, "w") as f:
        yaml.dump(summary, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {SUMMARY_YAML}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
