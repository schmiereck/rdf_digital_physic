#!/usr/bin/env python3
"""
iter_044 Part 1: Find the first valid kernel with contiguous bits.

Searches state-pairs (A, B) with Hamming weight 2 that satisfy:
  1. Center-bit flip: center bit of A != center bit of B
  2. Disjoint orbits: B not in A's rotational orbit
  3. Conflict-free closure: joint 6-rotation closure has exactly 12 unique states
  4. Contiguity: for both A and B, the two '1' bits must be in adjacent positions

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise (E,SE,SW,W,NW,NE).
Adjacency: center(0) adjacent to all neighbors; neighbors adjacent in ring: (1,2),(2,3),(3,4),(4,5),(5,6),(6,1).
"""
import itertools

# Adjacent bit-position pairs in LSB encoding (0=center, 1=E, 2=SE, 3=SW, 4=W, 5=NW, 6=NE)
ADJACENT_PAIRS = frozenset([
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),  # center + any neighbor
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (1, 6),   # adjacent neighbors in ring
])


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
    """True if the two set bits in a HW=2 state are at adjacent positions."""
    bits = [i for i in range(7) if (state >> i) & 1]
    if len(bits) != 2:
        return False
    p, q = bits[0], bits[1]
    return (min(p, q), max(p, q)) in ADJACENT_PAIRS or (min(q, p), max(q, p)) in ADJACENT_PAIRS


def is_valid_kernel(A: int, B: int) -> bool:
    if (A & 1) == (B & 1):
        return False
    orb_A = orbit(A)
    if B in orb_A:
        return False
    orb_B = orbit(B)
    closure = orb_A | orb_B
    return len(closure) == 12


def find_contiguous_kernel():
    """Return first (A, B) with HW=2, contiguous bits, satisfying all four conditions."""
    states = sorted(s for s in range(128) if bin(s).count("1") == 2)
    contiguous_states = [s for s in states if is_contiguous(s)]
    for A, B in itertools.combinations(contiguous_states, 2):
        if is_valid_kernel(A, B):
            return A, B
    return None


def main():
    result = find_contiguous_kernel()
    if result is None:
        print("ERROR: no valid contiguous kernel found")
        return None
    A, B = result
    print(f"Found contiguous kernel: A={A} ('{A:07b}'), B={B} ('{B:07b}')")
    print(f"center_bit(A)={A & 1}, center_bit(B)={B & 1}")
    print(f"orbit(A) = {sorted(orbit(A))}")
    print(f"orbit(B) = {sorted(orbit(B))}")
    print(f"closure size = {len(orbit(A) | orbit(B))}")
    print(f"is_contiguous(A)={is_contiguous(A)}, is_contiguous(B)={is_contiguous(B)}")
    return A, B


if __name__ == "__main__":
    main()
