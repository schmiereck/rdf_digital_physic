#!/usr/bin/env python3
"""
reevaluate_gen3_for_motion.py

Re-evaluates the 100 Gen-3 rules (archive/iter_088/population/) using the
motion-based fitness metric validated in iter_090:

    fitness = displacement / (1 + final_bit_count)

where displacement is the Euclidean distance traveled by the centre of mass
over one full period of a detected stable cycle.  Rules that decay, explode,
or oscillate in place receive fitness = 0.

Seed: 4-bit contiguous T-shape on a 150×150 equivalent sparse grid.
Simulation: up to 500 steps.
"""

import csv
import json
import math
import sys
from pathlib import Path

import yaml

PROJECT_ROOT   = Path(__file__).parent.parent
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_088" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_092" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_092" / "result.yaml"

STEPS     = 500
MAX_CELLS = 3000

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]

# 4-bit contiguous T-shape (centre + three neighbours)
T_SHAPE_CELLS = frozenset([(0, 0), (0, -1), (0, 1), (1, 0)])


def load_rule(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


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


def evaluate_motion_fitness(rule_path: Path) -> dict:
    rule    = load_rule(rule_path)
    current = T_SHAPE_CELLS

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


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_files = sorted(POPULATION_DIR.glob("rule_*.json"))
    if len(rule_files) != 100:
        print(f"ERROR: expected 100 rule files, found {len(rule_files)}", file=sys.stderr)
        return 1

    rows = []
    for rule_path in rule_files:
        print(f"Evaluating {rule_path.name} ...", end=" ", flush=True)
        res = evaluate_motion_fitness(rule_path)
        rows.append({
            "rule_id":        rule_path.name,
            "fitness":        res["fitness"],
            "kind":           res["kind"],
            "period":         res["period"],
            "displacement":   res["displacement"],
            "final_bit_count": res["final_bit_count"],
            "dq":             res["dq"],
            "dr":             res["dr"],
        })
        print(f"kind={res['kind']:<12s}  fitness={res['fitness']:.8f}  "
              f"bits={res['final_bit_count']}  period={res['period']}")

    csv_path = RESULTS_DIR / "gen3_motion_scores.csv"
    fieldnames = ["rule_id", "fitness", "kind", "period", "displacement",
                  "final_bit_count", "dq", "dr"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {csv_path}")

    gliders  = [r for r in rows if r["fitness"] > 0]
    top_row  = max(rows, key=lambda r: r["fitness"])

    rules_with_motion      = len(gliders)
    top_fitness_score      = top_row["fitness"]
    top_rule_id            = top_row["rule_id"]
    top_rule_glider_period = top_row["period"]
    top_rule_glider_bits   = top_row["final_bit_count"]
    top_dq                 = top_row["dq"]
    top_dr                 = top_row["dr"]

    print("\n=== Summary ===")
    print(f"  rules_with_motion:  {rules_with_motion}")
    print(f"  top_rule_id:        {top_rule_id}")
    print(f"  top_fitness_score:  {top_fitness_score:.8f}")
    print(f"  top_glider_period:  {top_rule_glider_period}")
    print(f"  top_glider_bits:    {top_rule_glider_bits}")
    print(f"  top_glider_velocity: ({top_dq:.4f}, {top_dr:.4f})")

    yaml_result = {
        "rules_with_motion":         rules_with_motion,
        "top_fitness_score":         round(top_fitness_score, 10),
        "top_rule_id":               top_rule_id,
        "top_rule_glider_period":    int(top_rule_glider_period),
        "top_rule_glider_bit_count": int(top_rule_glider_bits),
        "top_rule_glider_velocity":  [round(top_dq, 6), round(top_dr, 6)],
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}")

    return 0 if rules_with_motion >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
