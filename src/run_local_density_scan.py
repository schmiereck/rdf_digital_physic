#!/usr/bin/env python3
"""
run_local_density_scan.py

Density scan for local-fitness founders. Tests three populations of 100 random
C2-symmetric rules at different densities (4/8/16 kernel pairs), evaluating each
with the local fitness metric targeting the two closest oscillators in the
rule_011 remnant (object IDs 2 and 3 from iter_133).
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
REMNANT_OBJECTS_PATH = (
    PROJECT_ROOT / "archive" / "iter_133" / "results" / "remnant_objects.json"
)

ITER_DIR = PROJECT_ROOT / "archive" / "iter_136"
RESULTS_DIR = ITER_DIR / "results"
RESULT_YAML = RESULTS_DIR / "result.yaml"

POPULATION_SIZE = 100
SIM_STEPS = 200
LATE_START = 100
TRACKING_PADDING = 25
MAX_ATTEMPTS = 50000
MAX_PAIR_TRIES = 2000

DENSITY_CONFIGS = [
    {"name": "low_density",    "n_pairs": 4,  "seed_base": 1000},
    {"name": "medium_density", "n_pairs": 8,  "seed_base": 2000},
    {"name": "high_density",   "n_pairs": 16, "seed_base": 3000},
]

VIABLE_FITNESS_THRESHOLD = 0.001
VIABLE_BIT_RATIO_MAX = 3.0

HEX_DIRS = [
    ( 1,  0), ( 1, -1), ( 0, -1),
    (-1,  0), (-1,  1), ( 0,  1),
]


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
    """Generate a random C2-symmetric reversible rule with exactly n_pairs kernel pairs."""
    rng = random.Random(seed)
    for _ in range(MAX_ATTEMPTS):
        pairs: list = []
        used_states: set = set()
        ok = True
        for _ in range(n_pairs):
            found = False
            for _ in range(MAX_PAIR_TRIES):
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
        f"Failed to generate C2 rule with {n_pairs} pairs after {MAX_ATTEMPTS} attempts"
    )


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


def com_in_box(grid: np.ndarray, q_min: int, q_max: int,
               r_min: int, r_max: int) -> tuple:
    sub = grid[q_min:q_max + 1, r_min:r_max + 1]
    qs, rs = np.where(sub > 0)
    if len(qs) == 0:
        return None, 0
    return (float(np.mean(qs)) + q_min, float(np.mean(rs)) + r_min), int(len(qs))


def find_two_closest_oscillators(objects: list) -> tuple:
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

def evaluate_local_fitness(
    rule_dict: dict,
    remnant_grid: np.ndarray,
    target_cells: list,
    initial_bits: int,
    grid_size: int,
) -> dict:
    """
    Simulate rule on the full remnant; measure displacement of the target region.

    fitness = displacement / (1 + abs(bit_ratio - 1))
    where bit_ratio = bits_at_200 / initial_bits within the tracking box.
    """
    lut = rule_to_lut(rule_dict)

    qs = [c[0] for c in target_cells]
    rs = [c[1] for c in target_cells]
    q_min = max(0, min(qs) - TRACKING_PADDING)
    q_max = min(grid_size - 1, max(qs) + TRACKING_PADDING)
    r_min = max(0, min(rs) - TRACKING_PADDING)
    r_max = min(grid_size - 1, max(rs) + TRACKING_PADDING)

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
    fitness = displacement / (1.0 + abs(bit_ratio - 1.0))

    return {
        "fitness": fitness,
        "displacement": displacement,
        "bit_ratio": bit_ratio,
        "bits_100": bits_100,
        "bits_200": bits_200,
    }


# ── Density-level evaluation ──────────────────────────────────────────────────

def run_density_level(
    config: dict,
    remnant_grid: np.ndarray,
    target_cells: list,
    initial_bits: int,
    grid_size: int,
) -> tuple[list, dict]:
    name = config["name"]
    n_pairs = config["n_pairs"]
    seed_base = config["seed_base"]

    pop_dir = ITER_DIR / "population" / name
    pop_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {name} (n_pairs={n_pairs}, "
          f"{n_pairs * 4} non-identity mappings) ===", flush=True)

    rows = []
    for i in range(POPULATION_SIZE):
        rule_dict = generate_c2_rule(n_pairs, seed_base + i)

        rule_path = pop_dir / f"rule_{i:03d}.json"
        with open(rule_path, "w") as f:
            json.dump({str(k): v for k, v in rule_dict.items()}, f,
                      indent=2, sort_keys=True)

        res = evaluate_local_fitness(
            rule_dict, remnant_grid, target_cells, initial_bits, grid_size
        )

        is_viable = (
            res["fitness"] > VIABLE_FITNESS_THRESHOLD
            and res["bit_ratio"] < VIABLE_BIT_RATIO_MAX
        )

        rows.append({
            "rule_id":      f"rule_{i:03d}",
            "fitness":      round(res["fitness"], 8),
            "displacement": round(res["displacement"], 6),
            "bit_ratio":    round(res["bit_ratio"], 6),
            "bits_100":     res["bits_100"],
            "bits_200":     res["bits_200"],
            "viable":       is_viable,
        })

        if (i + 1) % 10 == 0:
            print(
                f"  [{i+1:3d}/{POPULATION_SIZE}] last: "
                f"fitness={res['fitness']:.6f}  disp={res['displacement']:.4f}  "
                f"bit_ratio={res['bit_ratio']:.4f}  bits={res['bits_200']}",
                flush=True,
            )

    viable_count = sum(1 for r in rows if r["viable"])
    fitnesses = [r["fitness"] for r in rows]
    top_fitness = max(fitnesses)
    mean_fitness = float(np.mean(fitnesses))

    print(f"  viable={viable_count}  "
          f"top_fitness={top_fitness:.8f}  mean_fitness={mean_fitness:.8f}",
          flush=True)

    return rows, {
        "viable_rules": viable_count,
        "top_fitness":  round(float(top_fitness), 8),
        "mean_fitness": round(float(mean_fitness), 8),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading remnant objects from {REMNANT_OBJECTS_PATH} ...", flush=True)
    with open(REMNANT_OBJECTS_PATH) as f:
        remnant_data = json.load(f)

    grid_size = remnant_data["grid_size"]
    objects = remnant_data["objects"]
    remnant_cells = remnant_data["remnant_cells"]

    remnant_grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in remnant_cells:
        remnant_grid[q, r] = 1

    n_osc = sum(1 for o in objects if o["type"] == "oscillator")
    print(f"  {len(objects)} objects ({n_osc} oscillators, "
          f"{len(remnant_cells)} live cells) on {grid_size}x{grid_size} grid",
          flush=True)

    obj_a, obj_b, target_dist = find_two_closest_oscillators(objects)
    target_cells = obj_a["cells"] + obj_b["cells"]
    initial_bits = obj_a["bit_count"] + obj_b["bit_count"]
    print(
        f"Target pair: obj{obj_a['object_id']} (p{obj_a['period']}, "
        f"{obj_a['bit_count']}bit, COM {obj_a['com_q']:.2f}/{obj_a['com_r']:.2f}) "
        f"<-> obj{obj_b['object_id']} (p{obj_b['period']}, {obj_b['bit_count']}bit, "
        f"COM {obj_b['com_q']:.2f}/{obj_b['com_r']:.2f})  dist={target_dist:.2f}",
        flush=True,
    )
    print(f"  {len(target_cells)} target cells, {initial_bits} initial bits",
          flush=True)

    yaml_result: dict = {}
    fieldnames = ["rule_id", "fitness", "displacement", "bit_ratio",
                  "bits_100", "bits_200", "viable"]

    for config in DENSITY_CONFIGS:
        rows, summary = run_density_level(
            config, remnant_grid, target_cells, initial_bits, grid_size
        )
        name = config["name"]
        yaml_result[f"{name}_viable_rules"] = summary["viable_rules"]
        yaml_result[f"{name}_top_fitness"]  = summary["top_fitness"]

        csv_path = RESULTS_DIR / f"{name}_scores.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  Saved CSV: {csv_path}", flush=True)

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved YAML: {RESULT_YAML}", flush=True)

    print("\n=== FINAL SUMMARY ===", flush=True)
    for config in DENSITY_CONFIGS:
        name = config["name"]
        viable = yaml_result[f"{name}_viable_rules"]
        top = yaml_result[f"{name}_top_fitness"]
        print(f"  {name}: viable={viable}  top_fitness={top:.8f}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
