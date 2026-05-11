#!/usr/bin/env python3
"""
iter_061: Find the first valid W=3 3-cycle kernel triplet (A, B, C).

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise (E,SE,SW,W,NW,NE).

Constraints:
  1. Contiguity: all 3 states have connected set-bit patterns on the hex adjacency graph
  2. Center-Bit Flip: center bits of A, B, C are not all identical
  3. Disjoint Orbits: orbit(A), orbit(B), orbit(C) are pairwise disjoint
  4. Conflict-Free Closure: |orbit(A) union orbit(B) union orbit(C)| == 18
"""
import itertools
import os
import yaml

ADJACENT_PAIRS = frozenset([
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (1, 6),
])

ADJACENCY = {i: set() for i in range(7)}
for _p, _q in ADJACENT_PAIRS:
    ADJACENCY[_p].add(_q)
    ADJACENCY[_q].add(_p)


def rotate(state: int, steps: int) -> int:
    center = state & 1
    neighbors = (state >> 1) & 0x3F
    steps = steps % 6
    if steps == 0:
        return state
    rotated = ((neighbors << steps) | (neighbors >> (6 - steps))) & 0x3F
    return center | (rotated << 1)


def orbit(state: int) -> frozenset:
    return frozenset(rotate(state, i) for i in range(6))


def is_contiguous(state: int) -> bool:
    bits = [i for i in range(7) if (state >> i) & 1]
    if not bits:
        return True
    visited = {bits[0]}
    queue = [bits[0]]
    bit_set = set(bits)
    while queue:
        node = queue.pop()
        for neighbor in ADJACENCY[node]:
            if neighbor in bit_set and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited == bit_set


def find_w3_cycle_kernel():
    states = sorted(s for s in range(128) if bin(s).count("1") == 3)
    contiguous = [s for s in states if is_contiguous(s)]

    print(f"  Total W=3 states: {len(states)}")
    print(f"  Contiguous W=3 states: {len(contiguous)}")

    triplets_checked = 0
    for A, B, C in itertools.combinations(contiguous, 3):
        triplets_checked += 1

        # Constraint 2: center bits must not all be equal
        if (A & 1) == (B & 1) == (C & 1):
            continue

        # Compute orbits once
        orb_A = orbit(A)
        orb_B = orbit(B)

        # Constraint 3a: orbit(A) and orbit(B) disjoint
        if orb_A & orb_B:
            continue

        orb_C = orbit(C)

        # Constraint 3b/3c: orbit(C) disjoint from both
        if orb_A & orb_C:
            continue
        if orb_B & orb_C:
            continue

        # Constraint 4: joint closure must have exactly 18 unique states
        if len(orb_A | orb_B | orb_C) != 18:
            continue

        return A, B, C, triplets_checked

    return None, None, None, triplets_checked


def main():
    print("Searching for first valid W=3 3-cycle kernel (A, B, C)...")
    A, B, C, triplets_checked = find_w3_cycle_kernel()

    kernel_found = A is not None

    result = {
        "kernel_found": kernel_found,
        "hamming_weight_searched": 3,
        "triplets_checked": triplets_checked,
        "kernel_A": int(A) if kernel_found else None,
        "kernel_B": int(B) if kernel_found else None,
        "kernel_C": int(C) if kernel_found else None,
        "kernel_A_binary": f"{A:07b}" if kernel_found else None,
        "kernel_B_binary": f"{B:07b}" if kernel_found else None,
        "kernel_C_binary": f"{C:07b}" if kernel_found else None,
    }

    if kernel_found:
        orb_A = orbit(A)
        orb_B = orbit(B)
        orb_C = orbit(C)
        closure = orb_A | orb_B | orb_C
        print(f"\nFound valid W=3 3-cycle kernel:")
        print(f"  A = {A:3d}  binary: '{A:07b}'  center={A & 1}")
        print(f"  B = {B:3d}  binary: '{B:07b}'  center={B & 1}")
        print(f"  C = {C:3d}  binary: '{C:07b}'  center={C & 1}")
        print(f"  orbit(A) = {sorted(orb_A)}")
        print(f"  orbit(B) = {sorted(orb_B)}")
        print(f"  orbit(C) = {sorted(orb_C)}")
        print(f"  closure size = {len(closure)}")
        print(f"  triplets_checked = {triplets_checked}")
    else:
        print(f"\nNo valid 3-cycle kernel found. triplets_checked = {triplets_checked}")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_061")
    os.makedirs(out_dir, exist_ok=True)
    yaml_path = os.path.join(out_dir, "result.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"\nResult written to: {os.path.abspath(yaml_path)}")

    return A, B, C


if __name__ == "__main__":
    main()
