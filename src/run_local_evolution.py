#!/usr/bin/env python3
"""
run_local_evolution.py

Evolves Gen-4 rules using a localized fitness metric targeting the two closest
oscillators (obj2/obj3) in the rule_011 remnant. Breeds from top-5 Gen-3 elites
using the same 4+4 crossover and 10% mutation strategy as previous generations.
"""

import csv
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent
ASH_PATTERN_PATH = SRC_DIR / "ash_pattern.json"
RULE_011_PATH = PROJECT_ROOT / "archive" / "iter_131" / "population" / "rule_011.json"
GEN3_POP_DIR = PROJECT_ROOT / "archive" / "iter_131" / "population"
REMNANT_OBJECTS_PATH = PROJECT_ROOT / "archive" / "iter_133" / "results" / "remnant_objects.json"

ITER_DIR = PROJECT_ROOT / "archive" / "iter_135"
POPULATION_DIR = ITER_DIR / "population"
RESULTS_DIR = ITER_DIR / "results"
RESULT_YAML = ITER_DIR / "result.yaml"
GEN4_CSV = RESULTS_DIR / "gen4_local_fitness_scores.csv"
BEST_RULE_PATH = POPULATION_DIR / "best_local_rule.json"

GRID_SIZE = 200
SIM_STEPS = 200
LATE_START = 100
ISO_PADDING = 50
MAX_PERIOD_STEPS = 100
TRACKING_PADDING = 25

N_ELITES = 5
N_PAIRS = 8
POPULATION_SIZE = 100
N_MUTATIONS = 10
BREED_SEED = 135
MAX_PAIR_TRIES = 4000
MAX_BREED_RETRIES = 500

HEX_DIRS = [
    ( 1,  0), ( 1, -1), ( 0, -1),
    (-1,  0), (-1,  1), ( 0,  1),
]


# ── C2 helpers ─────────────────────────────────────────────────────────────────

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
    seen = set()
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
    p1 = list(p1_pairs)
    p2 = list(p2_pairs)
    rng.shuffle(p1)
    rng.shuffle(p2)
    return p1[:4] + p2[:4]


def mutate_one_pair(pairs: list, rng: random.Random) -> list:
    pairs = list(pairs)
    idx = rng.randrange(len(pairs))
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
) -> tuple | None:
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


def get_connected_components(grid: np.ndarray, grid_size: int) -> list:
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    components = []
    for start in live:
        if start in visited:
            continue
        component = []
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            component.append(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % grid_size, (r + dr) % grid_size)
                if nb in live and nb not in visited:
                    stack.append(nb)
        components.append(component)
    return components


def normalize_shape(cells) -> frozenset:
    if not cells:
        return frozenset()
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    min_q, min_r = min(qs), min(rs)
    return frozenset((q - min_q, r - min_r) for q, r in cells)


def characterize_object(cells: list, lut: np.ndarray,
                        max_steps: int = MAX_PERIOD_STEPS,
                        padding: int = ISO_PADDING) -> tuple:
    """Simulate object in isolation; return (type_str, period)."""
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    min_q, max_q = min(qs), max(qs)
    min_r, max_r = min(rs), max(rs)
    h = max_q - min_q + 1 + 2 * padding
    w = max_r - min_r + 1 + 2 * padding
    iso = np.zeros((h, w), dtype=np.uint8)
    for q, r in cells:
        iso[q - min_q + padding, r - min_r + padding] = 1
    shape_to_step: dict = {}
    for step in range(max_steps + 1):
        live = list(map(tuple, np.argwhere(iso == 1)))
        if not live:
            return 'decayed', 0
        norm = normalize_shape(live)
        if norm in shape_to_step:
            prev = shape_to_step[norm]
            period = step - prev
            status = 'still-life' if period == 1 else 'oscillator'
            return status, period
        shape_to_step[norm] = step
        iso = step_grid(iso, lut)
    return 'unknown', 0


# ── Remnant object generation ─────────────────────────────────────────────────

