#!/usr/bin/env python3
"""
search_c2_gliders_4bit.py

Exhaustive search for moving 4-bit objects under the C2-symmetric rule (A=3, B=14).
Tests all 10 unique one-sided contiguous 4-bit patterns (tetrahexes).

Coordinates: hex axial (q, r).
MSB neighborhood encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_c2_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_073"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULT_DIR / "result.yaml"

STEPS = 400
GROWTH_LIMIT = 2000

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


def _apply_rotation(q, r, t):
    if t == 0: return ( q,       r      )
    if t == 1: return (-r,       q + r  )
    if t == 2: return (-(q + r), q      )
    if t == 3: return (-q,      -r      )
    if t == 4: return ( r,      -(q + r))
    if t == 5: return ( q + r,  -q      )
    raise ValueError(f"Unknown rotation {t}")


def _normalize(cells):
    sorted_cells = sorted(cells)
    q0, r0 = sorted_cells[0]
    return frozenset((q - q0, r - r0) for q, r in sorted_cells)


def canonical_form_rotational(cells) -> frozenset:
    best = None
    for t in range(6):
        transformed = [_apply_rotation(q, r, t) for q, r in cells]
        normalized = _normalize(transformed)
        if best is None or sorted(normalized) < sorted(best):
            best = normalized
    return best


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


def get_all_contiguous_4bit_seeds():
    """Return the 10 one-sided tetrahex patterns (rotation-canonical, no reflections)."""
    coord_range = range(-4, 5)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen = set()
    seeds = []
    for combo in combinations(all_cells, 4):
        if not is_connected(combo):
            continue
        cf = canonical_form_rotational(combo)
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


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def test_seed(seed_cells, rule, steps=STEPS):
    """
    Simulate seed for up to `steps` steps, detecting stable cycles.

    Cycle detection uses canonical (translation-normalized) shape, so gliders
    (moving patterns with repeating shape) are detected.

    Returns dict with keys:
      stable: bool
      period: int
      displacement: (dq, dr)
      kind: DECAY | GROWTH | STILL_LIFE | OSCILLATOR | GLIDER | NO_CYCLE
      final_bit_count: int
    """
    current = frozenset(seed_cells)
    canon_to_step = {_normalize(current): 0}
    centers = [center_of_mass(current)]

    for t in range(1, steps + 1):
        current = step_cells(current, rule)
        bit_count = len(current)

        if bit_count == 0:
            return {"stable": False, "period": 0, "displacement": (0, 0),
                    "kind": "DECAY", "final_bit_count": 0}

        if bit_count > GROWTH_LIMIT:
            return {"stable": False, "period": 0, "displacement": (0, 0),
                    "kind": "GROWTH", "final_bit_count": bit_count}

        shape = _normalize(current)
        com = center_of_mass(current)

        if shape in canon_to_step:
            prev_t = canon_to_step[shape]
            period = t - prev_t
            dq = round(com[0] - centers[prev_t][0])
            dr = round(com[1] - centers[prev_t][1])
            is_moving = (dq != 0 or dr != 0)
            if period == 1 and not is_moving:
                kind = "STILL_LIFE"
            elif is_moving:
                kind = "GLIDER"
            else:
                kind = "OSCILLATOR"
            return {"stable": True, "period": period, "displacement": (dq, dr),
                    "kind": kind, "final_bit_count": bit_count}

        canon_to_step[shape] = t
        centers.append(com)

    return {"stable": False, "period": 0, "displacement": (0, 0),
            "kind": "NO_CYCLE", "final_bit_count": len(current)}


SEED_NAMES = [
    "straight", "L-shape", "T-shape", "S-shape", "Y-shape",
    "zigzag", "hook", "arch", "fan", "bent"
]


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule()
    print(f"Loaded rule: {len(rule)} entries from {RULE_PATH.name}")

    non_identity = sum(1 for k, v in rule.items() if k != v)
    print(f"Non-identity mappings: {non_identity}")

    seeds = get_all_contiguous_4bit_seeds()
    print(f"Generated {len(seeds)} one-sided tetrahex seeds")
    print(f"Simulating {STEPS} steps per seed\n")

    glider_found = False
    glider_period = 0
    glider_velocity = [0, 0]
    stable_object_count = 0
    decayed_seed_count = 0
    outcomes = []
    all_results = []

    for idx, seed in enumerate(seeds):
        seed_num = idx + 1
        name = SEED_NAMES[idx] if idx < len(SEED_NAMES) else f"shape_{seed_num}"
        res = test_seed(seed, rule)
        kind = res["kind"]
        bits = res["final_bit_count"]
        period = res["period"]
        disp = res["displacement"]

        if kind == "DECAY":
            decayed_seed_count += 1
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): DECAY"
        elif kind == "GROWTH":
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): GROWTH, {bits} bits"
        elif kind == "NO_CYCLE":
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): NO_CYCLE, {bits} bits after {STEPS} steps"
        elif kind == "STILL_LIFE":
            stable_object_count += 1
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): STILL_LIFE, {bits} bits, period {period}"
        elif kind == "OSCILLATOR":
            stable_object_count += 1
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): OSCILLATOR, {bits} bits, period {period}"
        elif kind == "GLIDER":
            stable_object_count += 1
            outcome_str = (f"Seed {seed_num:2d} ({name:10s}): GLIDER, {bits} bits, "
                           f"period {period}, displacement {disp}")
            if not glider_found:
                glider_found = True
                glider_period = period
                glider_velocity = list(disp)
        else:
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): {kind}"

        outcomes.append(outcome_str)
        print(f"  {outcome_str}")

        all_results.append({
            "seed_num": seed_num,
            "name": name,
            "seed": [list(c) for c in seed],
            "kind": kind,
            "period": period,
            "displacement": list(disp),
            "final_bit_count": bits,
        })

    print(f"\n=== Summary ===")
    print(f"patterns_checked:    {len(seeds)}")
    print(f"stable_object_count: {stable_object_count}")
    print(f"decayed_seed_count:  {decayed_seed_count}")
    print(f"glider_found:        {glider_found}")
    if glider_found:
        print(f"glider_period:       {glider_period}")
        print(f"glider_velocity_hex: {glider_velocity}")

    details_path = RESULTS_DIR / "all_4bit_c2_results.yaml"
    with open(details_path, "w") as f:
        yaml.dump(all_results, f, default_flow_style=False, sort_keys=False)
    print(f"Written: {details_path}")

    yaml_result = {
        "glider_found": bool(glider_found),
        "patterns_checked": int(len(seeds)),
        "stable_object_count": int(stable_object_count),
        "decayed_seed_count": int(decayed_seed_count),
        "glider_period": int(glider_period),
        "glider_velocity_hex": glider_velocity,
        "outcomes": outcomes,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Written: {RESULT_YAML}")

    return 0 if glider_found else 1


if __name__ == "__main__":
    sys.exit(main())
