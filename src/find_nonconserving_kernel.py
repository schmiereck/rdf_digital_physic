#!/usr/bin/env python3
"""
iter_065: Find the first valid kernel pair (A, B) where popcount(A)=2, popcount(B)=3.

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise (E,SE,SW,W,NW,NE).

Constraints:
  1. Contiguity: both A and B have connected set-bit patterns on the hex adjacency graph
  2. Center-Bit Flip: center bit of A differs from center bit of B
  3. Disjoint Orbits: orbit(A) and orbit(B) are mutually disjoint
  4. Conflict-Free Closure: |{rotate(A,i), rotate(B,i) for i in 0..5}| == 12
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


def find_nonconserving_kernel():
    states_w2 = sorted(s for s in range(128) if bin(s).count("1") == 2)
    states_w3 = sorted(s for s in range(128) if bin(s).count("1") == 3)

    contiguous_w2 = [s for s in states_w2 if is_contiguous(s)]
    contiguous_w3 = [s for s in states_w3 if is_contiguous(s)]

    print(f"  W=2 states total: {len(states_w2)}, contiguous: {len(contiguous_w2)}")
    print(f"  W=3 states total: {len(states_w3)}, contiguous: {len(contiguous_w3)}")

    pairs_checked = 0
    for A in contiguous_w2:
        orb_A = orbit(A)
        for B in contiguous_w3:
            pairs_checked += 1

            # Constraint 2: center bits must differ
            if (A & 1) == (B & 1):
                continue

            # Constraint 3: orbits must be disjoint
            # (rotation preserves HW so different-HW orbits are always disjoint;
            #  included explicitly for completeness)
            orb_B = orbit(B)
            if orb_A & orb_B:
                continue

            # Constraint 4: joint closure must have exactly 12 unique states
            closure = set()
            for i in range(6):
                closure.add(rotate(A, i))
                closure.add(rotate(B, i))
            if len(closure) != 12:
                continue

            return A, B, pairs_checked

    return None, None, pairs_checked


def main():
    print("Searching for first valid non-conserving kernel (popcount A=2, popcount B=3)...")
    A, B, pairs_checked = find_nonconserving_kernel()

    kernel_found = A is not None

    result = {
        "kernel_found": kernel_found,
        "popcount_A": 2,
        "popcount_B": 3,
        "pairs_checked": pairs_checked,
        "kernel_A": int(A) if kernel_found else None,
        "kernel_B": int(B) if kernel_found else None,
        "kernel_A_binary": f"{A:07b}" if kernel_found else None,
        "kernel_B_binary": f"{B:07b}" if kernel_found else None,
    }

    if kernel_found:
        orb_A = orbit(A)
        orb_B = orbit(B)
        closure = orb_A | orb_B
        print(f"\nFound valid non-conserving kernel:")
        print(f"  A = {A:3d}  binary: '{A:07b}'  center={A & 1}  popcount={bin(A).count('1')}")
        print(f"  B = {B:3d}  binary: '{B:07b}'  center={B & 1}  popcount={bin(B).count('1')}")
        print(f"  orbit(A) size = {len(orb_A)}: {sorted(orb_A)}")
        print(f"  orbit(B) size = {len(orb_B)}: {sorted(orb_B)}")
        print(f"  closure size = {len(closure)}")
        print(f"  disjoint orbits: {len(orb_A & orb_B) == 0}")
        print(f"  contiguous A: {is_contiguous(A)}")
        print(f"  contiguous B: {is_contiguous(B)}")
        print(f"  center flip: {(A & 1) != (B & 1)}")
    else:
        print(f"\nNo valid non-conserving kernel found.")

    print(f"  pairs_checked = {pairs_checked}")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_065")
    os.makedirs(out_dir, exist_ok=True)
    results_dir = os.path.join(out_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    yaml_path = os.path.join(out_dir, "result.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"\nResult written to: {os.path.abspath(yaml_path)}")

    return A, B


if __name__ == "__main__":
    main()
