#!/usr/bin/env python3
"""
evolve_reboot_gen3.py

Breed and evaluate a third generation of C2-symmetric rules.
- Parents: top-5 elites from Gen-2 (iter_130)
- Crossover: 4 kernel-pairs from parent-A + 4 from parent-B
- Mutation: exactly 10 of 100 child rules get one pair replaced at random
- Fitness: late-displacement metric (steps 100-200), formula:
      displacement / (1 + final_bit_count / initial_bit_count)
  Rules are chaotic (bits > 1000) or dead (bits < 20) → fitness = 0
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
ITER_DIR         = PROJECT_ROOT / "archive" / "iter_131"
POPULATION_DIR   = ITER_DIR / "population"
RESULTS_DIR      = ITER_DIR / "results"
RESULT_YAML      = ITER_DIR / "result.yaml"
GEN3_CSV         = RESULTS_DIR / "reboot_gen3_scores.csv"

GEN2_ITER_DIR    = PROJECT_ROOT / "archive" / "iter_130"
GEN2_POP_DIR     = GEN2_ITER_DIR / "population"
# iter_130 may save under either name
_GEN2_CSV_A      = GEN2_ITER_DIR / "results" / "reboot_gen2_scores.csv"
_GEN2_CSV_B      = GEN2_ITER_DIR / "results" / "gen2_reboot_scores.csv"

POPULATION_SIZE  = 100
STEPS            = 200
LATE_START       = 100
CHAOS_THRESHOLD  = 1000
DEAD_THRESHOLD   = 20
N_PAIRS          = 8
N_ELITES         = 5
N_MUTATIONS      = 10   # exactly 10 of 100 rules get one pair replaced
BREED_SEED       = 131
MAX_PAIR_TRIES   = 4000
MAX_BREED_RETRIES = 500

HEX_DIRS = [
    ( 1,  0), ( 1, -1), ( 0, -1),
    (-1,  0), (-1,  1), ( 0,  1),
]


# ── C2 helpers (same as iter_130) ─────────────────────────────────────────────

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


def generate_random_valid_pair(
    used_states: set, rng: random.Random, max_tries: int = MAX_PAIR_TRIES
) -> tuple | None:
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


# ── Genetic operators ─────────────────────────────────────────────────────────

def crossover_4_4(p1_pairs: list, p2_pairs: list, rng: random.Random) -> list:
    """Return 4 pairs from p1 + 4 pairs from p2 (shuffled before slicing)."""
    p1 = list(p1_pairs)
    p2 = list(p2_pairs)
    rng.shuffle(p1)
    rng.shuffle(p2)
    return p1[:4] + p2[:4]


def mutate_one_pair(pairs: list, rng: random.Random) -> list:
    """Replace exactly one randomly selected pair with a fresh valid pair."""
    pairs = list(pairs)
    idx   = rng.randrange(len(pairs))
    a_old, b_old = pairs[idx]
    ra_old = rotate_c2(a_old)
    rb_old = rotate_c2(b_old)

    used: set = set()
    for i, (a, b) in enumerate(pairs):
        if i == idx:
            continue
        used.update({a, b, rotate_c2(a), rotate_c2(b)})

    new_pair = generate_random_valid_pair(used, rng)
    if new_pair is not None:
        pairs[idx] = new_pair
    return pairs


def breed_child(
    p1_pairs: list, p2_pairs: list, rng: random.Random, mutate: bool
) -> dict | None:
    """Crossover + optional single-pair mutation; retry until valid or give up."""
    for _ in range(MAX_BREED_RETRIES):
        candidate = crossover_4_4(p1_pairs, p2_pairs, rng)

        if mutate:
            candidate = mutate_one_pair(candidate, rng)

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


# ── Simulation ────────────────────────────────────────────────────────────────

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


def evaluate_late_displacement(
    rule_dict: dict, ash_grid: np.ndarray, grid_size: int, initial_bits: int
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

    is_chaotic = final_bits > CHAOS_THRESHOLD
    is_dead    = final_bits < DEAD_THRESHOLD

    if is_chaotic or is_dead:
        fitness = 0.0
    else:
        fitness = displacement / (1.0 + final_bits / initial_bits)

    return {
        "fitness":              fitness,
        "displacement_100_200": displacement,
        "final_bits":           final_bits,
        "final_objects":        final_objects,
        "is_chaotic":           is_chaotic,
        "is_dead":              is_dead,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load ash pattern
    print("Loading ash pattern ...", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size    = ash_data["grid_size"]
    initial_bits = ash_data["bit_count"]
    ash_grid     = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {initial_bits} bits on {grid_size}x{grid_size} grid", flush=True)

    # Load Gen-2 scores
    gen2_csv = _GEN2_CSV_A if _GEN2_CSV_A.exists() else _GEN2_CSV_B
    if not gen2_csv.exists():
        print(f"ERROR: cannot find Gen-2 scores CSV in {GEN2_ITER_DIR}/results/", flush=True)
        return 1
    print(f"\nLoading Gen-2 scores from {gen2_csv} ...", flush=True)
    gen2_rows = []
    with open(gen2_csv) as f:
        for row in csv.DictReader(f):
            gen2_rows.append(row)
    gen2_rows.sort(key=lambda r: float(r["fitness"]), reverse=True)
    gen2_top_fitness = float(gen2_rows[0]["fitness"])
    print(f"  {len(gen2_rows)} rules loaded, top fitness = {gen2_top_fitness:.8f}", flush=True)

    # Identify top-5 elites
    elite_rows = gen2_rows[:N_ELITES]
    elite_ids  = [r["rule_id"] for r in elite_rows]
    print(f"\nTop-{N_ELITES} Gen-2 elites:", flush=True)
    for r in elite_rows:
        print(f"  {r['rule_id']}: fitness={r['fitness']}", flush=True)

    # Load elite rule dicts from Gen-2 population dir
    elites = []
    for rule_id in elite_ids:
        rule_path = GEN2_POP_DIR / f"{rule_id}.json"
        if not rule_path.exists():
            print(f"ERROR: missing Gen-2 rule file {rule_path}", flush=True)
            return 1
        with open(rule_path) as f:
            rule_dict = json.load(f)
        rule_dict = {int(k): int(v) for k, v in rule_dict.items()}
        pairs     = extract_c2_generator_pairs(rule_dict)
        print(f"  Loaded {rule_id}: {len(pairs)} generator pairs", flush=True)
        elites.append({"rule_id": rule_id, "rule_dict": rule_dict, "pairs": pairs})

    # Decide which 10 rules will be mutated
    rng          = random.Random(BREED_SEED)
    mutate_set   = set(rng.sample(range(POPULATION_SIZE), N_MUTATIONS))
    print(f"\nMutation indices: {sorted(mutate_set)}", flush=True)

    # Breed Gen-3 population
    print(f"\nBreeding {POPULATION_SIZE} Gen-3 rules ...", flush=True)
    population: list[dict] = []
    failed = 0
    for i in range(POPULATION_SIZE):
        # Choose two distinct parents at random from the elite pool
        pa, pb = rng.sample(elites, 2)
        mutate = i in mutate_set

        result = breed_child(pa["pairs"], pb["pairs"], rng, mutate)
        if result is None:
            failed += 1
            print(f"  WARNING: breed failed for rule_{i:03d}, cloning best elite", flush=True)
            rule_d = elites[0]["rule_dict"]
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

    # Evaluate all Gen-3 rules
    print(f"\nEvaluating {POPULATION_SIZE} rules ({STEPS} steps) ...", flush=True)
    rows = []
    for idx, entry in enumerate(population):
        rule_id   = entry["rule_id"]
        rule_dict = entry["rule_dict"]
        res       = evaluate_late_displacement(rule_dict, ash_grid, grid_size, initial_bits)

        rows.append({
            "rule_id":              rule_id,
            "fitness":              round(res["fitness"], 8),
            "final_bits":           res["final_bits"],
            "final_objects":        res["final_objects"],
            "displacement_100_200": round(res["displacement_100_200"], 6),
            "_chaotic":             res["is_chaotic"],
            "_dead":                res["is_dead"],
        })

        if (idx + 1) % 10 == 0:
            print(
                f"  Evaluated {idx+1}/{POPULATION_SIZE}  "
                f"last: {rule_id} fitness={res['fitness']:.8f}  "
                f"bits={res['final_bits']}",
                flush=True,
            )

    # Summary stats
    fitnesses     = [r["fitness"] for r in rows]
    chaotic_count = sum(1 for r in rows if r["_chaotic"])
    dead_count    = sum(1 for r in rows if r["_dead"])
    viable_rows   = [r for r in rows if not r["_chaotic"] and not r["_dead"]]
    viable_count  = len(viable_rows)
    gen3_top      = max(fitnesses)
    viable_fits   = [r["fitness"] for r in viable_rows]
    gen3_mean     = float(np.mean(viable_fits)) if viable_fits else 0.0
    beating_gen2  = sum(1 for f in fitnesses if f > gen2_top_fitness)
    improvement   = (gen3_top - gen2_top_fitness) / gen2_top_fitness * 100.0 \
                    if gen2_top_fitness > 0 else 0.0

    # Print per-rule results
    print("\n=== Gen-3 Per-Rule Results ===", flush=True)
    for r in rows:
        status = "CHAOTIC" if r["_chaotic"] else ("DEAD" if r["_dead"] else "viable")
        print(
            f"  {r['rule_id']}: fitness={r['fitness']:.8f}  "
            f"bits={r['final_bits']}  disp={r['displacement_100_200']:.4f}  [{status}]",
            flush=True,
        )

    # Save CSV (only the specified columns)
    fieldnames = ["rule_id", "fitness", "final_bits", "final_objects", "displacement_100_200"]
    csv_rows   = [{k: r[k] for k in fieldnames} for r in rows]
    with open(GEN3_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nSaved CSV: {GEN3_CSV}", flush=True)

    # Save result.yaml
    result = {
        "gen2_top_fitness":         round(gen2_top_fitness, 8),
        "gen3_top_fitness":         round(float(gen3_top), 8),
        "fitness_improvement_pct":  round(float(improvement), 4),
        "rules_beating_gen2_top":   int(beating_gen2),
        "viable_rules":             int(viable_count),
        "chaotic_rules":            int(chaotic_count),
        "gen3_mean_fitness":        round(float(gen3_mean), 8),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}", flush=True)

    print("\n=== Gen-3 Summary ===", flush=True)
    print(f"  gen2_top_fitness:        {gen2_top_fitness:.8f}", flush=True)
    print(f"  gen3_top_fitness:        {gen3_top:.8f}", flush=True)
    print(f"  fitness_improvement_pct: {improvement:+.4f}%", flush=True)
    print(f"  rules_beating_gen2_top:  {beating_gen2}", flush=True)
    print(f"  viable_rules:            {viable_count}", flush=True)
    print(f"  chaotic_rules:           {chaotic_count}", flush=True)
    print(f"  dead_rules:              {dead_count}", flush=True)
    print(f"  gen3_mean_fitness:       {gen3_mean:.8f}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
