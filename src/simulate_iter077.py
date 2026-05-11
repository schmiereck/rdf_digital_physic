#!/usr/bin/env python3
"""
simulate_iter077.py

Asymmetric composite still-life interaction under the C6 non-conserving rule (A=3<->B=14).
Two 3-bit still lifes placed in a "stepped" asymmetric configuration.

Still Life 1: (50,50), (51,50), (50,51)
Still Life 2: (51,51), (52,51), (51,52)   <- corner-adjacent, stepped
"""

import json
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_077"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULTS_DIR / "result.yaml"

STEPS = 500
GROWTH_LIMIT = 10000

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
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


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule()

    # Initial condition: two 3-bit still lifes in asymmetric "stepped" configuration
    initial_cells = frozenset([
        (50, 50), (51, 50), (50, 51),  # Still Life 1
        (51, 51), (52, 51), (51, 52),  # Still Life 2 (corner-adjacent, stepped)
    ])

    print(f"\nInitial 6-bit asymmetric composite (stepped):")
    for c in sorted(initial_cells):
        print(f"  {c}")
    print(f"Bit count: {len(initial_cells)}")
    print(f"\nSimulating {STEPS} steps...\n")

    current = initial_cells
    initial_bit_count = len(current)

    # Cycle detection: map normalized shape -> step index
    shape_to_step = {}
    states = []

    shape0 = _normalize(current)
    shape_to_step[shape0] = 0
    states.append(current)

    result_kind = "NO_CYCLE"
    period = 0
    displacement = (0, 0)
    cycle_start = -1
    final_bit_count = initial_bit_count

    for t in range(1, STEPS + 1):
        current = step_cells(current, rule)
        bit_count = len(current)

        if t % 50 == 0:
            print(f"  Step {t:4d}: {bit_count} bits")

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

            print(f"\nCycle detected: period={period}, start={prev_t}, end={t}")
            print(f"  Shape: {result_kind}")
            print(f"  Displacement per period: dq={dq:.6f}, dr={dr:.6f}")
            break

        shape_to_step[shape] = t
        states.append(current)

    else:
        final_bit_count = len(current)
        print(f"\nNo cycle detected after {STEPS} steps")

    print(f"\n=== Results ===")
    print(f"behavior_class:       {result_kind}")
    print(f"initial_bit_count:    {initial_bit_count}")
    print(f"final_bit_count:      {final_bit_count}")
    print(f"object_period:        {period}")
    print(f"net_displacement_hex: {displacement}")
    print(f"is_bit_count_stable:  {initial_bit_count == final_bit_count and result_kind != 'DECAY'}")
    print(f"glider_found:         {result_kind == 'GLIDER'}")

    is_bit_count_stable = (result_kind in ("STILL_LIFE", "OSCILLATOR", "GLIDER"))

    if result_kind == "GLIDER":
        net_dq = round(displacement[0])
        net_dr = round(displacement[1])
    else:
        net_dq = 0
        net_dr = 0

    yaml_result = {
        "glider_found": bool(result_kind == "GLIDER"),
        "behavior_class": result_kind,
        "is_bit_count_stable": bool(is_bit_count_stable),
        "initial_bit_count": int(initial_bit_count),
        "final_bit_count": int(final_bit_count),
        "object_period": int(period),
        "net_displacement_hex": [int(net_dq), int(net_dr)],
        "cycle_start_step": int(cycle_start),
        "displacement_float": list(displacement),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if result_kind == "GLIDER" else 1


if __name__ == "__main__":
    sys.exit(main())
