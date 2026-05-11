#!/usr/bin/env python3
"""
search_3cycle_objects.py: Search for stable 3-bit objects under the 3-cycle W=3 rule.

Tests all 11 unique contiguous 3-bit hex seeds, simulates each for 200 steps.
Checks bit conservation and cycle detection. Stops at first stable object found.
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_3cycle.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_062" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_062" / "result.yaml"

STEPS = 200

# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
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
    """Return all canonical contiguous 3-cell hex patterns."""
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
    """Compute 7-bit MSB neighborhood value for cell (q, r)."""
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    """One CA step on an infinite sparse grid."""
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


def test_seed(seed_cells, rule, steps=STEPS):
    """
    Simulate seed for up to `steps` steps.

    Returns dict with:
      stable: bool
      period: int (0 if no cycle found)
      displacement: (dq, dr) net displacement per period
      kind: 'STILL_LIFE' | 'OSCILLATOR' | 'GLIDER' | 'unstable' | 'no_cycle'
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

        for prev_t in range(len(shapes)):
            if shapes[prev_t] == shape:
                period = (t + 1) - prev_t
                dq = round(com[0] - centers[prev_t][0])
                dr = round(com[1] - centers[prev_t][1])
                is_moving = (dq != 0 or dr != 0)
                if period == 1:
                    kind = "STILL_LIFE"
                elif is_moving:
                    kind = "GLIDER"
                else:
                    kind = "OSCILLATOR"
                return {"stable": True, "period": period, "displacement": (dq, dr), "kind": kind}

        shapes.append(shape)
        centers.append(com)

    return {"stable": True, "period": 0, "displacement": (0, 0), "kind": "no_cycle"}


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule()
    print(f"Loaded rule: {len(rule)} entries")

    seeds = get_all_contiguous_3bit_seeds()
    print(f"Generated {len(seeds)} unique contiguous 3-bit seed patterns")

    object_found = False
    object_type = None
    object_period = None
    net_displacement = None
    patterns_checked = 0

    for seed in seeds:
        patterns_checked += 1
        res = test_seed(seed, rule)
        kind = res["kind"]

        print(f"  [{patterns_checked:3d}] seed={seed}  kind={kind}  "
              f"period={res['period']}  disp={res['displacement']}")

        if res["stable"] and kind not in ("no_cycle",):
            object_found = True
            object_type = kind
            object_period = res["period"]
            net_displacement = list(res["displacement"])
            print(f"\n*** FOUND: {kind} (period={res['period']}) "
                  f"from seed #{patterns_checked}: {seed} ***")
            break

    if not object_found:
        print(f"\nNo stable object found after checking all {patterns_checked} seeds")

    yaml_result = {
        "kernel_A": 7,
        "kernel_B": 11,
        "kernel_C": 14,
        "object_found": bool(object_found),
        "patterns_checked": int(patterns_checked),
        "object_type": object_type,
        "object_period": int(object_period) if object_period is not None else None,
        "net_displacement": net_displacement,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if object_found else 1


if __name__ == "__main__":
    sys.exit(main())
