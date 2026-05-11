#!/usr/bin/env python3
"""
search_stable_nonconserving_objects.py

Systematically search for stable objects under the non-conserving rule (A=3, B=14).
Tests all unique contiguous 2-bit seeds (dihexes), then 3-bit seeds (trihexes),
stopping as soon as the first stable object is found.

Coordinates: hex axial (q, r).
MSB neighborhood encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR = PROJECT_ROOT / "archive" / "iter_067"
RESULTS_DIR = RESULT_DIR / "results"
RESULT_YAML = RESULT_DIR / "result.yaml"

STEPS = 300
GROWTH_LIMIT = 1000

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


def canonical_form(cells) -> tuple:
    """Translate so lex-min cell is at (0,0); returns sorted tuple of (q,r) pairs."""
    cells_list = sorted(cells)
    q0, r0 = cells_list[0]
    return tuple((q - q0, r - r0) for q, r in cells_list)


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def get_contiguous_seeds(n_bits: int) -> list:
    """Return all canonically unique contiguous n-bit hex patterns (translation-only normalization)."""
    r = n_bits + 1
    all_cells = [(q, c) for q in range(-r, r + 1) for c in range(-r, r + 1)]

    seen = set()
    seeds = []
    for combo in combinations(all_cells, n_bits):
        if not is_connected(combo):
            continue
        cf = canonical_form(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(list(cf))

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

    Cycle detection uses canonical form (translation-normalized shape), so gliders
    are also detected. Returns dict with keys: stable, period, displacement, kind,
    final_bit_count.
    """
    current = frozenset(seed_cells)

    cf0 = canonical_form(current)
    canon_to_step = {cf0: 0}
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

        cf = canonical_form(current)
        com = center_of_mass(current)

        if cf in canon_to_step:
            prev_t = canon_to_step[cf]
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

        canon_to_step[cf] = t
        centers.append(com)

    return {"stable": False, "period": 0, "displacement": (0, 0),
            "kind": "NO_CYCLE", "final_bit_count": len(current)}


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule = load_rule()
    print(f"Loaded rule: {len(rule)} entries from {RULE_PATH.name}")

    object_found = False
    found_result = None
    found_seed = None
    found_seed_bit_count = None
    patterns_checked = 0

    for n_bits in [2, 3]:
        seeds = get_contiguous_seeds(n_bits)
        print(f"\n--- Stage {n_bits}: {n_bits}-bit seeds ({len(seeds)} unique patterns) ---")

        for seed in seeds:
            patterns_checked += 1
            res = test_seed(seed, rule)
            kind = res["kind"]

            print(f"  [{patterns_checked:3d}] seed={seed}  kind={kind}  "
                  f"period={res['period']}  bits={res['final_bit_count']}  "
                  f"disp={res['displacement']}")

            if res["stable"] and kind != "NO_CYCLE":
                object_found = True
                found_result = res
                found_seed = seed
                found_seed_bit_count = n_bits
                print(f"\n*** FOUND: {kind} (period={res['period']}) "
                      f"from seed #{patterns_checked}: {seed} ***")
                break

        if object_found:
            break

    if not object_found:
        print(f"\nNo stable object found after checking all {patterns_checked} seeds")

    if object_found:
        disp = list(found_result["displacement"])
    else:
        disp = [0, 0]

    yaml_result = {
        "object_found": bool(object_found),
        "seed_bit_count": int(found_seed_bit_count) if found_seed_bit_count is not None else None,
        "patterns_checked": int(patterns_checked),
        "behavior_class": found_result["kind"] if object_found else None,
        "object_period": int(found_result["period"]) if object_found else None,
        "final_bit_count": int(found_result["final_bit_count"]) if object_found else None,
        "net_displacement": disp,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if object_found else 1


if __name__ == "__main__":
    sys.exit(main())
