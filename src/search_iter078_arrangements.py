#!/usr/bin/env python3
"""
search_iter078_arrangements.py

Exhaustive search of all distinct symmetric placements of two Seed #7 instances
with a 1-cell gap (minimum hex distance = 2). Reports all arrangements and their
behavior class, highlighting any GLIDERs.

Seed #7: [(0,0), (1,-1), (1,0)]
"""

import json
from itertools import product
from pathlib import Path

RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
STEPS = 500
GROWTH_LIMIT = 10000

HEX_DIRS = [
    ( 1,  0), ( 1, -1), ( 0, -1),
    (-1,  0), (-1,  1), ( 0,  1),
]

SEED7 = frozenset([(0, 0), (1, -1), (1, 0)])


def load_rule():
    with open(RULE_PATH) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


def hex_dist(q1, r1, q2, r2):
    return (abs(q1-q2) + abs(r1-r2) + abs((q1+r1)-(q2+r2))) // 2


def min_dist(cells_a, cells_b):
    return min(hex_dist(qa, ra, qb, rb) for (qa, ra) in cells_a for (qb, rb) in cells_b)


def translate(cells, dq, dr):
    return frozenset((q + dq, r + dr) for q, r in cells)


def neighborhood(cells_set, q, r):
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells, rule):
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


def normalize(cells):
    if not cells:
        return frozenset()
    sq = sorted(cells)
    q0, r0 = sq[0]
    return frozenset((q - q0, r - r0) for q, r in sq)


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def simulate(initial_cells, rule, steps=STEPS):
    current = initial_cells
    shape_to_step = {}
    states = []
    shape_to_step[normalize(current)] = 0
    states.append(current)

    for t in range(1, steps + 1):
        current = step_cells(current, rule)
        bc = len(current)
        if bc == 0:
            return "DECAY", 0, (0, 0), 0, -1
        if bc > GROWTH_LIMIT:
            return "CHAOTIC", bc, (0, 0), 0, -1
        shape = normalize(current)
        if shape in shape_to_step:
            prev_t = shape_to_step[shape]
            period = t - prev_t
            com_prev = center_of_mass(states[prev_t])
            com_now = center_of_mass(current)
            dq = com_now[0] - com_prev[0]
            dr = com_now[1] - com_prev[1]
            is_moving = (abs(dq) > 1e-9 or abs(dr) > 1e-9)
            if period == 1 and not is_moving:
                kind = "STILL_LIFE"
            elif is_moving:
                kind = "GLIDER"
            else:
                kind = "OSCILLATOR"
            return kind, bc, (round(dq, 6), round(dr, 6)), period, prev_t
        shape_to_step[shape] = t
        states.append(current)

    return "NO_CYCLE", len(current), (0, 0), 0, -1


def canonical_composite(sl1, sl2):
    """Return a canonical form of the composite that is translation-invariant."""
    combined = frozenset(sl1) | frozenset(sl2)
    return normalize(combined)


def main():
    rule = load_rule()
    print("Searching all Seed #7 + Seed #7 arrangements with 1-cell gap...\n")
    print(f"Seed #7: {sorted(SEED7)}\n")

    # Try all offsets (dq, dr) in a reasonable range
    seen_composites = set()
    results = []

    for dq, dr in product(range(-6, 7), repeat=2):
        if dq == 0 and dr == 0:
            continue
        sl2 = translate(SEED7, dq, dr)
        if sl2 & SEED7:  # overlap
            continue
        d = min_dist(SEED7, sl2)
        if d != 2:  # not exactly 1-cell gap
            continue

        # Check for duplicates (translation-equivalent composites)
        canon = canonical_composite(SEED7, sl2)
        if canon in seen_composites:
            continue
        seen_composites.add(canon)

        initial = frozenset(SEED7) | sl2
        kind, final_bc, disp, period, cycle_start = simulate(initial, rule)
        results.append({
            "offset": (dq, dr),
            "sl1": sorted(SEED7),
            "sl2": sorted(sl2),
            "kind": kind,
            "final_bc": final_bc,
            "disp": disp,
            "period": period,
            "cycle_start": cycle_start,
        })

    # Print summary
    print(f"Found {len(results)} unique arrangements with 1-cell gap.\n")
    gliders = [r for r in results if r["kind"] == "GLIDER"]
    print(f"Results by class:")
    from collections import Counter
    counts = Counter(r["kind"] for r in results)
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")

    print(f"\nGLIDERS ({len(gliders)}):")
    for r in gliders:
        print(f"  offset={r['offset']}  sl1={r['sl1']}  sl2={r['sl2']}")
        print(f"    period={r['period']}  disp={r['disp']}  final_bc={r['final_bc']}")

    print(f"\nAll results:")
    for r in sorted(results, key=lambda x: (x["kind"], x["offset"])):
        print(f"  [{r['kind']:12s}] offset={r['offset']}  "
              f"period={r['period']:3d}  disp={r['disp']}  bc={r['final_bc']}")


if __name__ == "__main__":
    main()
