#!/usr/bin/env python3
"""
search_iter078_gap_sizes.py

Search all arrangements of two Seed #7 instances with gap sizes 1, 2, 3
to find any that produce gliders.
"""

import json
from itertools import product
from pathlib import Path
from collections import Counter

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


def search_gap(rule, seed, gap_size, search_range=8):
    seen = set()
    results = []
    for dq, dr in product(range(-search_range, search_range+1), repeat=2):
        if dq == 0 and dr == 0:
            continue
        sl2 = translate(seed, dq, dr)
        if sl2 & seed:
            continue
        d = min_dist(seed, sl2)
        if d != gap_size + 1:
            continue
        combined = frozenset(seed) | sl2
        canon = normalize(combined)
        if canon in seen:
            continue
        seen.add(canon)

        kind, final_bc, disp, period, cycle_start = simulate(combined, rule)
        results.append({
            "offset": (dq, dr),
            "kind": kind,
            "final_bc": final_bc,
            "disp": disp,
            "period": period,
            "sl2": sorted(sl2),
        })
    return results


def main():
    rule = load_rule()
    print(f"Seed #7: {sorted(SEED7)}")
    print(f"(Compact triangle: all 3 cells mutually adjacent)\n")

    for gap in [1, 2, 3]:
        results = search_gap(rule, SEED7, gap)
        counts = Counter(r["kind"] for r in results)
        gliders = [r for r in results if r["kind"] == "GLIDER"]
        print(f"=== Gap size {gap} ({len(results)} unique arrangements) ===")
        for k, v in sorted(counts.items()):
            print(f"  {k}: {v}")
        if gliders:
            print(f"  GLIDERS FOUND:")
            for r in gliders:
                print(f"    offset={r['offset']}  sl2={r['sl2']}")
                print(f"    period={r['period']}  disp={r['disp']}  bc={r['final_bc']}")
        print()


if __name__ == "__main__":
    main()
