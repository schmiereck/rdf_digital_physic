#!/usr/bin/env python3
"""
run_c2_dense_motion_evolution.py

Generates 100 random, reversible, dense C2-symmetric rules and evaluates
each with the multi-seed motion-based fitness metric:

    fitness = displacement / (1 + final_bit_count)

Dense rules have ~32 non-identity mappings (25% of 128 states), compared to
the sparse rules in iter_095 which had only 8-16 non-identity mappings.

C2 symmetry = 180-degree rotation = 3 steps in the hex neighbor ring.

Evaluation uses the standard suite of 21 contiguous seeds (11 trihexes +
10 tetrahexes).  The final score for a rule is the maximum fitness across
all 21 seeds, run for 500 steps each.
"""

import csv
import json
import math
import random
import sys
from itertools import combinations
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POP_DIR      = PROJECT_ROOT / "archive" / "iter_096" / "population"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_096" / "results"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_096" / "result.yaml"

POPULATION_SIZE  = 1000
STEPS            = 500
MAX_CELLS        = 500   # lower cap: dense rules cause explosion; early cutoff keeps evaluation fast
TARGET_MAPPINGS  = 32   # ~25% of 128 states; each valid pair adds 4 mappings
MAX_GEN_ATTEMPTS = 200  # retries per rule to satisfy non-conserving constraint

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


# ── C2-symmetric rule helpers ─────────────────────────────────────────────────
# MSB encoding: bit 6 = center, bits 5-0 = E, SE, SW, W, NW, NE

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1  # E
    b2 = (state >> 4) & 1  # SE
    b3 = (state >> 3) & 1  # SW
    b4 = (state >> 2) & 1  # W
    b5 = (state >> 1) & 1  # NW
    b6 = (state >> 0) & 1  # NE
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


# ── Dense C2 rule generation ──────────────────────────────────────────────────

def _build_dense_c2_rule(rng: random.Random, target_mappings: int = TARGET_MAPPINGS) -> dict:
    """
    Generate a single random, reversible, dense C2-symmetric rule.

    Iteratively picks pairs of orbits {A, rotate_c2(A)} and {B, rotate_c2(B)}
    from the still-unmapped states and adds the 4-way swap until
    `target_mappings` non-identity mappings are collected.
    """
    unmapped = set(range(128))
    rule: dict = {}
    non_identity_count = 0

    while non_identity_count < target_mappings:
        # States eligible to be A: not a C2 fixed point, rotation also unmapped
        eligible = [s for s in unmapped if s != rotate_c2(s) and rotate_c2(s) in unmapped]
        if len(eligible) < 4:
            break  # not enough free orbits to proceed

        a  = rng.choice(eligible)
        ra = rotate_c2(a)

        # States eligible to be B: same criteria, orbits disjoint from {A, rA}
        eligible_b = [
            s for s in eligible
            if s != a and s != ra and rotate_c2(s) != a and rotate_c2(s) != ra
        ]
        if not eligible_b:
            continue  # re-pick A next iteration

        b  = rng.choice(eligible_b)
        rb = rotate_c2(b)

        quad = {a, b, ra, rb}
        if len(quad) == 4 and all(s in unmapped for s in quad):
            rule[a]  = b
            rule[b]  = a
            rule[ra] = rb
            rule[rb] = ra
            unmapped -= quad
            non_identity_count += 4

    return rule


def generate_dense_c2_rule(rng: random.Random) -> dict:
    """
    Repeatedly generates dense C2 rules until one is non-conserving
    (at least one mapping changes the cell-count bit).
    """
    for _ in range(MAX_GEN_ATTEMPTS):
        rule = _build_dense_c2_rule(rng)
        if any(bin(k).count('1') != bin(v).count('1') for k, v in rule.items()):
            return rule
    # Fallback: return last attempt even if conserving
    return _build_dense_c2_rule(rng)


# ── Seed generation (standard 21-seed suite) ──────────────────────────────────

def _apply_rotation(q, r, t):
    if t == 0: return ( q,       r      )
    if t == 1: return (-r,       q + r  )
    if t == 2: return (-(q + r), q      )
    if t == 3: return (-q,      -r      )
    if t == 4: return ( r,      -(q + r))
    if t == 5: return ( q + r,  -q      )
    raise ValueError(t)


def _translate_norm(cells) -> frozenset:
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _rotation_norm(cells) -> frozenset:
    best = None
    for t in range(6):
        norm = _translate_norm([_apply_rotation(q, r, t) for q, r in cells])
        if best is None or sorted(norm) < sorted(best):
            best = norm
    return best


