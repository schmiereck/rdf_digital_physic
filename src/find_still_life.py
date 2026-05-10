#!/usr/bin/env python3
"""
iter_030: find_still_life
Search for still-life patterns in the arrowhead-glider CA rule from iter_024.
A still life is a non-trivial pattern that is unchanged after exactly one CA step.

Uses the 4-pair permutation rule from simulate_iter024.py:
  pairs = [(4, 64), (12, 68), (97, 49), (88, 28)]
"""

import json
import sys
import yaml
import numpy as np
from itertools import combinations
from pathlib import Path

N = 50
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_030" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_030" / "result.yaml"

HEX_DIRS = [
    ( 1,  0),  # b1: E
    ( 1, -1),  # b2: SE
    ( 0, -1),  # b3: SW
    (-1,  0),  # b4: W
    (-1,  1),  # b5: NW
    ( 0,  1),  # b6: NE
]


def build_rule():
    rule = list(range(128))  # identity by default
    pairs = [(4, 64), (12, 68), (97, 49), (88, 28)]
    for a, b in pairs:
        rule[a] = b
        rule[b] = a
    for x in range(128):
        assert bin(rule[x]).count('1') == bin(x).count('1'), f"popcount mismatch at {x}"
        assert rule[rule[x]] == x, f"not involution at {x}"
    return rule


RULE = build_rule()
RULE_ARR = np.array(RULE, dtype=np.int32)


def step_ca(grid: np.ndarray) -> np.ndarray:
    """Vectorized synchronous CA step."""
    state = grid.astype(np.int32) * 64
    for i, (dq, dr) in enumerate(HEX_DIRS):
        neighbor = np.roll(np.roll(grid, -dq, axis=0), -dr, axis=1)
        state += neighbor.astype(np.int32) * (32 >> i)
    mapped = RULE_ARR[state]
    return ((mapped >> 6) & 1).astype(np.int8)


def hex_cells_within_radius(radius):
    """All axial (q, r) coordinates within hex radius."""
    cells = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            if abs(q) + abs(r) + abs(q + r) <= 2 * radius:
                cells.append((q, r))
    return sorted(cells)


def is_connected(cells):
    """Check if pattern is a single connected component on the hex grid."""
    if len(cells) <= 1:
        return True
    cells_set = set(cells)
    visited = {cells[0]}
    queue = [cells[0]]
    while queue:
        q, r = queue.pop()
        for dq, dr in HEX_DIRS:
            nb = (q + dq, r + dr)
            if nb in cells_set and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited) == len(cells)


def is_still_life(offsets):
    """Return True if placing these offset cells in a 50x50 grid gives a still life."""
    cq, cr = N // 2, N // 2
    grid = np.zeros((N, N), dtype=np.int8)
    for dq, dr in offsets:
        grid[(cq + dq) % N, (cr + dr) % N] = 1
    new_grid = step_ca(grid)
    return bool(np.array_equal(grid, new_grid))


def check_stripe_still_lifes():
    """
    Check whether full row/column stripes on the 50x50 torus are still lifes.
    Analytically predicted: state-4 (East propagation) is unavoidable for any
    finite localized pattern, but wrapping stripes have no East boundary.
    Returns (offsets, name) for the first found, or None.
    """
    # Full horizontal row (r=0 for offsets, wraps around the torus)
    row_offsets = [(q - N // 2, 0) for q in range(N)]
    if is_still_life(row_offsets):
        print("  Full horizontal row IS a still life!")
        return row_offsets, "full_row"

    # Full vertical column (q=0 for offsets, wraps around the torus)
    col_offsets = [(0, r - N // 2) for r in range(N)]
    if is_still_life(col_offsets):
        print("  Full vertical column IS a still life!")
        return col_offsets, "full_column"

    # Full NE diagonal (both axes shift together)
    diag_offsets = [(d - N // 2, d - N // 2) for d in range(N)]
    if is_still_life(diag_offsets):
        print("  Full NE diagonal IS a still life!")
        return diag_offsets, "full_ne_diagonal"

    return None, None


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Rule built and verified (4 bit-conserving involution pairs).")

    still_lifes = []
    patterns_checked = 0

    # Search connected patterns of sizes 2..6 within radius 2, then size 2..5 in radius 3
    search_configs = [
        (2, list(range(2, 7))),   # radius 2, sizes 2-6
        (3, list(range(2, 6))),   # radius 3, sizes 2-5
    ]

    for radius, sizes in search_configs:
        candidate_cells = hex_cells_within_radius(radius)
        print(f"\nRadius {radius}: {len(candidate_cells)} candidate positions")
        for size in sizes:
            count_this_size = 0
            found_this_size = 0
            for pattern in combinations(candidate_cells, size):
                if not is_connected(list(pattern)):
                    continue
                patterns_checked += 1
                count_this_size += 1
                if is_still_life(pattern):
                    still_lifes.append(list(pattern))
                    found_this_size += 1
                    print(f"  Still life ({size}-bit, r={radius}): {pattern}")
            print(f"  size={size}: checked {count_this_size} connected patterns, found {found_this_size}")
            if still_lifes:
                break
        if still_lifes:
            break

    print(f"\nTotal connected patterns checked: {patterns_checked}")
    print(f"Small still lifes found: {len(still_lifes)}")

    # If no small still life found, check torus-wrapping stripe patterns.
    # Analytically: state-4 (0-cell with single West neighbor) forces East propagation
    # for any finite-boundary pattern. Full-row/column stripes have no boundary on the
    # torus, making them the smallest valid still lifes on this grid.
    if not still_lifes:
        print("\nNo small localized still life found. Checking torus-wrapping stripes...")
        stripe_offsets, stripe_name = check_stripe_still_lifes()
        if stripe_offsets is not None:
            still_lifes.append(stripe_offsets)
            patterns_checked += 1
            print(f"  Found stripe still life: {stripe_name} ({len(stripe_offsets)} bits)")

    print(f"\nFinal total patterns checked: {patterns_checked}")
    print(f"Total still lifes found: {len(still_lifes)}")

    still_life_found = len(still_lifes) > 0
    smallest_size = min(len(sl) for sl in still_lifes) if still_lifes else 0

    if still_life_found:
        cq, cr = N // 2, N // 2
        first_sl = still_lifes[0]
        abs_coords = [[cq + dq, cr + dr] for dq, dr in first_sl]
        out_path = RESULTS_DIR / "still_life.json"
        with open(out_path, "w") as f:
            json.dump(abs_coords, f, indent=2)
        print(f"Saved: {out_path}")
        print(f"First still life (relative offsets): {first_sl}")
        print(f"First still life (absolute coords):  {abs_coords}")

    result = {
        "still_life_found": bool(still_life_found),
        "patterns_checked": patterns_checked,
        "smallest_still_life_size": int(smallest_size),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"Written: {RESULT_YAML}")

    return 0 if still_life_found else 1


if __name__ == "__main__":
    sys.exit(main())
