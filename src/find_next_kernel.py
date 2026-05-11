#!/usr/bin/env python3
"""
iter_043 Part 1: Find the second valid kernel for the 6-fold symmetric CA.

Searches state-pairs (A, B) with Hamming weight 2 that satisfy:
  1. Center-bit flip: center bit of A != center bit of B
  2. Disjoint orbits: B not in A's rotational orbit
  3. Conflict-free closure: joint 6-rotation closure has exactly 12 unique states

Skips the first valid kernel (A=65, B=6 or any equivalent representative)
and returns the second valid kernel.

Encoding: 7-bit LSB, bit 0 = center, bits 1-6 = neighbors clockwise.
"""
import itertools


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


def is_valid_kernel(A: int, B: int) -> bool:
    if (A & 1) == (B & 1):
        return False
    orb_A = orbit(A)
    if B in orb_A:
        return False
    orb_B = orbit(B)
    closure = orb_A | orb_B
    return len(closure) == 12


def find_kernels(max_find: int = 2):
    states = sorted(s for s in range(128) if bin(s).count("1") == 2)
    found = []
    for A, B in itertools.combinations(states, 2):
        if is_valid_kernel(A, B):
            found.append((A, B))
            if len(found) >= max_find:
                break
    return found


def main():
    kernels = find_kernels(max_find=2)

    if len(kernels) < 2:
        print(f"ERROR: found only {len(kernels)} valid kernel(s), need 2")
        return None

    A1, B1 = kernels[0]
    A2, B2 = kernels[1]

    print(f"First valid kernel  (ignored): A={A1} ('{A1:07b}'), B={B1} ('{B1:07b}')")
    print(f"Second valid kernel (target):  A={A2} ('{A2:07b}'), B={B2} ('{B2:07b}')")
    print()
    print(f"A2={A2}, B2={B2}")
    print(f"center_bit(A2)={A2 & 1}, center_bit(B2)={B2 & 1}")
    print(f"orbit(A2) = {sorted(orbit(A2))}")
    print(f"orbit(B2) = {sorted(orbit(B2))}")
    print(f"closure size = {len(orbit(A2) | orbit(B2))}")
    return A2, B2


if __name__ == "__main__":
    main()
