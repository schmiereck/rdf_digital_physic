#!/usr/bin/env python3
"""
run_motion_evolution_gen1.py

Generates 100 random, reversible, C6-symmetric, non-conserving rules (Gen-1)
and evaluates each with the motion-based fitness metric:

    fitness = displacement / (1 + final_bit_count)

where displacement is the Euclidean distance traveled by the center of mass
over one full period of the first detected shape cycle.  Rules with no cycle,
zero displacement, or immediate decay receive fitness = 0.
"""

import csv
import json
import math
import random
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POP_DIR      = PROJECT_ROOT / "archive" / "iter_091" / "population"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_091" / "results"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_091" / "result.yaml"

POPULATION_SIZE = 100
STEPS           = 500
MAX_CELLS       = 3000
MAX_ATTEMPTS    = 10000

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]

# 4-bit T-shape seed
T_SHAPE_CELLS = frozenset([(0, 0), (0, -1), (0, 1), (1, 0)])


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


# ── Geometry helpers ──────────────────────────────────────────────────────────

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


# ── Motion-fitness evaluation ─────────────────────────────────────────────────

def evaluate_motion_fitness(rule: dict) -> dict:
    current    = T_SHAPE_CELLS
    init_shape = _translate_normalize(current)
    init_com   = _center_of_mass(current)

    history: dict = {init_shape: (0, init_com)}

    for t in range(STEPS):
        current = step_cells(current, rule)

        if len(current) == 0:
            return {
                "fitness": 0.0, "kind": "decayed",
                "final_bit_count": 0, "period": 0,
                "displacement": 0.0, "dq": 0.0, "dr": 0.0,
            }

        if len(current) > MAX_CELLS:
            return {
                "fitness": 0.0, "kind": "exploded",
                "final_bit_count": len(current), "period": 0,
                "displacement": 0.0, "dq": 0.0, "dr": 0.0,
            }

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

            if displacement > 1e-9:
                kind = "glider"
            elif period == 1:
                kind = "still_life"
            else:
                kind = "oscillator"

            return {
                "fitness": fitness, "kind": kind,
                "final_bit_count": final_bits, "period": period,
                "displacement": displacement, "dq": dq, "dr": dr,
            }

        history[shape] = (t + 1, com)

    return {
        "fitness": 0.0, "kind": "no_cycle",
        "final_bit_count": len(current), "period": 0,
        "displacement": 0.0, "dq": 0.0, "dr": 0.0,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POP_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Generate population
    # ------------------------------------------------------------------
    print(f"=== Step 1: Generating {POPULATION_SIZE} random rules ===")
    rng = random.Random(91)
    rules = []
    for i in range(1, POPULATION_SIZE + 1):
        rule_dict, pairs = generate_random_rule(rng)
        rule_id  = f"rule_{i:03d}"
        out_path = POP_DIR / f"{rule_id}.json"
        rule_str = {str(k): v for k, v in rule_dict.items()}
        with open(out_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)
        rules.append({"rule_id": rule_id, "rule_dict": rule_dict, "path": out_path})
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE} ...")

    print(f"  Saved {POPULATION_SIZE} rules to {POP_DIR}\n")

    # ------------------------------------------------------------------
    # Step 2: Evaluate with motion-based fitness metric
    # ------------------------------------------------------------------
    print(f"=== Step 2: Evaluating {POPULATION_SIZE} rules (motion metric) ===")
    rows = []
    for entry in rules:
        m = evaluate_motion_fitness(entry["rule_dict"])
        entry.update(m)
        rows.append({
            "rule_id":        entry["rule_id"],
            "fitness_score":  round(m["fitness"], 10),
            "kind":           m["kind"],
            "period":         m["period"],
            "displacement":   round(m["displacement"], 8),
            "final_bit_count": m["final_bit_count"],
            "dq":             round(m["dq"], 6),
            "dr":             round(m["dr"], 6),
        })
        marker = " <-- GLIDER" if m["kind"] == "glider" else ""
        print(f"  {entry['rule_id']}: kind={m['kind']:<12s}  "
              f"fitness={m['fitness']:.8f}  bits={m['final_bit_count']:4d}  "
              f"period={m['period']:4d}{marker}")

    csv_path = RESULTS_DIR / "fitness_scores.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["rule_id", "fitness_score", "kind", "period",
                        "displacement", "final_bit_count", "dq", "dr"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n  Saved: {csv_path}")

    # ------------------------------------------------------------------
    # Step 3: Summarize
    # ------------------------------------------------------------------
    print("\n=== Step 3: Summary ===")
    glider_rows = [r for r in rows if r["fitness_score"] > 0]
    rules_with_motion = len(glider_rows)

    if glider_rows:
        top = max(glider_rows, key=lambda r: r["fitness_score"])
        top_fitness       = top["fitness_score"]
        top_rule_id       = top["rule_id"] + ".json"
        top_period        = top["period"]
        top_bit_count     = top["final_bit_count"]
        top_dq            = top["dq"]
        top_dr            = top["dr"]
        glider_rule_found = True
    else:
        top_fitness       = 0.0
        top_rule_id       = ""
        top_period        = 0
        top_bit_count     = 0
        top_dq            = 0.0
        top_dr            = 0.0
        glider_rule_found = False

    print(f"  glider_rule_found:       {glider_rule_found}")
    print(f"  rules_with_motion:       {rules_with_motion}")
    print(f"  top_fitness_score:       {top_fitness:.10f}")
    print(f"  top_rule_id:             {top_rule_id}")
    print(f"  top_rule_glider_period:  {top_period}")
    print(f"  top_rule_glider_bits:    {top_bit_count}")
    print(f"  top_rule_glider_velocity: ({top_dq}, {top_dr})")

    yaml_result = {
        "glider_rule_found":          glider_rule_found,
        "population_size":            POPULATION_SIZE,
        "rules_with_motion":          rules_with_motion,
        "top_fitness_score":          float(top_fitness),
        "top_rule_id":                top_rule_id,
        "top_rule_glider_period":     top_period,
        "top_rule_glider_bit_count":  top_bit_count,
        "top_rule_glider_velocity":   [float(top_dq), float(top_dr)],
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\n  Saved: {RESULT_YAML}")

    return 0 if glider_rule_found else 1


if __name__ == "__main__":
    sys.exit(main())
