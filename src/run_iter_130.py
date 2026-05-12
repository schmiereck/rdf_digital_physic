#!/usr/bin/env python3
"""
run_iter_130.py

Breed Gen-2 rules from the two viable medium-density rules discovered in
iter_129 (rule_050 and rule_088).  Uses uniform crossover of generator pairs
plus per-pair mutation, then evaluates with the late-displacement fitness
metric.
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
ITER_DIR         = PROJECT_ROOT / "archive" / "iter_130"
POPULATION_DIR   = ITER_DIR / "population"
RESULTS_DIR      = ITER_DIR / "results"
RESULT_YAML      = ITER_DIR / "result.yaml"
CSV_PATH         = RESULTS_DIR / "gen2_reboot_scores.csv"

PARENT_SCORES_CSV = (
    PROJECT_ROOT / "archive" / "iter_129" / "results" / "medium_density_scores.csv"
)

POPULATION_SIZE  = 100
STEPS            = 200
LATE_START       = 100
INITIAL_BITS     = 325
INITIAL_OBJECTS  = 72
CHAOS_THRESHOLD  = 1000
N_PAIRS          = 8
MUTATION_RATE    = 0.10
GEN1_TOP_FITNESS = 0.02771506
SEED_BASE_MEDIUM = 2000      # seed_base used for medium density in iter_129
BREED_SEED       = 130
MAX_GEN_ATTEMPTS = 50000     # for fresh pair generation
MAX_BREED_RETRIES = 500      # per rule

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


# ── C2-symmetric rule helpers (identical to run_density_scan.py) ──────────────

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


def generate_c2_rule(n_pairs: int, seed: int) -> dict:
    """Deterministic C2-symmetric reversible rule with exactly n_pairs kernel pairs."""
    rng = random.Random(seed)
    for _ in range(MAX_GEN_ATTEMPTS):
        pairs: list      = []
        used_states: set = set()
        ok = True
        for _ in range(n_pairs):
            found = False
            for _ in range(2000):
                a = rng.randint(1, 127)
                b = rng.randint(1, 127)
                if not is_valid_c2_pair(a, b):
                    continue
                ra = rotate_c2(a)
                rb = rotate_c2(b)
                states = {a, b, ra, rb}
                if states & used_states:
                    continue
                pairs.append((a, b))
                used_states.update(states)
                found = True
                break
            if not found:
                ok = False
                break
        if not ok:
            continue
        if not is_nonconserving(pairs):
            continue
        rule = try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(
        f"Failed to generate C2 rule with {n_pairs} pairs after {MAX_GEN_ATTEMPTS} attempts"
    )


# ── Pair extraction ───────────────────────────────────────────────────────────

def extract_c2_generator_pairs(rule_dict: dict) -> list:
    """Recover the N_PAIRS generator pairs from a C2 rule dict."""
    seen  = set()
    pairs = []
    for a_str, b in rule_dict.items():
        a = int(a_str)
        b = int(b)
        if a == b or a in seen:
            continue
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        seen.update({a, b, ra, rb})
        pairs.append((a, b))
    return pairs


# ── Genetic operators ─────────────────────────────────────────────────────────

def _pairs_have_conflict(pairs: list) -> bool:
    """True if any two pairs share a state (would create a rule conflict)."""
    used: set = set()
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        states = {a, b, ra, rb}
        if states & used:
            return True
        used.update(states)
    return False


def generate_random_valid_pair(
    used_states: set, rng: random.Random, max_tries: int = 2000
) -> tuple | None:
    """Random valid C2 pair that is non-conserving and avoids used_states."""
    for _ in range(max_tries):
        a = rng.randint(1, 127)
        b = rng.randint(1, 127)
        if not is_valid_c2_pair(a, b):
            continue
        if bin(a).count('1') == bin(b).count('1'):
            continue
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        if {a, b, ra, rb} & used_states:
            continue
        return (a, b)
    return None


def apply_per_pair_mutation(pairs: list, rng: random.Random) -> list:
    """For each pair, independently replace it with 10% probability."""
    pairs = list(pairs)
    # Build the set of states currently in use
    used_states: set = set()
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        used_states.update({a, b, ra, rb})

    for i in range(len(pairs)):
        if rng.random() >= MUTATION_RATE:
            continue
        a_old, b_old = pairs[i]
        ra_old = rotate_c2(a_old)
        rb_old = rotate_c2(b_old)
        # Free the old pair's states so the new pair can use them
        used_states -= {a_old, b_old, ra_old, rb_old}
        new_pair = generate_random_valid_pair(used_states, rng)
        if new_pair is not None:
            pairs[i] = new_pair
            a_n, b_n = new_pair
            used_states.update({a_n, b_n, rotate_c2(a_n), rotate_c2(b_n)})
        else:
            # Mutation failed — restore old pair
            used_states.update({a_old, b_old, ra_old, rb_old})
    return pairs


def breed_rule(
    elite1_pairs: list,
    elite2_pairs: list,
    rng: random.Random,
) -> dict | None:
    """Breed one child via uniform crossover + per-pair mutation."""
    for _ in range(MAX_BREED_RETRIES):
        k = rng.randint(0, N_PAIRS)  # pairs from elite1

        p1 = list(elite1_pairs)
        p2 = list(elite2_pairs)
        rng.shuffle(p1)
        rng.shuffle(p2)
        candidate = p1[:k] + p2[:(N_PAIRS - k)]

        # Apply mutation before conflict check
        candidate = apply_per_pair_mutation(candidate, rng)

        if len(candidate) != N_PAIRS:
            continue
        if _pairs_have_conflict(candidate):
            continue
        if not is_nonconserving(candidate):
            continue

        rule = try_build_c2_rule(candidate)
        if rule is not None:
            return rule, candidate

    return None


# ── Grid simulation (identical to run_density_scan.py) ───────────────────────

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


def count_objects(grid: np.ndarray, grid_size: int) -> int:
    live     = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    count    = 0
    for start in live:
        if start in visited:
            continue
        count += 1
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % grid_size, (r + dr) % grid_size)
                if nb in live and nb not in visited:
                    stack.append(nb)
    return count


def evaluate_rule_late_displacement(
    rule_dict: dict, ash_grid: np.ndarray, grid_size: int
) -> dict:
    lut  = rule_to_lut(rule_dict)
    grid = ash_grid.copy()

    for _ in range(LATE_START):
        grid = step_grid(grid, lut)

    com_100 = center_of_mass(grid)

    for _ in range(STEPS - LATE_START):
        grid = step_grid(grid, lut)

    com_200       = center_of_mass(grid)
    final_bits    = int(grid.sum())
    final_objects = count_objects(grid, grid_size)

    dq           = com_200[0] - com_100[0]
    dr           = com_200[1] - com_100[1]
    displacement = math.sqrt(dq * dq + dr * dr)

    denom   = 1.0 + abs(final_bits - INITIAL_BITS) + abs(final_objects - INITIAL_OBJECTS)
    fitness = displacement / denom

    return {
        "fitness":           fitness,
        "late_displacement": displacement,
        "final_bits":        final_bits,
        "final_objects":     final_objects,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load ash pattern
    print("Loading ash pattern ...", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    # Identify the two viable parents from iter_129 medium_density_scores.csv
    print("\nLoading parent scores from iter_129 ...", flush=True)
    viable_rows = []
    with open(PARENT_SCORES_CSV) as f:
        for row in csv.DictReader(f):
            if row["viable"].strip().lower() == "true":
                viable_rows.append(row)

    viable_rows.sort(key=lambda r: float(r["fitness"]), reverse=True)
    elite_ids = [r["rule_id"] for r in viable_rows[:2]]
    print(f"  Elite parents: {elite_ids}", flush=True)
    for r in viable_rows[:2]:
        print(f"    {r['rule_id']}: fitness={r['fitness']}", flush=True)

    # Regenerate the elite rules using the same seeds as iter_129
    elite_rules = []
    for rule_id in elite_ids:
        idx  = int(rule_id.replace("rule_", ""))
        seed = SEED_BASE_MEDIUM + idx
        print(f"  Regenerating {rule_id} (seed={seed}) ...", flush=True)
        rule_dict = generate_c2_rule(N_PAIRS, seed)
        pairs     = extract_c2_generator_pairs(rule_dict)
        print(f"    Extracted {len(pairs)} generator pairs", flush=True)
        elite_rules.append({"rule_id": rule_id, "rule_dict": rule_dict, "pairs": pairs})

    elite1_pairs = elite_rules[0]["pairs"]
    elite2_pairs = elite_rules[1]["pairs"]

    # Breed Gen-2 population
    print(f"\nBreeding {POPULATION_SIZE} Gen-2 rules ...", flush=True)
    rng = random.Random(BREED_SEED)

    population: list[dict] = []
    failed = 0
    for i in range(POPULATION_SIZE):
        result = breed_rule(elite1_pairs, elite2_pairs, rng)
        if result is None:
            failed += 1
            print(f"  WARNING: breed failed for rule_{i:03d}, using fallback", flush=True)
            # Fallback: clone elite1 with full mutation pass
            pairs   = apply_per_pair_mutation(list(elite1_pairs), rng)
            rule_d  = try_build_c2_rule(pairs) or elite_rules[0]["rule_dict"]
        else:
            rule_d, _ = result

        rule_id = f"rule_{i:03d}"
        population.append({"rule_id": rule_id, "rule_dict": rule_d})

        # Save to population dir
        rule_path = POPULATION_DIR / f"{rule_id}.json"
        rule_str  = {str(k): v for k, v in rule_d.items()}
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)

        if (i + 1) % 10 == 0:
            print(f"  Bred {i+1}/{POPULATION_SIZE}", flush=True)

    print(f"  Breed failures: {failed}", flush=True)

    # Evaluate all Gen-2 rules
    print(f"\nEvaluating {POPULATION_SIZE} rules ({STEPS} steps) ...", flush=True)
    rows = []
    for entry in population:
        rule_id   = entry["rule_id"]
        rule_dict = entry["rule_dict"]
        res       = evaluate_rule_late_displacement(rule_dict, ash_grid, grid_size)

        is_chaotic = res["final_bits"] >= CHAOS_THRESHOLD
        is_viable  = res["fitness"] > 0.0 and not is_chaotic

        rows.append({
            "rule_id":           rule_id,
            "fitness":           round(res["fitness"], 8),
            "late_displacement": round(res["late_displacement"], 6),
            "final_bits":        res["final_bits"],
            "final_objects":     res["final_objects"],
            "chaotic":           is_chaotic,
            "viable":            is_viable,
        })

    fitnesses = [r["fitness"] for r in rows]
    gen2_top  = max(fitnesses)
    gen2_mean = float(np.mean(fitnesses))
    viable_count  = sum(1 for r in rows if r["viable"])
    chaotic_count = sum(1 for r in rows if r["chaotic"])
    beating_gen1  = sum(1 for f in fitnesses if f > GEN1_TOP_FITNESS)
    improvement_pct = (gen2_top - GEN1_TOP_FITNESS) / GEN1_TOP_FITNESS * 100.0

    # Print progress at end
    for r in rows:
        print(
            f"  {r['rule_id']}: fitness={r['fitness']:.8f}  "
            f"bits={r['final_bits']}  viable={r['viable']}",
            flush=True,
        )

    # Save CSV
    fieldnames = ["rule_id", "fitness", "late_displacement",
                  "final_bits", "final_objects", "chaotic", "viable"]
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {CSV_PATH}", flush=True)

    # Save result.yaml
    result = {
        "gen1_top_fitness":      GEN1_TOP_FITNESS,
        "gen2_top_fitness":      round(float(gen2_top), 8),
        "gen2_mean_fitness":     round(float(gen2_mean), 8),
        "rules_beating_gen1_top": int(beating_gen1),
        "fitness_improvement_pct": round(float(improvement_pct), 4),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}", flush=True)

    print("\n=== Gen-2 Summary ===", flush=True)
    print(f"  gen1_top_fitness:        {GEN1_TOP_FITNESS:.8f}", flush=True)
    print(f"  gen2_top_fitness:        {gen2_top:.8f}", flush=True)
    print(f"  gen2_mean_fitness:       {gen2_mean:.8f}", flush=True)
    print(f"  viable_rules:            {viable_count}", flush=True)
    print(f"  chaotic_rules:           {chaotic_count}", flush=True)
    print(f"  rules_beating_gen1_top:  {beating_gen1}", flush=True)
    print(f"  fitness_improvement_pct: {improvement_pct:+.4f}%", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
