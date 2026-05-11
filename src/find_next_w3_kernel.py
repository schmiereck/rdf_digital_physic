#!/usr/bin/env python3
"""
iter_058 Part 1: Find the second valid W=3 contiguous kernel.

Searches state-pairs (A, B) with Hamming weight 3 satisfying all four conditions:
  1. Center-Bit Flip: center bit of A != center bit of B
  2. Disjoint Orbits: B not in A's rotational orbit
  3. Conflict-Free Closure: joint 6-rotation closure has exactly 12 unique states
  4. Contiguity: all '1' bits in both A and B form a single connected cluster

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise (E,SE,SW,W,NW,NE).

The first valid kernel (A=7, B=14) is skipped; the second is reported.
"""
import itertools

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


def is_valid_kernel(A: int, B: int) -> bool:
    if (A & 1) == (B & 1):
        return False
    orb_A = orbit(A)
    if B in orb_A:
        return False
    orb_B = orbit(B)
    return len(orb_A | orb_B) == 12


FIRST_KERNEL = (7, 14)


def find_second_w3_kernel():
    """Return (A2, B2) — the second valid W=3 contiguous kernel — skipping (7,14)."""
    states = sorted(s for s in range(128) if bin(s).count("1") == 3)
    contiguous_states = [s for s in states if is_contiguous(s)]

    found_count = 0
    pairs_checked = 0
    for A, B in itertools.combinations(contiguous_states, 2):
        pairs_checked += 1
        if is_valid_kernel(A, B):
            found_count += 1
            orb_A = orbit(A)
            first_rep = min(orb_A)
            orb_B = orbit(B)
            second_rep = min(orb_B)
            canonical = (min(first_rep, second_rep), max(first_rep, second_rep))
            if canonical == FIRST_KERNEL or (A, B) == FIRST_KERNEL or (B, A) == FIRST_KERNEL:
                print(f"  [skip] first kernel: A={A} ('{A:07b}'), B={B} ('{B:07b}')")
                continue
            return A, B, pairs_checked, found_count

    return None, None, pairs_checked, found_count


def main():
    print("Searching for the second valid W=3 contiguous kernel...")
    A2, B2, pairs_checked, found_count = find_second_w3_kernel()

    if A2 is None:
        print(f"ERROR: no second valid kernel found (pairs_checked={pairs_checked})")
        return None, None

    print(f"\nSecond valid W=3 kernel found:")
    print(f"  A2 = {A2}  binary: '{A2:07b}'")
    print(f"  B2 = {B2}  binary: '{B2:07b}'")
    print(f"  center_bit(A2) = {A2 & 1},  center_bit(B2) = {B2 & 1}")
    print(f"  orbit(A2) = {sorted(orbit(A2))}")
    print(f"  orbit(B2) = {sorted(orbit(B2))}")
    print(f"  closure size = {len(orbit(A2) | orbit(B2))}")
    print(f"  is_contiguous(A2) = {is_contiguous(A2)},  is_contiguous(B2) = {is_contiguous(B2)}")
    print(f"  pairs_checked = {pairs_checked},  valid_kernels_found = {found_count}")

    return A2, B2


if __name__ == "__main__":
    main()
