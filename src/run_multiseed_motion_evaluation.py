#!/usr/bin/env python3
"""
run_multiseed_motion_evaluation.py

Evaluates all 100 Gen-3 rules (archive/iter_088/population/) using the
motion-based fitness metric across a suite of 21 standard seeds:
  - 11 unique contiguous 3-bit trihexes
  - 10 unique one-sided contiguous 4-bit tetrahexes

For each rule, the maximum fitness across all 21 seeds is reported.

fitness = displacement / (1 + final_bit_count)
"""

import csv
import json
import math
import sys
from itertools import combinations
from pathlib import Path

import yaml

PROJECT_ROOT   = Path(__file__).parent.parent
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_088" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_093" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_093" / "result.yaml"

STEPS     = 500
MAX_CELLS = 3000

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]


# ---------------------------------------------------------------------------
# Seed generation (mirrors analyze_top_stabilizing_rule.py / iter_089)
# ---------------------------------------------------------------------------

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
    """All 11 fixed trihexes — unique under translation only."""
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
    """All 10 one-sided tetrahexes — unique under C6 rotation."""
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
    for i, s in enumerate(trihexes,   1): suite[f"3bit_{i:02d}"]  = s
    for i, s in enumerate(tetrahexes, 1): suite[f"4bit_{i:02d}"]  = s
    return suite


ALL_SEEDS: dict = _build_seed_suite()


# ---------------------------------------------------------------------------
# CA helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_seed(rule: dict, seed: frozenset) -> dict:
    current = seed

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


def evaluate_rule_multiseed(rule_path: Path) -> dict:
    rule = load_rule(rule_path)
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_files = sorted(POPULATION_DIR.glob("rule_*.json"))
    if len(rule_files) != 100:
        print(f"ERROR: expected 100 rule files, found {len(rule_files)}", file=sys.stderr)
        return 1

    n_tri  = sum(1 for k in ALL_SEEDS if k.startswith("3bit"))
    n_tet  = sum(1 for k in ALL_SEEDS if k.startswith("4bit"))
    print(f"Evaluating {len(rule_files)} rules across {len(ALL_SEEDS)} seeds "
          f"({n_tri} trihexes + {n_tet} tetrahexes)...")

    rows = []
    for rule_path in rule_files:
        print(f"  {rule_path.name} ...", end=" ", flush=True)
        res = evaluate_rule_multiseed(rule_path)
        rows.append({"rule_id": rule_path.name, **res})
        print(f"best_seed={res['best_seed_name']:<22s}  "
              f"kind={res['best_kind']:<12s}  "
              f"fitness={res['best_fitness']:.8f}  "
              f"bits={res['best_bit_count']}  "
              f"period={res['best_period']}")

    csv_path = RESULTS_DIR / "gen3_multiseed_scores.csv"
    fieldnames = ["rule_id", "best_fitness", "best_seed_name", "best_kind",
                  "best_period", "best_bit_count", "best_dq", "best_dr"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved CSV: {csv_path}")

    gliders  = [r for r in rows if r["best_fitness"] > 0]
    top_row  = max(rows, key=lambda r: r["best_fitness"])

    rules_with_motion = len(gliders)
    top_fitness_score = top_row["best_fitness"]
    top_rule_id       = top_row["rule_id"]
    top_seed_name     = top_row["best_seed_name"]
    top_period        = top_row["best_period"]
    top_bit_count     = top_row["best_bit_count"]
    top_dq            = top_row["best_dq"]
    top_dr            = top_row["best_dr"]

    print("\n=== Summary ===")
    print(f"  rules_with_motion:       {rules_with_motion}")
    print(f"  top_rule_id:             {top_rule_id}")
    print(f"  top_fitness_score:       {top_fitness_score:.8f}")
    print(f"  top_seed:                {top_seed_name}")
    print(f"  top_glider_period:       {top_period}")
    print(f"  top_glider_bits:         {top_bit_count}")
    print(f"  top_glider_velocity:     ({top_dq:.4f}, {top_dr:.4f})")

    yaml_result = {
        "rules_with_motion":           rules_with_motion,
        "top_fitness_score":           round(top_fitness_score, 10),
        "top_rule_id":                 top_rule_id,
        "top_rule_glider_seed_info":   top_seed_name,
        "top_rule_glider_period":      int(top_period),
        "top_rule_glider_bit_count":   int(top_bit_count),
        "top_rule_glider_velocity":    [round(top_dq, 6), round(top_dr, 6)],
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved YAML: {RESULT_YAML}")

    return 0 if rules_with_motion >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
