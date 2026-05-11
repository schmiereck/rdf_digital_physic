#!/usr/bin/env python3
"""
analyze_top_elite_rule.py

Search for gliders under the highest-fitness rule from iter_084 (Gen-2 evolution).
Tests all 11 unique fixed trihex (3-bit) seeds and all 10 unique one-sided tetrahex
(4-bit) seeds.  Stops and reports immediately when the first glider is found.

Seed counts:
  3-bit: 11 fixed trihexes  (canonical under translation only)
  4-bit: 10 one-sided tetrahexes (canonical under C6 rotation)
"""

import csv
import json
import sys
from itertools import combinations
from pathlib import Path

import yaml

PROJECT_ROOT   = Path(__file__).parent.parent
FITNESS_CSV    = PROJECT_ROOT / "archive" / "iter_084" / "results" / "fitness_scores.csv"
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_084" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_085" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_085" / "result.yaml"

STEPS            = 500
MAX_PERIOD_SEARCH = 300
MAX_CELLS        = 500   # treat as "exploded" if pattern grows beyond this

HEX_DIRS = [
    ( 1,  0),   # E  (bit5)
    ( 1, -1),   # SE (bit4)
    ( 0, -1),   # SW (bit3)
    (-1,  0),   # W  (bit2)
    (-1,  1),   # NW (bit1)
    ( 0,  1),   # NE (bit0)
]


# ── Hex transform for rotation-canonical form ────────────────────────────────

def _apply_rotation(q, r, t):
    if t == 0: return ( q,       r      )
    if t == 1: return (-r,       q + r  )
    if t == 2: return (-(q + r), q      )
    if t == 3: return (-q,      -r      )
    if t == 4: return ( r,      -(q + r))
    if t == 5: return ( q + r,  -q      )
    raise ValueError(t)


def _translate_normalize(cells):
    """Canonical form under translation only (lex-min cell → origin)."""
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _rotation_normalize(cells) -> frozenset:
    """Canonical form under all 6 C6 rotations (smallest lexicographic wins)."""
    best = None
    for t in range(6):
        rot  = [_apply_rotation(q, r, t) for q, r in cells]
        norm = _translate_normalize(rot)
        if best is None or sorted(norm) < sorted(best):
            best = norm
    return best


# ── Connectivity check ───────────────────────────────────────────────────────

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


# ── Seed generators ──────────────────────────────────────────────────────────

def get_contiguous_3bit_seeds():
    """Return all 11 fixed trihex seeds (unique under translation only)."""
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
    """Return all 10 one-sided tetrahex seeds (unique under C6 rotation)."""
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


# ── Rule loading ─────────────────────────────────────────────────────────────

