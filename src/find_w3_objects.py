#!/usr/bin/env python3
"""
find_w3_objects.py: Combinatorial search for stable 3-bit objects under the W=3 rule.

Generates all unique contiguous 3-cell hex seeds, simulates each for 20 steps,
and reports the first stable (bit-conserving + periodic) object found.
"""

import json
import sys
import yaml
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_a7_b14.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_051" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_051" / "result.yaml"

STEPS = 20

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


def get_all_contiguous_3bit_seeds():
    """Return list of canonical 3-cell connected hex patterns (each as sorted list)."""
    coord_range = range(-2, 3)
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
    """One CA step using sparse representation on an effectively infinite grid."""
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


def test_seed(seed_cells, rule, steps=20):
    """
    Simulate seed for up to `steps` steps.
    Returns (found: bool, period: int).
    found=True if bit-count stays 3 and pattern state repeats.
    """
    current = frozenset(seed_cells)
    history = [canonical_form(current)]

    for t in range(steps):
        current = step_cells(current, rule)
        if len(current) != 3:
            return False, 0

        shape = canonical_form(current)
        for prev_t, prev_shape in enumerate(history):
            if shape == prev_shape:
                return True, (t + 1) - prev_t

        history.append(shape)

    return False, 0


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "archive" / "iter_051").mkdir(parents=True, exist_ok=True)

    rule = load_rule()
    print(f"Loaded rule: {len(rule)} entries")

    seeds = get_all_contiguous_3bit_seeds()
    print(f"Generated {len(seeds)} unique contiguous 3-bit seed patterns")

    object_found = False
    object_type = None
    object_period = None
    initial_seed_coords = None
    patterns_checked = 0

    for seed in seeds:
        patterns_checked += 1
        found, period = test_seed(seed, rule, steps=STEPS)

        if found:
            object_found = True
            object_period = period
            object_type = "STILL_LIFE" if period == 1 else "OSCILLATOR"
            initial_seed_coords = [list(c) for c in seed]
            print(f"FOUND: {object_type} (period={period}) from seed #{patterns_checked}: {seed}")
            break

        print(f"  [{patterns_checked:3d}] seed={seed} -> unstable")

    if not object_found:
        print(f"\nNo stable object found after {patterns_checked} seeds")

    result = {
        "object_found": bool(object_found),
        "patterns_checked": int(patterns_checked),
        "object_type": object_type,
        "object_period": int(object_period) if object_period is not None else None,
        "initial_seed_coords": initial_seed_coords,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if object_found else 1


if __name__ == "__main__":
    sys.exit(main())