def _is_connected(cells) -> bool:
    cs = set(cells)
    start = next(iter(cs))
    visited = {start}
    stack = [start]
    while stack:
        q, r = stack.pop()
        for dq, dr in HEX_DIRS:
            nb = (q + dq, r + dr)
            if nb in cs and nb not in visited:
                visited.add(nb)
                stack.append(nb)
    return len(visited) == len(cs)


def _build_trihex_seeds():
    coord_range = range(-3, 4)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 3):
        if not _is_connected(combo):
            continue
        cf = _translate_norm(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(cf)
    return seeds


def _build_tetrahex_seeds():
    coord_range = range(-4, 5)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 4):
        if not _is_connected(combo):
            continue
        cf = _rotation_norm(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(_translate_norm(combo))
    return seeds


def _build_seed_suite():
    trihexes   = _build_trihex_seeds()
    tetrahexes = _build_tetrahex_seeds()
    suite = {}
    for i, s in enumerate(trihexes,   1): suite[f"3bit_{i:02d}"] = s
    for i, s in enumerate(tetrahexes, 1): suite[f"4bit_{i:02d}"] = s
    return suite


ALL_SEEDS: dict = _build_seed_suite()


# ── Sparse hexagonal CA ───────────────────────────────────────────────────────

def _neighborhood(cells_set: frozenset, q: int, r: int) -> int:
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    candidates: set = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            candidates.add((q + dq, r + dr))
    new_cells: set = set()
    for q, r in candidates:
        nbr    = _neighborhood(cells, q, r)
        mapped = rule.get(nbr, nbr)
        if (mapped >> 6) & 1:
            new_cells.add((q, r))
    return frozenset(new_cells)


def _translate_normalize(cells: frozenset) -> frozenset:
    if not cells:
        return frozenset()
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _center_of_mass(cells: frozenset) -> tuple:
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, _ in cells) / n, sum(r for _, r in cells) / n)


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_seed(rule: dict, seed: frozenset) -> dict:
    current    = seed
    init_shape = _translate_normalize(current)
    init_com   = _center_of_mass(current)
    history: dict = {init_shape: (0, init_com)}

    for t in range(STEPS):
        current = step_cells(current, rule)

        if len(current) == 0:
            return {"fitness": 0.0, "kind": "decayed",   "final_bit_count": 0,
                    "period": 0, "displacement": 0.0, "dq": 0.0, "dr": 0.0}

        if len(current) > MAX_CELLS:
            return {"fitness": 0.0, "kind": "exploded",  "final_bit_count": len(current),
                    "period": 0, "displacement": 0.0, "dq": 0.0, "dr": 0.0}

        shape = _translate_normalize(current)
        com   = _center_of_mass(current)

        if shape in history:
            prev_t, prev_com = history[shape]
            period       = (t + 1) - prev_t
            dq           = com[0] - prev_com[0]
            dr           = com[1] - prev_com[1]
            displacement = math.sqrt(dq * dq + dr * dr)
            final_bits   = len(current)
            fitness      = displacement / (1.0 + final_bits) if displacement > 1e-9 else 0.0
            kind = "glider" if displacement > 1e-9 else ("still_life" if period == 1 else "oscillator")
            return {"fitness": fitness, "kind": kind, "final_bit_count": final_bits,
                    "period": period, "displacement": displacement, "dq": dq, "dr": dr}

        history[shape] = (t + 1, com)

    return {"fitness": 0.0, "kind": "no_cycle", "final_bit_count": len(current),
            "period": 0, "displacement": 0.0, "dq": 0.0, "dr": 0.0}


