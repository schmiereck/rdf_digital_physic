#!/usr/bin/env python3
"""
simulate_3phase.py

3-phase update schedule for the non-conserving rule (A=3, B=14).
Cell color = (q + 2*r) % 3.
Each full step: Phase 0 (color=0), Phase 1 (color=1), Phase 2 (color=2).
Within each phase, only cells of that color are updated; others keep their state.

Exhaustive search over all 10 one-sided contiguous 4-bit tetrahex seeds.
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_070"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULT_DIR / "result.yaml"

FULL_STEPS = 400
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


def cell_color(q, r) -> int:
    return (q + 2 * r) % 3


def neighborhood(cells_set, q, r) -> int:
    """7-bit MSB neighborhood: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE."""
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def phase_step(cells: frozenset, rule: dict, target_color: int) -> frozenset:
    """Apply one phase: only cells with color == target_color are updated."""
    # Candidates: all target-color cells plus their neighbors that are target-color
    candidates = set()
    for q, r in cells:
        if cell_color(q, r) == target_color:
            candidates.add((q, r))
        for dq, dr in HEX_DIRS:
            nb = (q + dq, r + dr)
            if cell_color(*nb) == target_color:
                candidates.add(nb)

    new_cells = set(cells)  # start from current state
    for q, r in candidates:
        nbr = neighborhood(cells, q, r)
        mapped = rule.get(nbr, nbr)
        new_state = (mapped >> 6) & 1
        if new_state:
            new_cells.add((q, r))
        else:
            new_cells.discard((q, r))

    return frozenset(new_cells)


def full_step(cells: frozenset, rule: dict) -> frozenset:
    """Three-phase full step."""
    cells = phase_step(cells, rule, 0)
    cells = phase_step(cells, rule, 1)
    cells = phase_step(cells, rule, 2)
    return cells


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
    """Return the 10 one-sided tetrahex patterns."""
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


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def test_seed(seed_cells, rule, steps=FULL_STEPS):
    """
    Simulate seed for up to `steps` full steps with 3-phase schedule.
    Detects stable cycles (still life, oscillator, glider).
    """
    current = frozenset(seed_cells)
    canon_to_step = {_normalize(current): 0}
    centers = [center_of_mass(current)]

    for t in range(1, steps + 1):
        current = full_step(current, rule)
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

    seeds = get_all_contiguous_4bit_seeds()
    print(f"Generated {len(seeds)} one-sided tetrahex seeds")
    print(f"Using 3-phase update schedule, {FULL_STEPS} full steps per seed\n")

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
            outcome_str = f"Seed {seed_num:2d} ({name:10s}): NO_CYCLE, {bits} bits after {FULL_STEPS} steps"
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

    details_path = RESULTS_DIR / "all_4bit_3phase_results.yaml"
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
