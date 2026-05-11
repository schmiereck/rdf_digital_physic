#!/usr/bin/env python3
"""
iter_044 Part 1 / iter_049: Find the first valid kernel with contiguous bits.

Searches state-pairs (A, B) with Hamming weight 3 that satisfy:
  1. Center-bit flip: center bit of A != center bit of B
  2. Disjoint orbits: B not in A's rotational orbit
  3. Conflict-free closure: joint 6-rotation closure has exactly 12 unique states
  4. Contiguity: for both A and B, all '1' bits must form a single connected cluster

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise (E,SE,SW,W,NW,NE).
Adjacency: center(0) adjacent to all neighbors; neighbors adjacent in ring: (1,2),(2,3),(3,4),(4,5),(5,6),(6,1).
"""
import itertools
import os
import yaml

# Adjacent bit-position pairs in LSB encoding (0=center, 1=E, 2=SE, 3=SW, 4=W, 5=NW, 6=NE)
ADJACENT_PAIRS = frozenset([
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),  # center + any neighbor
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (1, 6),   # adjacent neighbors in ring
])

# Build adjacency list for connectivity check
ADJACENCY = {i: set() for i in range(7)}
for p, q in ADJACENT_PAIRS:
    ADJACENCY[p].add(q)
    ADJACENCY[q].add(p)


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
    """True if all set bits form a single connected cluster (BFS over adjacency graph)."""
    bits = [i for i in range(7) if (state >> i) & 1]
    if len(bits) == 0:
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


def is_valid_kernel(A: int, B: int) -> bool:
    if (A & 1) == (B & 1):
        return False
    orb_A = orbit(A)
    if B in orb_A:
        return False
    orb_B = orbit(B)
    closure = orb_A | orb_B
    return len(closure) == 12


def find_contiguous_kernel_w3():
    """Return first (A, B) with HW=3, contiguous bits, satisfying all four conditions."""
    states = sorted(s for s in range(128) if bin(s).count("1") == 3)
    contiguous_states = [s for s in states if is_contiguous(s)]
    pairs_checked = 0
    for A, B in itertools.combinations(contiguous_states, 2):
        pairs_checked += 1
        if is_valid_kernel(A, B):
            return A, B, pairs_checked
    return None, None, pairs_checked


def main():
    A, B, pairs_checked = find_contiguous_kernel_w3()

    result = {
        "valid_kernel_found": A is not None,
        "hamming_weight_searched": 3,
        "pairs_checked": pairs_checked,
        "kernel_A": int(A) if A is not None else None,
        "kernel_B": int(B) if B is not None else None,
        "kernel_A_binary": f"{A:07b}" if A is not None else None,
        "kernel_B_binary": f"{B:07b}" if B is not None else None,
    }

    out_dir = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_049", "results")
    os.makedirs(out_dir, exist_ok=True)
    yaml_path = os.path.join(out_dir, "..", "result.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(result, f, default_flow_style=False)

    if A is None:
        print("ERROR: no valid contiguous W=3 kernel found")
        print(f"pairs_checked: {pairs_checked}")
    else:
        print(f"Found W=3 contiguous kernel: A={A} ('{A:07b}'), B={B} ('{B:07b}')")
        print(f"center_bit(A)={A & 1}, center_bit(B)={B & 1}")
        print(f"orbit(A) = {sorted(orbit(A))}")
        print(f"orbit(B) = {sorted(orbit(B))}")
        print(f"closure size = {len(orbit(A) | orbit(B))}")
        print(f"is_contiguous(A)={is_contiguous(A)}, is_contiguous(B)={is_contiguous(B)}")
        print(f"pairs_checked: {pairs_checked}")
        print(f"Result written to: {os.path.abspath(yaml_path)}")

    return A, B


if __name__ == "__main__":
    main()
