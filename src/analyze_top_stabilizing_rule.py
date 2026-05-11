#!/usr/bin/env python3
"""
analyze_top_stabilizing_rule.py

Find the best non-annihilating rule from the Gen-3 population (iter_088) and
search for gliders using all 21 standard contiguous seeds (11 trihex + 10
tetrahex).

A rule with fitness == 1.0 is a complete annihilator and is excluded.  The
highest-fitness survivor is tested exhaustively against all seeds.
"""

import csv
import json
import sys
from itertools import combinations
from pathlib import Path

import yaml

PROJECT_ROOT   = Path(__file__).parent.parent
# Actual file produced by iter_088
FITNESS_CSV    = PROJECT_ROOT / "archive" / "iter_088" / "results" / "gen3_fitness.csv"
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_088" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_089" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_089" / "result.yaml"

STEPS             = 500
MAX_PERIOD_SEARCH = 300
MAX_CELLS         = 500

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


# ── Hex geometry helpers ──────────────────────────────────────────────────────

def _apply_rotation(q, r, t):
    if t == 0: return ( q,       r      )
    if t == 1: return (-r,       q + r  )
    if t == 2: return (-(q + r), q      )
    if t == 3: return (-q,      -r      )
    if t == 4: return ( r,      -(q + r))
    if t == 5: return ( q + r,  -q      )
    raise ValueError(t)


def _translate_normalize(cells):
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _rotation_normalize(cells) -> frozenset:
    best = None
    for t in range(6):
        rot  = [_apply_rotation(q, r, t) for q, r in cells]
        norm = _translate_normalize(rot)
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


# ── Seed generators ───────────────────────────────────────────────────────────

def get_contiguous_3bit_seeds():
    """All 11 fixed trihex seeds (unique under translation only)."""
    coord_range = range(-3, 4)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 3):
        if not _is_connected(combo):
            continue
        cf = _translate_normalize(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(sorted(cf))
    return seeds


def get_contiguous_4bit_seeds():
    """All 10 one-sided tetrahex seeds (unique under C6 rotation)."""
    coord_range = range(-4, 5)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 4):
        if not _is_connected(combo):
            continue
        cf = _rotation_normalize(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(sorted(cf))
    return seeds


# ── Rule loading ──────────────────────────────────────────────────────────────

def load_rule(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


# ── Sparse-grid CA simulation ─────────────────────────────────────────────────

def _neighborhood(cells_set, q, r) -> int:
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    candidates = set(cells)
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


def _center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


# ── Glider / cycle detection ──────────────────────────────────────────────────

def test_seed(seed_cells, rule, steps: int = STEPS) -> dict:
    current = frozenset(seed_cells)
    shapes  = [_translate_normalize(current)]
    centers = [_center_of_mass(current)]

    for t in range(steps):
        current = step_cells(current, rule)

        if len(current) == 0:
            return {"stable": False, "period": 0, "displacement": (0, 0),
                    "kind": "decayed", "final_bit_count": 0}

        if len(current) > MAX_CELLS:
            return {"stable": False, "period": 0, "displacement": (0, 0),
                    "kind": "exploded", "final_bit_count": len(current)}

        shape = _translate_normalize(current)
        com   = _center_of_mass(current)

        search_start = max(0, len(shapes) - MAX_PERIOD_SEARCH)
        for prev_t in range(search_start, len(shapes)):
            if shapes[prev_t] == shape:
                period  = (t + 1) - prev_t
                dq_raw  = com[0] - centers[prev_t][0]
                dr_raw  = com[1] - centers[prev_t][1]
                dq = round(dq_raw)
                dr = round(dr_raw)
                is_moving = (dq != 0 or dr != 0)
                if period == 1 and not is_moving:
                    kind = "still_life"
                elif is_moving:
                    kind = "glider"
                else:
                    kind = "oscillator"
                return {"stable": True, "period": period,
                        "displacement": (dq, dr), "kind": kind,
                        "final_bit_count": len(current)}

        shapes.append(shape)
        centers.append(com)

    return {"stable": False, "period": 0, "displacement": (0, 0),
            "kind": "no_cycle", "final_bit_count": len(current)}


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    # Part 1: identify best non-annihilating rule
    print(f"Reading fitness scores from {FITNESS_CSV} ...")
    best_rule_id = None
    best_fitness = -1.0
    with open(FITNESS_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # column may be 'fitness' or 'fitness_score'
            score_key = "fitness_score" if "fitness_score" in row else "fitness"
            score = float(row[score_key])
            if score == 1.0:
                continue  # annihilator – skip
            if score > best_fitness:
                best_fitness  = score
                best_rule_id  = row["rule_id"]

    if best_rule_id is None:
        print("ERROR: no non-annihilating rule found", file=sys.stderr)
        return 2

    print(f"Best non-annihilating rule: {best_rule_id}  fitness={best_fitness:.6f}")

    rule_path = POPULATION_DIR / f"{best_rule_id}.json"
    print(f"Loading rule from {rule_path} ...")
    rule = load_rule(rule_path)
    print(f"  {len(rule)} non-identity entries in rule table")

    # Part 2: generate and test all 21 seeds
    seeds_3bit = get_contiguous_3bit_seeds()
    seeds_4bit = get_contiguous_4bit_seeds()
    print(f"Seeds: {len(seeds_3bit)} trihex + {len(seeds_4bit)} tetrahex = "
          f"{len(seeds_3bit) + len(seeds_4bit)} total")

    glider_found        = False
    glider_seed_bits    = 0
    glider_period       = 0
    stable_objects      = 0
    decayed_count       = 0
    counts: dict        = {}

    all_seeds = [("3bit", s) for s in seeds_3bit] + [("4bit", s) for s in seeds_4bit]

    for idx, (label, seed) in enumerate(all_seeds, 1):
        result = test_seed(seed, rule)
        kind   = result["kind"]
        counts[kind] = counts.get(kind, 0) + 1

        if result["stable"]:
            stable_objects += 1
        if kind == "decayed":
            decayed_count += 1

        print(f"  [{idx:2d}/{len(all_seeds)} {label}] "
              f"kind={kind:<12s} "
              f"period={result['period']:4d}  disp={result['displacement']}  "
              f"bits={result['final_bit_count']}")

        if kind == "glider" and not glider_found:
            glider_found     = True
            glider_seed_bits = int(label[0])
            glider_period    = result["period"]
            print(f"\n  *** GLIDER FOUND ***")
            print(f"      seed_bits = {glider_seed_bits}")
            print(f"      period    = {glider_period}")
            print(f"      velocity  = {result['displacement']}")
            print(f"      seed      = {seed}\n")

    # Part 3: write result.yaml
    print("\n=== Summary ===")
    print(f"  best_rule_id:       {best_rule_id}")
    print(f"  best_rule_fitness:  {best_fitness:.6f}")
    print(f"  glider_found:       {glider_found}")
    print(f"  seeds_tested:       {len(all_seeds)}")
    print(f"  stable_objects:     {stable_objects}")
    print(f"  decayed_seeds:      {decayed_count}")
    print(f"  counts:             {counts}")

    yaml_result = {
        "best_rule_id":          f"{best_rule_id}.json",
        "best_rule_fitness":     round(best_fitness, 8),
        "glider_found":          bool(glider_found),
        "seeds_tested":          int(len(all_seeds)),
        "stable_objects_found":  int(stable_objects),
        "decayed_seeds_found":   int(decayed_count),
        "glider_seed_bits":      int(glider_seed_bits),
        "glider_period":         int(glider_period),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if glider_found else 1


if __name__ == "__main__":
    sys.exit(main())
