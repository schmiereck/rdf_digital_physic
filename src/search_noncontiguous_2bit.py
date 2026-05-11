#!/usr/bin/env python3
"""
search_noncontiguous_2bit.py

Systematic search for gliders from 2-bit non-contiguous seeds under the
C6-symmetric non-conserving rule (A=3, B=14).

Tests all 3 unique orientations of distance-2 hexagonal separation:
  orient (2,0), (1,1), (0,2)
"""

import json
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_079"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULT_DIR / "result.yaml"

STEPS = 500
GRID_CENTER = 75
GROWTH_LIMIT = 10000

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]

# The 3 unique distance-2 orientations on a hex grid
DISTANCE2_ORIENTATIONS = [
    (2, 0),
    (1, 1),
    (0, 2),
]


def load_rule() -> dict:
    with open(RULE_PATH) as f:
        raw = json.load(f)
    rule = {int(k): int(v) for k, v in raw.items()}
    non_identity = [(k, v) for k, v in rule.items() if k != v]
    print(f"Loaded rule: {len(rule)} entries, {len(non_identity)} non-identity mappings")
    for k, v in sorted(non_identity):
        print(f"  {k} -> {v}")
    return rule


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


def _normalize(cells):
    """Translate so lex-min cell is at (0,0)."""
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


def test_seed(seed_cells: frozenset, rule: dict, label: str) -> dict:
    """Run one seed and return a result dict."""
    print(f"\n--- Testing {label} ---")
    print(f"  Initial bits: {sorted(seed_cells)}")

    initial_bit_count = len(seed_cells)
    current = seed_cells

    shape_to_step = {}
    states = []

    shape0 = _normalize(current)
    shape_to_step[shape0] = 0
    states.append(current)

    result_kind = "NO_CYCLE"
    period = 0
    displacement = (0.0, 0.0)
    cycle_start = -1
    final_bit_count = initial_bit_count

    for t in range(1, STEPS + 1):
        current = step_cells(current, rule)
        bit_count = len(current)

        if bit_count == 0:
            result_kind = "DECAY"
            final_bit_count = 0
            print(f"  DECAY at step {t}")
            break

        if bit_count > GROWTH_LIMIT:
            result_kind = "CHAOTIC"
            final_bit_count = bit_count
            print(f"  GROWTH exceeded limit at step {t}: {bit_count} bits")
            break

        shape = _normalize(current)
        if shape in shape_to_step:
            prev_t = shape_to_step[shape]
            period = t - prev_t
            cycle_start = prev_t
            final_bit_count = bit_count

            com_prev = center_of_mass(states[prev_t])
            com_now = center_of_mass(current)
            dq = com_now[0] - com_prev[0]
            dr = com_now[1] - com_prev[1]
            displacement = (round(dq, 6), round(dr, 6))

            is_moving = (abs(dq) > 1e-9 or abs(dr) > 1e-9)
            if period == 1 and not is_moving:
                result_kind = "STILL_LIFE"
            elif is_moving:
                result_kind = "GLIDER"
            else:
                result_kind = "OSCILLATOR"

            print(f"  Cycle detected: period={period}, start={prev_t}, end={t}")
            print(f"  Result: {result_kind}")
            print(f"  Displacement per period: dq={dq:.6f}, dr={dr:.6f}")
            break

        shape_to_step[shape] = t
        states.append(current)

    else:
        final_bit_count = len(current)
        print(f"  No cycle after {STEPS} steps: {result_kind}")

    return {
        "label": label,
        "result_kind": result_kind,
        "initial_bit_count": initial_bit_count,
        "final_bit_count": final_bit_count,
        "period": period,
        "cycle_start": cycle_start,
        "displacement": displacement,
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule()

    outcomes = []
    stable_object_count = 0
    glider_found = False

    for dq, dr in DISTANCE2_ORIENTATIONS:
        # Place first bit at grid center, second bit offset by (dq, dr)
        q0, r0 = GRID_CENTER, GRID_CENTER
        seed_cells = frozenset([(q0, r0), (q0 + dq, r0 + dr)])
        label = f"dist=2, orient=({dq},{dr})"

        res = test_seed(seed_cells, rule, label)

        rk = res["result_kind"]
        disp = res["displacement"]
        per = res["period"]

        if rk in ("STILL_LIFE", "OSCILLATOR", "GLIDER"):
            stable_object_count += 1

        if rk == "GLIDER":
            glider_found = True
            outcome_str = (
                f"Seed {label}: GLIDER, period {per}, "
                f"velocity ({disp[0]:.4f}, {disp[1]:.4f})"
            )
        elif rk in ("STILL_LIFE", "OSCILLATOR"):
            outcome_str = f"Seed {label}: {rk}, period {per}"
        else:
            outcome_str = f"Seed {label}: {rk}"

        outcomes.append(outcome_str)
        print(f"  -> {outcome_str}")

    print(f"\n=== Summary ===")
    print(f"glider_found:         {glider_found}")
    print(f"patterns_checked:     {len(DISTANCE2_ORIENTATIONS)}")
    print(f"stable_object_count:  {stable_object_count}")
    for o in outcomes:
        print(f"  {o}")

    yaml_result = {
        "glider_found": bool(glider_found),
        "patterns_checked": len(DISTANCE2_ORIENTATIONS),
        "stable_object_count": int(stable_object_count),
        "outcomes": outcomes,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if glider_found else 1


if __name__ == "__main__":
    sys.exit(main())
