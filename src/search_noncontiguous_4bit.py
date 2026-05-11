#!/usr/bin/env python3
"""
search_noncontiguous_4bit.py

Systematic search for gliders from 4-bit non-contiguous seeds under the
C6-symmetric non-conserving rule (A=3, B=14).

Generates all unique 4-bit non-contiguous seeds within hex-radius 3 (37 cells),
reduces to rotational+translational canonical forms, and tests each for up to
500 steps.
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_081"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULT_DIR / "result.yaml"

STEPS = 500
GROWTH_LIMIT = 1000

HEX_DIRS = [
    ( 1,  0),   # E  (bit5)
    ( 1, -1),   # SE (bit4)
    ( 0, -1),   # SW (bit3)
    (-1,  0),   # W  (bit2)
    (-1,  1),   # NW (bit1)
    ( 0,  1),   # NE (bit0)
]


def hex_distance(q, r):
    return (abs(q) + abs(r) + abs(q + r)) // 2


def get_hex_grid(radius):
    cells = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            if hex_distance(q, r) <= radius:
                cells.append((q, r))
    return cells


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


def all_rotations(cells):
    """All 6 rotations (0°, 60°, ..., 300°) using (q,r) -> (-r, q+r)."""
    current = list(cells)
    result = [list(current)]
    for _ in range(5):
        current = [(-r, q + r) for q, r in current]
        result.append(list(current))
    return result


def canonical_form(cells) -> tuple:
    """Rotational + translational canonical form (lex-min over all rotations)."""
    best = None
    for rot in all_rotations(cells):
        sorted_r = sorted(rot)
        q0, r0 = sorted_r[0]
        translated = tuple((q - q0, r - r0) for q, r in sorted_r)
        if best is None or translated < best:
            best = translated
    return best


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


def normalize_translation(cells) -> frozenset:
    sorted_cells = sorted(cells)
    if not sorted_cells:
        return frozenset()
    q0, r0 = sorted_cells[0]
    return frozenset((q - q0, r - r0) for q, r in sorted_cells)


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def test_seed(seed_cells: frozenset, rule: dict) -> dict:
    current = seed_cells

    shape_to_step = {}
    centers = []

    shape0 = normalize_translation(current)
    shape_to_step[shape0] = 0
    centers.append(center_of_mass(current))

    for t in range(1, STEPS + 1):
        current = step_cells(current, rule)
        bit_count = len(current)

        if bit_count == 0:
            return {"result_kind": "DECAY", "period": 0,
                    "displacement": (0.0, 0.0), "final_bit_count": 0}

        if bit_count > GROWTH_LIMIT:
            return {"result_kind": "CHAOTIC", "period": 0,
                    "displacement": (0.0, 0.0), "final_bit_count": bit_count}

        shape = normalize_translation(current)
        com = center_of_mass(current)

        if shape in shape_to_step:
            prev_t = shape_to_step[shape]
            period = t - prev_t
            dq = com[0] - centers[prev_t][0]
            dr = com[1] - centers[prev_t][1]
            displacement = (round(dq, 6), round(dr, 6))
            is_moving = (abs(dq) > 1e-9 or abs(dr) > 1e-9)
            if period == 1 and not is_moving:
                result_kind = "STILL_LIFE"
            elif is_moving:
                result_kind = "GLIDER"
            else:
                result_kind = "OSCILLATOR"
            return {"result_kind": result_kind, "period": period,
                    "displacement": displacement, "final_bit_count": bit_count}

        shape_to_step[shape] = t
        centers.append(com)

    return {"result_kind": "NO_CYCLE", "period": 0,
            "displacement": (0.0, 0.0), "final_bit_count": len(current)}


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RULE_PATH) as f:
        raw = json.load(f)
    rule = {int(k): int(v) for k, v in raw.items()}
    non_identity = [(k, v) for k, v in rule.items() if k != v]
    print(f"Loaded rule: {len(rule)} entries, {len(non_identity)} non-identity mappings")
    for k, v in sorted(non_identity):
        print(f"  {k} -> {v}")

    # 37-cell diamond = hex-radius 3
    grid = get_hex_grid(3)
    print(f"\nGrid size: {len(grid)} cells (hex-radius 3)")

    all_combos = list(combinations(grid, 4))
    print(f"Total 4-cell combinations: {len(all_combos)}")

    seen_canonical = set()
    unique_seeds = []
    contiguous_count = 0

    for combo in all_combos:
        if is_connected(combo):
            contiguous_count += 1
            continue
        cf = canonical_form(combo)
        if cf not in seen_canonical:
            seen_canonical.add(cf)
            unique_seeds.append(frozenset(cf))

    print(f"Contiguous combinations filtered out: {contiguous_count}")
    print(f"Unique non-contiguous seeds (rot+trans canonical): {len(unique_seeds)}")
    print(f"\nSimulating each for up to {STEPS} steps...\n")

    outcomes = []
    stable_object_count = 0
    glider_found = False
    first_glider_seed = None
    first_glider_period = None
    first_glider_velocity = None

    for i, seed in enumerate(unique_seeds, 1):
        if i % 500 == 0:
            print(f"  [{i}/{len(unique_seeds)}] stable={stable_object_count}, glider={glider_found}")

        res = test_seed(seed, rule)
        rk = res["result_kind"]
        per = res["period"]
        disp = res["displacement"]
        bits = res["final_bit_count"]

        if rk in ("STILL_LIFE", "OSCILLATOR", "GLIDER"):
            stable_object_count += 1

        if rk == "GLIDER":
            glider_found = True
            first_glider_seed = sorted(seed)
            first_glider_period = per
            first_glider_velocity = (disp[0], disp[1])
            outcome_str = (
                f"Seed #{i}: GLIDER, period {per}, "
                f"velocity ({disp[0]:.4f}, {disp[1]:.4f}), bits={bits}"
            )
            outcomes.append(outcome_str)
            print(f"\nGLIDER FOUND at seed #{i}!")
            print(f"  Cells: {sorted(seed)}")
            print(f"  Period: {per}")
            print(f"  Displacement per period: dq={disp[0]:.6f}, dr={disp[1]:.6f}")
            print(f"  Final bit count: {bits}")
            break  # Stop immediately on first glider
        elif rk in ("STILL_LIFE", "OSCILLATOR"):
            outcome_str = f"Seed #{i}: {rk}, period={per}, bits={bits}"
            print(f"  Seed #{i}: {rk}, period={per}")
        else:
            outcome_str = f"Seed #{i}: {rk}"

        outcomes.append(outcome_str)

    patterns_checked = len(outcomes)

    print(f"\n=== Summary ===")
    print(f"glider_found:         {glider_found}")
    print(f"patterns_checked:     {patterns_checked}")
    print(f"total_unique_seeds:   {len(unique_seeds)}")
    print(f"stable_object_count:  {stable_object_count}")
    if glider_found:
        print(f"glider_seed_coords:   {first_glider_seed}")
        print(f"glider_period:        {first_glider_period}")
        print(f"glider_velocity_hex:  {first_glider_velocity}")
    print("Last outcomes:")
    for o in outcomes[-20:]:
        print(f"  {o}")

    yaml_result = {
        "glider_found": bool(glider_found),
        "patterns_checked": patterns_checked,
        "total_unique_seeds": len(unique_seeds),
        "stable_object_count": int(stable_object_count),
        "glider_seed_coords": [list(c) for c in first_glider_seed] if first_glider_seed else None,
        "glider_period": int(first_glider_period) if first_glider_period is not None else None,
        "glider_velocity_hex": list(first_glider_velocity) if first_glider_velocity is not None else None,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if glider_found else 1


if __name__ == "__main__":
    sys.exit(main())
