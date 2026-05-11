#!/usr/bin/env python3
"""
iter_072: Find a valid C2-symmetric kernel pair (A, B) where popcount(A)=2, popcount(B)=3.

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise (E,SE,SW,W,NW,NE).
C2 symmetry = 180-degree rotation = 3 steps in the hex neighbor ring.

Constraints:
  1. Contiguity: both A and B have connected set-bit patterns
  2. Center-Bit Flip: center bit of A != center bit of B
  3. Conflict-Free C2 Closure: {A, rotate(A,3), B, rotate(B,3)} are all 4 distinct states,
     i.e. A != rotate(A,3), B != rotate(B,3), A != rotate(B,3)
"""
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


def find_c2_kernel():
    states_w2 = sorted(s for s in range(128) if bin(s).count("1") == 2)
    states_w3 = sorted(s for s in range(128) if bin(s).count("1") == 3)

    contiguous_w2 = [s for s in states_w2 if is_contiguous(s)]
    contiguous_w3 = [s for s in states_w3 if is_contiguous(s)]

    print(f"  W=2 states total: {len(states_w2)}, contiguous: {len(contiguous_w2)}")
    print(f"  W=3 states total: {len(states_w3)}, contiguous: {len(contiguous_w3)}")

    pairs_checked = 0
    for A in contiguous_w2:
        rot_A = rotate(A, 3)
        # Constraint 3a: A must not be its own 180-degree rotation
        if A == rot_A:
            continue
        for B in contiguous_w3:
            pairs_checked += 1

            # Constraint 2: center bits must differ
            if (A & 1) == (B & 1):
                continue

            rot_B = rotate(B, 3)
            # Constraint 3b: B must not be its own 180-degree rotation
            if B == rot_B:
                continue

            # Constraint 3c: A must not be the 180-degree rotation of B
            if A == rot_B:
                continue

            return A, B, pairs_checked

    return None, None, pairs_checked


def main():
    print("Searching for first valid C2-symmetric kernel (popcount A=2, popcount B=3)...")
    A, B, pairs_checked = find_c2_kernel()

    kernel_found = A is not None

    result = {
        "kernel_found": kernel_found,
        "pairs_checked": pairs_checked,
        "kernel_A": int(A) if kernel_found else None,
        "kernel_B": int(B) if kernel_found else None,
        "kernel_A_binary": f"{A:07b}" if kernel_found else None,
        "kernel_B_binary": f"{B:07b}" if kernel_found else None,
    }

    if kernel_found:
        rot_A = rotate(A, 3)
        rot_B = rotate(B, 3)
        c2_closure = {A, rot_A, B, rot_B}
        print(f"\nFound valid C2-symmetric kernel:")
        print(f"  A         = {A:3d}  binary: '{A:07b}'  center={A & 1}")
        print(f"  rotate(A,3) = {rot_A:3d}  binary: '{rot_A:07b}'  center={rot_A & 1}")
        print(f"  B         = {B:3d}  binary: '{B:07b}'  center={B & 1}")
        print(f"  rotate(B,3) = {rot_B:3d}  binary: '{rot_B:07b}'  center={rot_B & 1}")
        print(f"  C2 closure size = {len(c2_closure)} (must be 4)")
        print(f"  contiguous A: {is_contiguous(A)}, contiguous B: {is_contiguous(B)}")
        print(f"  center flip: {(A & 1) != (B & 1)}")
    else:
        print(f"\nNo valid C2-symmetric kernel found.")

    print(f"  pairs_checked = {pairs_checked}")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_072")
    os.makedirs(out_dir, exist_ok=True)
    results_dir = os.path.join(out_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    yaml_path = os.path.join(out_dir, "result.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"\nResult written to: {os.path.abspath(yaml_path)}")


if __name__ == "__main__":
    main()