def build_remnant_objects(ash_path: Path, rule_path: Path,
                          grid_size: int = GRID_SIZE,
                          run_steps: int = SIM_STEPS) -> dict:
    """Simulate rule_011 to produce remnant, extract and characterize all objects."""
    print(f"Loading rule_011 from {rule_path}", flush=True)
    with open(rule_path) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)

    print(f"Loading ash pattern from {ash_path}", flush=True)
    with open(ash_path) as f:
        ash_data = json.load(f)
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        if q < grid_size and r < grid_size:
            grid[q, r] = 1
    print(f"  {int(grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    print(f"Simulating {run_steps} steps with rule_011 ...", flush=True)
    for s in range(run_steps):
        grid = step_grid(grid, lut)
        if (s + 1) % 50 == 0:
            print(f"  step {s+1:3d}: {int(grid.sum())} bits", flush=True)
    remnant_cells_np = np.argwhere(grid == 1)
    remnant_cells = [[int(q), int(r)] for q, r in remnant_cells_np]
    print(f"  Remnant: {len(remnant_cells)} live cells", flush=True)

    print("Finding connected components ...", flush=True)
    components = get_connected_components(grid, grid_size)
    print(f"  Found {len(components)} objects", flush=True)

    print("Characterizing objects in isolation ...", flush=True)
    objects = []
    for i, comp in enumerate(components):
        obj_type, period = characterize_object(comp, lut)
        bit_count = len(comp)
        com_q = float(np.mean([c[0] for c in comp]))
        com_r = float(np.mean([c[1] for c in comp]))
        cells_list = [[int(c[0]), int(c[1])] for c in comp]
        objects.append({
            "object_id": i + 1,
            "type": obj_type,
            "period": period,
            "bit_count": bit_count,
            "com_q": round(com_q, 4),
            "com_r": round(com_r, 4),
            "cells": cells_list,
        })
        print(f"  [{i+1:3d}/{len(components)}] {obj_type:<12s} p={period:3d}  "
              f"bits={bit_count:3d}  COM=({com_q:.1f}, {com_r:.1f})", flush=True)

    return {
        "grid_size": grid_size,
        "run_steps": run_steps,
        "remnant_cells": remnant_cells,
        "objects": objects,
    }


def find_two_closest_oscillators(objects: list) -> tuple:
    """Return (obj_a, obj_b, distance) for the oscillator pair with minimum COM distance."""
    oscillators = [o for o in objects if o["type"] == "oscillator"]
    if len(oscillators) < 2:
        raise ValueError(f"Need >= 2 oscillators, found {len(oscillators)}")
    min_dist = float('inf')
    best_a, best_b = oscillators[0], oscillators[1]
    for i in range(len(oscillators)):
        for j in range(i + 1, len(oscillators)):
            dq = oscillators[i]["com_q"] - oscillators[j]["com_q"]
            dr = oscillators[i]["com_r"] - oscillators[j]["com_r"]
            dist = math.sqrt(dq**2 + dr**2)
            if dist < min_dist:
                min_dist = dist
                best_a, best_b = oscillators[i], oscillators[j]
    return best_a, best_b, min_dist


# ── Local fitness metric ──────────────────────────────────────────────────────

def com_in_box(grid: np.ndarray, q_min: int, q_max: int,
               r_min: int, r_max: int) -> tuple:
    """Return (COM as (q, r), bit_count) of live cells in the axis-aligned box."""
    sub = grid[q_min:q_max + 1, r_min:r_max + 1]
    qs, rs = np.where(sub > 0)
    if len(qs) == 0:
        return None, 0
    return (float(np.mean(qs)) + q_min, float(np.mean(rs)) + r_min), int(len(qs))


def evaluate_local_fitness(
    rule_dict: dict,
    remnant_grid: np.ndarray,
    target_cells: list,
    initial_bits: int,
    grid_size: int = GRID_SIZE,
    tracking_padding: int = TRACKING_PADDING,
) -> dict:
    """
    Simulate rule on the full remnant; measure displacement of the target region.

    Tracks live cells within a bounding box around the initial target cells.
    fitness = displacement / (1 + abs(1 - bit_ratio))
    """
    lut = rule_to_lut(rule_dict)

    qs = [c[0] for c in target_cells]
    rs = [c[1] for c in target_cells]
    q_min = max(0, min(qs) - tracking_padding)
    q_max = min(grid_size - 1, max(qs) + tracking_padding)
    r_min = max(0, min(rs) - tracking_padding)
    r_max = min(grid_size - 1, max(rs) + tracking_padding)

    grid = remnant_grid.copy()

    for _ in range(LATE_START):
        grid = step_grid(grid, lut)
    com_100, bits_100 = com_in_box(grid, q_min, q_max, r_min, r_max)

    for _ in range(SIM_STEPS - LATE_START):
        grid = step_grid(grid, lut)
    com_200, bits_200 = com_in_box(grid, q_min, q_max, r_min, r_max)

    if com_100 is None or com_200 is None:
        return {
            "fitness": 0.0, "displacement": 0.0, "bit_ratio": 0.0,
            "bits_100": bits_100 or 0, "bits_200": bits_200 or 0,
        }

    dq = com_200[0] - com_100[0]
    dr = com_200[1] - com_100[1]
    displacement = math.sqrt(dq**2 + dr**2)
    bit_ratio = bits_200 / initial_bits if initial_bits > 0 else 0.0
    fitness = displacement / (1.0 + abs(1.0 - bit_ratio))

    return {
        "fitness": fitness,
        "displacement": displacement,
        "bit_ratio": bit_ratio,
        "bits_100": bits_100,
        "bits_200": bits_200,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load or generate remnant_objects.json ─────────────────────────
    if not REMNANT_OBJECTS_PATH.exists():
        print("remnant_objects.json not found — generating ...", flush=True)
        remnant_data = build_remnant_objects(ASH_PATTERN_PATH, RULE_011_PATH)
        with open(REMNANT_OBJECTS_PATH, "w") as f:
            json.dump(remnant_data, f, indent=2)
        print(f"Saved: {REMNANT_OBJECTS_PATH}", flush=True)
    else:
        print(f"Loading existing {REMNANT_OBJECTS_PATH} ...", flush=True)
        with open(REMNANT_OBJECTS_PATH) as f:
            remnant_data = json.load(f)

    grid_size    = remnant_data["grid_size"]
    objects      = remnant_data["objects"]
    remnant_cells = remnant_data["remnant_cells"]

    remnant_grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in remnant_cells:
        remnant_grid[q, r] = 1

    n_osc  = sum(1 for o in objects if o["type"] == "oscillator")
    print(f"  {len(objects)} objects  ({n_osc} oscillators, "
          f"{len(remnant_cells)} live cells)", flush=True)

    # ── Step 2: Identify the two closest oscillators ──────────────────────────
    obj_a, obj_b, target_dist = find_two_closest_oscillators(objects)
    target_cells  = obj_a["cells"] + obj_b["cells"]
    initial_bits  = obj_a["bit_count"] + obj_b["bit_count"]
    print(
        f"Target pair: obj{obj_a['object_id']} (p{obj_a['period']}, "
        f"{obj_a['bit_count']}bit, COM {obj_a['com_q']:.2f}/{obj_a['com_r']:.2f}) "
        f"<-> obj{obj_b['object_id']} (p{obj_b['period']}, {obj_b['bit_count']}bit, "
        f"COM {obj_b['com_q']:.2f}/{obj_b['com_r']:.2f})  dist={target_dist:.2f}",
        flush=True,
    )
    print(f"  {len(target_cells)} target cells, {initial_bits} initial bits", flush=True)

    # ── Step 3: Load Gen-3 top-5 elites ──────────────────────────────────────
    _csv_a = PROJECT_ROOT / "archive" / "iter_131" / "results" / "gen3_fitness_scores.csv"
    _csv_b = PROJECT_ROOT / "archive" / "iter_131" / "results" / "reboot_gen3_scores.csv"
    gen3_csv = _csv_a if _csv_a.exists() else _csv_b
    if not gen3_csv.exists():
        print("ERROR: Gen-3 CSV not found in iter_131/results/", flush=True)
        return 1

    print(f"\nLoading Gen-3 scores from {gen3_csv.name} ...", flush=True)
    with open(gen3_csv) as f:
        gen3_rows = list(csv.DictReader(f))
    gen3_rows.sort(key=lambda r: float(r["fitness"]), reverse=True)
    elite_rows = gen3_rows[:N_ELITES]

    print(f"Top-{N_ELITES} Gen-3 elites:", flush=True)
    elites = []
    for row in elite_rows:
        rule_id   = row["rule_id"]
        rule_path = GEN3_POP_DIR / f"{rule_id}.json"
        if not rule_path.exists():
            print(f"ERROR: missing rule file {rule_path}", flush=True)
            return 1
        with open(rule_path) as f:
            rule_dict = json.load(f)
        rule_dict = {int(k): int(v) for k, v in rule_dict.items()}
        pairs = extract_c2_generator_pairs(rule_dict)
        elites.append({"rule_id": rule_id, "rule_dict": rule_dict, "pairs": pairs})
        print(f"  {rule_id}: fitness={row['fitness']}  ({len(pairs)} pairs)", flush=True)

    # ── Step 4: Breed Gen-4 population ───────────────────────────────────────
    rng        = random.Random(BREED_SEED)
    mutate_set = set(rng.sample(range(POPULATION_SIZE), N_MUTATIONS))
    print(f"\nBreeding {POPULATION_SIZE} Gen-4 rules "
          f"(mutation indices: {sorted(mutate_set)}) ...", flush=True)
    population = []
    failed     = 0
    for i in range(POPULATION_SIZE):
        pa, pb = rng.sample(elites, 2)
        result = breed_child(pa["pairs"], pb["pairs"], rng, i in mutate_set)
        if result is None:
            failed += 1
            print(f"  WARNING: breed failed for rule_{i:03d}, cloning elite 0",
                  flush=True)
            rule_d = elites[0]["rule_dict"]
        else:
            rule_d, _ = result
        population.append({"rule_id": f"rule_{i:03d}", "rule_dict": rule_d})
        if (i + 1) % 10 == 0:
            print(f"  Bred {i+1}/{POPULATION_SIZE}", flush=True)
    if failed:
        print(f"  Breed failures: {failed}", flush=True)

    # ── Step 5: Evaluate with local fitness metric ────────────────────────────
    print(f"\nEvaluating {POPULATION_SIZE} rules with local fitness "
          f"(tracking box padding={TRACKING_PADDING}) ...", flush=True)
    rows = []
    for idx, entry in enumerate(population):
        res = evaluate_local_fitness(
            entry["rule_dict"], remnant_grid, target_cells,
            initial_bits, grid_size, TRACKING_PADDING,
        )
        rows.append({
            "rule_id":    entry["rule_id"],
            "fitness":    round(res["fitness"], 8),
            "displacement": round(res["displacement"], 6),
            "bit_ratio":  round(res["bit_ratio"], 6),
            "bits_100":   res["bits_100"],
            "bits_200":   res["bits_200"],
            "rule_dict":  entry["rule_dict"],
        })
        if (idx + 1) % 10 == 0:
            print(
                f"  [{idx+1:3d}/{POPULATION_SIZE}] {entry['rule_id']}: "
                f"fitness={res['fitness']:.6f}  disp={res['displacement']:.4f}  "
                f"bit_ratio={res['bit_ratio']:.4f}  bits={res['bits_200']}",
                flush=True,
            )

    rows.sort(key=lambda r: r["fitness"], reverse=True)
    gen4_top_fitness = rows[0]["fitness"]

    # ── Step 6: Save CSV ──────────────────────────────────────────────────────
    fieldnames = ["rule_id", "fitness", "displacement", "bit_ratio", "bits_100", "bits_200"]
    with open(GEN4_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: r[k] for k in fieldnames} for r in rows])
    print(f"\nSaved CSV: {GEN4_CSV}", flush=True)

    # ── Step 7: Save best rule ────────────────────────────────────────────────
    best_rule_str = {str(k): v for k, v in rows[0]["rule_dict"].items()}
    with open(BEST_RULE_PATH, "w") as f:
        json.dump(best_rule_str, f, indent=2, sort_keys=True)
    print(f"Saved best rule: {BEST_RULE_PATH}  (id={rows[0]['rule_id']})", flush=True)

    # ── Step 8: Baseline — rule_011 local fitness ─────────────────────────────
    print("\nCalculating baseline (rule_011 local fitness) ...", flush=True)
    with open(RULE_011_PATH) as f:
        rule_011_dict = json.load(f)
    rule_011_dict = {int(k): int(v) for k, v in rule_011_dict.items()}
    baseline_res     = evaluate_local_fitness(
        rule_011_dict, remnant_grid, target_cells,
        initial_bits, grid_size, TRACKING_PADDING,
    )
    baseline_fitness = baseline_res["fitness"]
    print(f"  rule_011 local fitness: {baseline_fitness:.8f}  "
          f"disp={baseline_res['displacement']:.4f}  "
          f"bit_ratio={baseline_res['bit_ratio']:.4f}", flush=True)

    # ── Step 9: Summary stats and result.yaml ────────────────────────────────
    rules_beating = sum(1 for r in rows if r["fitness"] > baseline_fitness)

    result = {
        "top_local_fitness_gen4":           round(float(gen4_top_fitness), 8),
        "baseline_local_fitness_gen3_champ": round(float(baseline_fitness), 8),
        "rules_beating_baseline":            int(rules_beating),
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved: {RESULT_YAML}", flush=True)

    print("\n=== SUMMARY ===", flush=True)
    print(f"  top_local_fitness_gen4:             {gen4_top_fitness:.8f}", flush=True)
    print(f"  baseline_local_fitness_gen3_champ:  {baseline_fitness:.8f}", flush=True)
    print(f"  rules_beating_baseline:             {rules_beating}", flush=True)
    print(f"  best_rule_id:                       {rows[0]['rule_id']}", flush=True)
    print(f"  best_displacement:                  {rows[0]['displacement']:.6f}", flush=True)
    print(f"  best_bit_ratio:                     {rows[0]['bit_ratio']:.6f}", flush=True)
    print(f"  best_bits_200:                      {rows[0]['bits_200']}", flush=True)

    print("\n=== TOP 10 GEN-4 RULES BY LOCAL FITNESS ===", flush=True)
    for r in rows[:10]:
        print(
            f"  {r['rule_id']}: fitness={r['fitness']:.8f}  "
            f"disp={r['displacement']:.4f}  bit_ratio={r['bit_ratio']:.4f}  "
            f"bits_200={r['bits_200']}",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