def load_rule(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


# ── Sparse-grid simulation ───────────────────────────────────────────────────

def _neighborhood(cells_set, q, r) -> int:
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    """One CA step on an infinite sparse grid.

    For any 7-bit state not in the rule dict the identity mapping is used,
    preserving the center bit unchanged.
    """
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


# ── Glider detection ─────────────────────────────────────────────────────────

def test_seed(seed_cells, rule, steps: int = STEPS) -> dict:
    """
    Simulate seed on an infinite sparse grid for up to `steps` steps.

    Returns:
      kind:           'still_life' | 'oscillator' | 'glider' | 'decayed' | 'exploded' | 'no_cycle'
      stable:         bool
      period:         int  (0 if no cycle detected)
      displacement:   (dq, dr) per period
      final_bit_count int
    """
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


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)

    # --- Part 1: identify top rule ---
    print("Reading fitness scores from iter_084 ...")
    top_rule_id = None
    top_fitness = -1.0
    with open(FITNESS_CSV) as f:
        for row in csv.DictReader(f):
            score = float(row["fitness_score"])
            if score > top_fitness:
                top_fitness  = score
                top_rule_id  = row["rule_id"]

    print(f"Top rule: {top_rule_id}  fitness={top_fitness:,.4f}")

    rule_path = POPULATION_DIR / f"{top_rule_id}.json"
    print(f"Loading rule from {rule_path} ...")
    rule = load_rule(rule_path)
    print(f"  {len(rule)} non-identity entries in rule table")

    # --- Part 2: generate seeds ---
    seeds_3bit = get_contiguous_3bit_seeds()
    seeds_4bit = get_contiguous_4bit_seeds()
    print(f"Seeds generated: {len(seeds_3bit)} trihex (3-bit), "
          f"{len(seeds_4bit)} tetrahex (4-bit), "
          f"total {len(seeds_3bit) + len(seeds_4bit)}")

    # --- Part 3: test seeds ---
    glider_found       = False
    glider_seed_bits   = 0
    glider_period      = 0
    glider_velocity    = (0, 0)
    glider_seed_coords: list = []
    counts: dict = {}

    all_seeds = [("3bit", s) for s in seeds_3bit] + [("4bit", s) for s in seeds_4bit]
    n_checked = 0

    for label, seed in all_seeds:
        result  = test_seed(seed, rule)
        kind    = result["kind"]
        n_checked += 1
        counts[kind] = counts.get(kind, 0) + 1

        print(f"  [{n_checked:2d}/{len(all_seeds)} {label}] "
              f"seed={seed}  kind={kind}  "
              f"period={result['period']}  disp={result['displacement']}  "
              f"bits={result['final_bit_count']}")

        if kind == "glider" and not glider_found:
            glider_found       = True
            glider_seed_bits   = int(label[0])   # '3' or '4'
            glider_period      = result["period"]
            glider_velocity    = result["displacement"]
            glider_seed_coords = [list(c) for c in seed]
            print(f"\n  *** GLIDER FOUND ***")
            print(f"      seed_bits  = {glider_seed_bits}")
            print(f"      period     = {glider_period}")
            print(f"      velocity   = {glider_velocity}")
            print(f"      seed       = {seed}\n")
            break  # stop immediately on first glider

    # Build outcomes summary
    still_lifes = counts.get("still_life", 0)
    oscillators = counts.get("oscillator", 0)
    decayed     = counts.get("decayed", 0)
    exploded    = counts.get("exploded", 0)
    no_cycle    = counts.get("no_cycle", 0)
    gliders     = counts.get("glider", 0)

    if glider_found:
        summary = (
            f"Found 1 glider from {glider_seed_bits}-bit seeds after {n_checked} seeds. "
            f"{still_lifes} still lifes, {oscillators} oscillators, "
            f"{decayed} decayed, {exploded} exploded, {no_cycle} no_cycle."
        )
    else:
        summary = (
            f"No glider found in {n_checked}/{len(all_seeds)} seeds. "
            f"{still_lifes} still lifes, {oscillators} oscillators, "
            f"{decayed} decayed, {exploded} exploded, {no_cycle} no_cycle."
        )

    print("\n=== Summary ===")
    print(f"  top_rule_id:        {top_rule_id}")
    print(f"  top_rule_fitness:   {top_fitness:,.4f}")
    print(f"  glider_found:       {glider_found}")
    if glider_found:
        print(f"  glider_seed_bits:   {glider_seed_bits}")
        print(f"  glider_period:      {glider_period}")
        print(f"  glider_velocity:    {glider_velocity}")
    print(f"  outcome: {summary}")

    yaml_result = {
        "top_rule_id":       top_rule_id,
        "top_rule_fitness":  round(top_fitness, 4),
        "glider_found":      bool(glider_found),
        "glider_seed_bits":  int(glider_seed_bits),
        "glider_period":     int(glider_period),
        "glider_velocity_hex": list(glider_velocity),
        "glider_seed_coords":  glider_seed_coords,
        "outcomes_summary":  summary,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if glider_found else 1


if __name__ == "__main__":
    sys.exit(main())
