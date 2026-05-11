#!/usr/bin/env python3
"""
find_w3_glider.py: Search for moving objects (gliders) in the W=3 symmetric rule (A=7, B=14).

Tests all 11 unique contiguous 3-bit hex seeds on an infinite grid and classifies each
stable object as still life, oscillator, or glider based on center-of-mass displacement.
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_a7_b14.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_052" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_052" / "result.yaml"

STEPS = 200
MAX_PERIOD_SEARCH = 60

HEX_DIRS = [
    ( 1,  0),   # E  (bit5)
    ( 1, -1),   # SE (bit4)
    ( 0, -1),   # SW (bit3)
    (-1,  0),   # W  (bit2)
    (-1,  1),   # NW (bit1)
    ( 0,  1),   # NE (bit0)
]


def load_rule() -> dict:
    with open(RULE_PATH) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


def is_connected(cells) -> bool:
    cells_set = set(cells)
    start = next(iter(cells_set))
    visited = {start}
    queue = [start]
    while queue:
        q, r = queue.pop()
        for dq, dr in HEX_DIRS:
            nb = (q + dq, r + dr)
            if nb in cells_set and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited) == len(cells_set)


def canonical_form(cells) -> frozenset:
    """Translate cell set so lex-min cell is at (0,0)."""
    cells_list = sorted(cells)
    q0, r0 = cells_list[0]
    return frozenset((q - q0, r - r0) for q, r in cells_list)


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def get_all_contiguous_3bit_seeds():
    """Return list of all canonical 3-cell connected hex patterns (each as sorted list)."""
    coord_range = range(-3, 4)
    all_cells = [(q, r) for q in coord_range for r in coord_range]

    seen = set()
    seeds = []
    for combo in combinations(all_cells, 3):
        if not is_connected(combo):
            continue
        cf = canonical_form(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(sorted(cf))

    return seeds


def neighborhood(cells_set, q, r) -> int:
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    """One CA step using sparse infinite-grid representation."""
    candidates = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            candidates.add((q + dq, r + dr))

    new_cells = set()
    for q, r in candidates:
        nbr = neighborhood(cells, q, r)
        mapped = rule.get(nbr, nbr)
        if (mapped >> 6) & 1:
            new_cells.add((q, r))

    return frozenset(new_cells)


def test_seed_for_glider(seed_cells, rule, steps=STEPS):
    """
    Simulate seed for up to `steps` steps on an infinite grid.

    Returns dict with:
      stable: bool — bit count stayed 3 throughout
      period: int  — detected period (0 if none found)
      displacement: (dq, dr) — integer net displacement per period (or (0,0))
      kind: 'still_life' | 'oscillator' | 'glider' | 'unstable' | 'no_cycle'
    """
    current = frozenset(seed_cells)
    shapes = [canonical_form(current)]
    centers = [center_of_mass(current)]

    for t in range(steps):
        current = step_cells(current, rule)
        if len(current) != 3:
            return {"stable": False, "period": 0, "displacement": (0, 0), "kind": "unstable"}

        shape = canonical_form(current)
        com = center_of_mass(current)

        # Check if this shape appeared before (search last MAX_PERIOD_SEARCH steps)
        search_start = max(0, len(shapes) - MAX_PERIOD_SEARCH)
        for prev_t in range(search_start, len(shapes)):
            if shapes[prev_t] == shape:
                period = (t + 1) - prev_t
                # Displacement from prev_t to t+1 (one full cycle)
                dq_raw = com[0] - centers[prev_t][0]
                dr_raw = com[1] - centers[prev_t][1]
                dq = round(dq_raw)
                dr = round(dr_raw)
                is_moving = (dq != 0 or dr != 0)
                # Velocity per step (exact floats for sanity check)
                if period == 1:
                    kind = "still_life"
                elif is_moving:
                    kind = "glider"
                else:
                    kind = "oscillator"
                return {
                    "stable": True,
                    "period": period,
                    "displacement": (dq, dr),
                    "kind": kind,
                    "glider_velocity_per_step": (dq_raw / period, dr_raw / period),
                }

        shapes.append(shape)
        centers.append(com)

    return {"stable": True, "period": 0, "displacement": (0, 0), "kind": "no_cycle"}


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "archive" / "iter_052").mkdir(parents=True, exist_ok=True)

    rule = load_rule()
    print(f"Loaded rule: {len(rule)} entries")

    seeds = get_all_contiguous_3bit_seeds()
    print(f"Generated {len(seeds)} unique contiguous 3-bit seed patterns")

    glider_found = False
    glider_period = 0
    glider_velocity_hex = (0, 0)
    glider_seed_coords = []
    stable_still_lifes = 0
    stable_oscillators = 0
    patterns_checked = 0

    for seed in seeds:
        patterns_checked += 1
        result = test_seed_for_glider(seed, rule)
        kind = result["kind"]

        print(f"  [{patterns_checked:3d}] seed={seed}  kind={kind}  "
              f"period={result['period']}  displacement={result['displacement']}")

        if kind == "still_life":
            stable_still_lifes += 1
        elif kind == "oscillator":
            stable_oscillators += 1
        elif kind == "glider":
            glider_found = True
            glider_period = result["period"]
            glider_velocity_hex = result["displacement"]
            glider_seed_coords = [list(c) for c in seed]
            print(f"  *** GLIDER FOUND *** period={glider_period}  "
                  f"velocity={glider_velocity_hex}  seed={seed}")

    print(f"\n=== Summary ===")
    print(f"patterns_checked:         {patterns_checked}")
    print(f"stable_still_lifes_found: {stable_still_lifes}")
    print(f"stable_oscillators_found: {stable_oscillators}")
    print(f"glider_found:             {glider_found}")
    if glider_found:
        print(f"glider_period:            {glider_period}")
        print(f"glider_velocity_hex:      {glider_velocity_hex}")
        print(f"glider_seed_coords:       {glider_seed_coords}")

    yaml_result = {
        "glider_found": bool(glider_found),
        "patterns_checked": int(patterns_checked),
        "stable_still_lifes_found": int(stable_still_lifes),
        "stable_oscillators_found": int(stable_oscillators),
        "glider_period": int(glider_period),
        "glider_velocity_hex": list(glider_velocity_hex),
        "glider_seed_coords": glider_seed_coords,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if glider_found else 1


if __name__ == "__main__":
    sys.exit(main())
