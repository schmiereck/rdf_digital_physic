#!/usr/bin/env python3
"""
iter_058 Part 2: Generate the 6-fold symmetric rule for the second W=3 kernel
and search all unique contiguous 3-bit seeds for stable objects.

Encoding:
  LSB (kernel search): bit0=center, bits1-6=E,SE,SW,W,NW,NE clockwise
  MSB (rule / CA):     bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE

Steps:
  1. Import second kernel (A2, B2) from find_next_w3_kernel.
  2. Convert to MSB encoding and generate the 6-fold rule.
  3. Save rule to src/symmetric_rule_w3_next.json.
  4. Test all 11 unique contiguous 3-bit seeds for up to 200 steps.
  5. Stop at first stable (bit-conserving + periodic) object.
  6. Write archive/iter_058/result.yaml.
"""

import json
import sys
import math
import yaml
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from find_next_w3_kernel import find_second_w3_kernel, orbit as lsb_orbit

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_next.json"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_058" / "result.yaml"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_058" / "results"

STEPS = 200
MAX_PERIOD_SEARCH = 100

# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
HEX_DIRS = [
    ( 1,  0),   # E  (bit5)
    ( 1, -1),   # SE (bit4)
    ( 0, -1),   # SW (bit3)
    (-1,  0),   # W  (bit2)
    (-1,  1),   # NW (bit1)
    ( 0,  1),   # NE (bit0)
]


# ── Encoding conversion ────────────────────────────────────────────────────────

def lsb_to_msb(state: int) -> int:
    """Reverse bit order: LSB bit-i → MSB bit-(6-i)."""
    result = 0
    for i in range(7):
        result |= ((state >> i) & 1) << (6 - i)
    return result


def rotate60_msb(state: int) -> int:
    """60-degree CW rotation in MSB encoding."""
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


# ── Rule generation ────────────────────────────────────────────────────────────

def generate_rule(kernel_A_lsb: int, kernel_B_lsb: int) -> dict:
    A = lsb_to_msb(kernel_A_lsb)
    B = lsb_to_msb(kernel_B_lsb)
    print(f"Kernel LSB: A={kernel_A_lsb} ('{kernel_A_lsb:07b}'), B={kernel_B_lsb} ('{kernel_B_lsb:07b}')")
    print(f"Kernel MSB: A={A} ('{A:07b}'), B={B} ('{B:07b}')")

    rule = {i: i for i in range(128)}
    a_rot, b_rot = A, B
    for i in range(6):
        rule[a_rot] = b_rot
        rule[b_rot] = a_rot
        print(f"  rot {i*60:3d}deg: {a_rot} ('{a_rot:07b}') <-> {b_rot} ('{b_rot:07b}')")
        a_rot = rotate60_msb(a_rot)
        b_rot = rotate60_msb(b_rot)

    errors = []
    for src, dst in rule.items():
        if bin(src).count("1") != bin(dst).count("1"):
            errors.append(f"popcount mismatch: {src}->{dst}")
        if rule.get(dst) != src:
            errors.append(f"not involution: {src}->{dst}->{rule.get(dst)}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        non_id = sum(1 for k, v in rule.items() if k != v)
        print(f"Rule verified: bit-conserving involution, {non_id} non-identity mappings")

    return rule


# ── CA simulation (infinite sparse grid, MSB encoding) ────────────────────────

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
    cells_list = sorted(cells)
    q0, r0 = cells_list[0]
    return frozenset((q - q0, r - r0) for q, r in cells_list)


def center_of_mass(cells):
    n = len(cells)
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def get_all_contiguous_3bit_seeds():
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


def test_seed(seed_cells, rule, steps=STEPS):
    """
    Simulate for up to `steps` steps on an infinite grid.
    Returns dict: stable, period, displacement (dq,dr), kind.
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

        search_start = max(0, len(shapes) - MAX_PERIOD_SEARCH)
        for prev_t in range(search_start, len(shapes)):
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
                return {
                    "stable": True,
                    "period": period,
                    "displacement": (dq, dr),
                    "kind": kind,
                }

        shapes.append(shape)
        centers.append(com)

    return {"stable": False, "period": 0, "displacement": (0, 0), "kind": "no_cycle"}


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Part 1: get the second kernel
    print("=== Part 1: Finding second W=3 kernel ===")
    A2_lsb, B2_lsb, pairs_checked, _ = find_second_w3_kernel()
    if A2_lsb is None:
        print("ERROR: could not find second kernel")
        return 1

    # Part 2: generate rule
    print("\n=== Part 2: Generating rule ===")
    rule = generate_rule(A2_lsb, B2_lsb)
    json_rule = {str(k): v for k, v in rule.items()}
    with open(RULE_PATH, "w") as f:
        json.dump(json_rule, f, sort_keys=True, indent=2)
    print(f"Saved rule: {RULE_PATH}")

    # Part 3: search seeds
    print("\n=== Part 3: Searching 3-bit seeds ===")
    seeds = get_all_contiguous_3bit_seeds()
    print(f"Generated {len(seeds)} unique contiguous 3-bit seeds")

    object_found = False
    object_type = None
    object_period = None
    net_displacement = 0
    patterns_checked = 0

    for seed in seeds:
        patterns_checked += 1
        result = test_seed(seed, rule)
        kind = result["kind"]
        print(f"  [{patterns_checked:3d}] seed={seed}  kind={kind}  "
              f"period={result['period']}  displacement={result['displacement']}")

        if result["stable"] and result["period"] > 0:
            object_found = True
            object_type = kind
            object_period = result["period"]
            dq, dr = result["displacement"]
            net_displacement = math.sqrt(dq**2 + dr**2)
            print(f"  *** FOUND: {kind} period={object_period} displacement={result['displacement']} ***")
            break

    print(f"\n=== Summary ===")
    print(f"kernel_A:          {A2_lsb}")
    print(f"kernel_B:          {B2_lsb}")
    print(f"object_found:      {object_found}")
    print(f"patterns_checked:  {patterns_checked}")
    print(f"object_type:       {object_type}")
    print(f"object_period:     {object_period}")
    print(f"net_displacement:  {net_displacement}")

    yaml_result = {
        "kernel_A": int(A2_lsb),
        "kernel_B": int(B2_lsb),
        "object_found": bool(object_found),
        "patterns_checked": int(patterns_checked),
        "object_type": object_type,
        "object_period": int(object_period) if object_period is not None else None,
        "net_displacement": float(net_displacement),
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=True)
    print(f"\nWritten: {RESULT_YAML}")

    return 0 if object_found else 1


if __name__ == "__main__":
    sys.exit(main())