def evaluate_rule_multiseed(rule: dict) -> dict:
    best_fitness   = 0.0
    best_seed_name = ""
    best_result    = None

    for seed_name, seed_cells in ALL_SEEDS.items():
        res = evaluate_seed(rule, seed_cells)
        if res["fitness"] > best_fitness:
            best_fitness   = res["fitness"]
            best_seed_name = seed_name
            best_result    = res

    if best_result is None:
        best_result = {"fitness": 0.0, "kind": "no_motion", "final_bit_count": 0,
                       "period": 0, "displacement": 0.0, "dq": 0.0, "dr": 0.0}

    return {
        "best_fitness":   best_fitness,
        "best_seed_name": best_seed_name,
        "best_kind":      best_result["kind"],
        "best_period":    best_result["period"],
        "best_bit_count": best_result["final_bit_count"],
        "best_dq":        best_result["dq"],
        "best_dr":        best_result["dr"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POP_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    n_tri = sum(1 for k in ALL_SEEDS if k.startswith("3bit"))
    n_tet = sum(1 for k in ALL_SEEDS if k.startswith("4bit"))
    print(f"Seed suite: {len(ALL_SEEDS)} seeds ({n_tri} trihexes + {n_tet} tetrahexes)")
    print(f"Target non-identity mappings per rule: {TARGET_MAPPINGS}")

    # ── Step 1: Generate dense C2-symmetric population ────────────────────────
    print(f"\n=== Step 1: Generating {POPULATION_SIZE} dense C2-symmetric rules ===")
    rng = random.Random(96)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict = generate_dense_c2_rule(rng)
        rule_id   = f"rule_{i:03d}"
        out_path  = POP_DIR / f"{rule_id}.json"
        rule_str  = {str(k): v for k, v in rule_dict.items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        n_active = len(rule_dict)
        rules.append({"rule_id": rule_id, "rule_dict": rule_dict, "path": out_path,
                       "n_active": n_active})
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE} ...")

    avg_active = sum(r["n_active"] for r in rules) / len(rules)
    print(f"  Saved {POPULATION_SIZE} rules to {POP_DIR}")
    print(f"  Average non-identity mappings per rule: {avg_active:.1f}\n")

    # ── Step 2: Multi-seed motion evaluation ──────────────────────────────────
    print(f"=== Step 2: Evaluating {POPULATION_SIZE} rules across {len(ALL_SEEDS)} seeds ===")
    rows = []
    for entry in rules:
        res    = evaluate_rule_multiseed(entry["rule_dict"])
        marker = " <-- GLIDER" if res["best_kind"] == "glider" else ""
        print(f"  {entry['rule_id']}: seed={res['best_seed_name']:<12s}  "
              f"kind={res['best_kind']:<12s}  "
              f"fitness={res['best_fitness']:.8f}  "
              f"bits={res['best_bit_count']:4d}  "
              f"period={res['best_period']:4d}{marker}")
        rows.append({"rule_id": entry["rule_id"] + ".json", **res})

    # ── Step 3: Save CSV ───────────────────────────────────────────────────────
    csv_path   = RESULTS_DIR / "c2_dense_scores.csv"
    fieldnames = ["rule_id", "best_fitness", "best_seed_name", "best_kind",
                  "best_period", "best_bit_count", "best_dq", "best_dr"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {csv_path}")

    # ── Step 4: Summarize ─────────────────────────────────────────────────────
    gliders            = [r for r in rows if r["best_fitness"] > 0]
    rules_with_motion  = len(gliders)
    top_row            = max(rows, key=lambda r: r["best_fitness"])

    top_fitness   = top_row["best_fitness"]
    top_rule_id   = top_row["rule_id"] if top_fitness > 0 else ""
    top_seed_name = top_row["best_seed_name"]
    top_period    = top_row["best_period"]
    top_bit_count = top_row["best_bit_count"]
    top_dq        = top_row["best_dq"]
    top_dr        = top_row["best_dr"]

    glider_info = (
        f"seed={top_seed_name} period={top_period} bits={top_bit_count} "
        f"velocity=({top_dq:.4f},{top_dr:.4f})"
        if top_fitness > 0 else ""
    )

    print("\n=== Summary ===")
    print(f"  rules_with_motion:       {rules_with_motion}")
    print(f"  top_rule_id:             {top_rule_id}")
    print(f"  top_fitness_score:       {top_fitness:.10f}")
    print(f"  top_seed:                {top_seed_name}")
    print(f"  top_glider_period:       {top_period}")
    print(f"  top_glider_bits:         {top_bit_count}")
    print(f"  top_glider_velocity:     ({top_dq:.4f}, {top_dr:.4f})")

    yaml_result = {
        "rules_with_motion":         rules_with_motion,
        "top_fitness_score":         round(float(top_fitness), 10),
        "top_rule_id":               top_rule_id,
        "top_rule_glider_seed_info": glider_info,
        "top_rule_glider_period":    int(top_period),
        "top_rule_glider_bit_count": int(top_bit_count),
        "top_rule_glider_velocity":  [round(float(top_dq), 6), round(float(top_dr), 6)],
        "population_size":           POPULATION_SIZE,
        "seeds_evaluated":           len(ALL_SEEDS),
        "target_mappings_per_rule":  TARGET_MAPPINGS,
        "avg_active_mappings":       round(avg_active, 2),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}")

    return 0 if rules_with_motion >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
