#!/usr/bin/env python3
"""
validate_motion_fitness_metric.py

Tests a motion-based fitness function:
    fitness = displacement / (1 + final_bit_count)

where displacement is the Euclidean distance traveled by the center of mass
over one full period of a detected cycle.  A rule with no cycle (chaotic),
a zero-displacement cycle (still life / oscillator), or immediate decay all
receive fitness = 0.

Rules evaluated:
  rule_023.json (iter_084) – chaotic explosive rule (top from iter_085)
  rule_015.json (iter_088) – best non-annihilating Gen-3 rule (iter_089)
  symmetric_rule_nonconserving_A3_B14.json – classic still-life rule (iter_069)
"""

import json
import math
import sys
from pathlib import Path

import yaml

PROJECT_ROOT      = Path(__file__).parent.parent
CHAOTIC_RULE      = PROJECT_ROOT / "archive" / "iter_084" / "population" / "rule_023.json"
STABILIZING_RULE  = PROJECT_ROOT / "archive" / "iter_088" / "population" / "rule_015.json"
STILL_LIFE_RULE   = PROJECT_ROOT / "src" / "symmetric_rule_nonconserving_A3_B14.json"
RESULTS_DIR       = PROJECT_ROOT / "archive" / "iter_090" / "results"
RESULT_YAML       = PROJECT_ROOT / "archive" / "iter_090" / "result.yaml"

STEPS     = 500
MAX_CELLS = 3000   # cut off explosive / chaotic rules early

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]

# 4-bit T-shape: center + SW + NE + E  (matches grid-based T in validate_new_fitness_metric)
T_SHAPE_CELLS = frozenset([(0, 0), (0, -1), (0, 1), (1, 0)])


# ── Rule loading ──────────────────────────────────────────────────────────────

def load_rule(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


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

def evaluate_motion_fitness(rule_path: Path) -> dict:
    """
    Simulate from T-shape seed for up to STEPS steps.
    Detect the first shape cycle; if the cycle has nonzero displacement,
    compute fitness = displacement / (1 + final_bit_count), else 0.
    """
    rule    = load_rule(rule_path)
    current = T_SHAPE_CELLS

    init_shape = _translate_normalize(current)
    init_com   = _center_of_mass(current)

    # history maps normalized shape -> (step_index, center_of_mass)
    history: dict = {init_shape: (0, init_com)}

    for t in range(STEPS):
        current = step_cells(current, rule)

        if len(current) == 0:
            return {
                "fitness": 0.0, "kind": "decayed",
                "final_bit_count": 0, "period": 0, "displacement": 0.0,
            }

        if len(current) > MAX_CELLS:
            return {
                "fitness": 0.0, "kind": "exploded",
                "final_bit_count": len(current), "period": 0, "displacement": 0.0,
            }

        shape = _translate_normalize(current)
        com   = _center_of_mass(current)

        if shape in history:
            prev_t, prev_com = history[shape]
            period     = (t + 1) - prev_t
            dq         = com[0] - prev_com[0]
            dr         = com[1] - prev_com[1]
            displacement = math.sqrt(dq * dq + dr * dr)
            final_bits = len(current)
            fitness    = displacement / (1.0 + final_bits)

            if displacement > 1e-9:
                kind = "glider"
            elif period == 1:
                kind = "still_life"
            else:
                kind = "oscillator"

            return {
                "fitness": fitness, "kind": kind,
                "final_bit_count": final_bits, "period": period,
                "displacement": displacement,
            }

        history[shape] = (t + 1, com)

    return {
        "fitness": 0.0, "kind": "no_cycle",
        "final_bit_count": len(current), "period": 0, "displacement": 0.0,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    rules = [
        ("chaotic_rule",     CHAOTIC_RULE),
        ("stabilizing_rule", STABILIZING_RULE),
        ("still_life_rule",  STILL_LIFE_RULE),
    ]

    results: dict = {}
    for label, path in rules:
        print(f"Evaluating {label} ({path.name}) ...", flush=True)
        res = evaluate_motion_fitness(path)
        results[label] = res
        print(f"  kind={res['kind']:<15s}  fitness={res['fitness']:.8f}  "
              f"bits={res['final_bit_count']}  period={res['period']}  "
              f"displacement={res['displacement']:.6f}")

    chaotic_score     = results["chaotic_rule"]["fitness"]
    stabilizing_score = results["stabilizing_rule"]["fitness"]
    still_life_score  = results["still_life_rule"]["fitness"]

    metric_is_selective = (
        chaotic_score     < 1e-6 and
        stabilizing_score < 1e-6 and
        still_life_score  < 1e-6
    )

    print("\n=== Summary ===")
    print(f"  chaotic_rule_score:     {chaotic_score:.8f}")
    print(f"  stabilizing_rule_score: {stabilizing_score:.8f}")
    print(f"  still_life_rule_score:  {still_life_score:.8f}")
    print(f"  metric_is_selective:    {metric_is_selective}")

    yaml_result = {
        "chaotic_rule_score":     round(chaotic_score,     10),
        "stabilizing_rule_score": round(stabilizing_score, 10),
        "still_life_rule_score":  round(still_life_score,  10),
        "metric_is_selective":    bool(metric_is_selective),
        "chaotic_rule_kind":      results["chaotic_rule"]["kind"],
        "stabilizing_rule_kind":  results["stabilizing_rule"]["kind"],
        "still_life_rule_kind":   results["still_life_rule"]["kind"],
        "chaotic_rule_period":    results["chaotic_rule"]["period"],
        "stabilizing_rule_period": results["stabilizing_rule"]["period"],
        "still_life_rule_period": results["still_life_rule"]["period"],
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved: {RESULT_YAML}")

    return 0 if metric_is_selective else 1


if __name__ == "__main__":
    sys.exit(main())
