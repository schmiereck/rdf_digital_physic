#!/usr/bin/env python3
"""
generate_c2_rule.py

Generate the C2-symmetric rule from kernel (A=3, B=14) found in iter_072.

Encoding:
  LSB (for rotation): bit0=center, bits 1-6 = E,SE,SW,W,NW,NE
  MSB (stored in rule): bit6=center, bits 5-0 = E,SE,SW,W,NW,NE

C2 symmetry = 180-degree rotation = 3 steps in the hex neighbor ring.

The rule has exactly 4 non-identity mappings:
  A_MSB      -> B_MSB
  B_MSB      -> A_MSB
  rot(A,3)_MSB -> rot(B,3)_MSB
  rot(B,3)_MSB -> rot(A,3)_MSB
"""

import json
from pathlib import Path

A_LSB = 3    # center + E, popcount=2
B_LSB = 14   # E + SE + SW, popcount=3

RULE_PATH = Path(__file__).parent / "symmetric_rule_c2_A3_B14.json"


def rotate_lsb(state: int, steps: int) -> int:
    center = state & 1
    neighbors = (state >> 1) & 0x3F
    steps = steps % 6
    if steps == 0:
        return state
    rotated = ((neighbors << steps) | (neighbors >> (6 - steps))) & 0x3F
    return center | (rotated << 1)


def lsb_to_msb(state: int) -> int:
    result = 0
    for i in range(7):
        result |= ((state >> i) & 1) << (6 - i)
    return result


def generate_c2_rule() -> dict:
    rule = {i: i for i in range(128)}

    rot_A_lsb = rotate_lsb(A_LSB, 3)
    rot_B_lsb = rotate_lsb(B_LSB, 3)

    A_msb     = lsb_to_msb(A_LSB)
    B_msb     = lsb_to_msb(B_LSB)
    rot_A_msb = lsb_to_msb(rot_A_lsb)
    rot_B_msb = lsb_to_msb(rot_B_lsb)

    c2_set = {A_msb, rot_A_msb, B_msb, rot_B_msb}
    assert len(c2_set) == 4, f"C2 closure must have 4 distinct states, got {len(c2_set)}"

    rule[A_msb]     = B_msb
    rule[B_msb]     = A_msb
    rule[rot_A_msb] = rot_B_msb
    rule[rot_B_msb] = rot_A_msb

    print(f"A:        LSB={A_LSB:3d} ('{A_LSB:07b}'), MSB={A_msb:3d} ('{A_msb:07b}')")
    print(f"rotate(A,3): LSB={rot_A_lsb:3d} ('{rot_A_lsb:07b}'), MSB={rot_A_msb:3d} ('{rot_A_msb:07b}')")
    print(f"B:        LSB={B_LSB:3d} ('{B_LSB:07b}'), MSB={B_msb:3d} ('{B_msb:07b}')")
    print(f"rotate(B,3): LSB={rot_B_lsb:3d} ('{rot_B_lsb:07b}'), MSB={rot_B_msb:3d} ('{rot_B_msb:07b}')")
    print(f"\nNon-identity mappings (MSB):")
    print(f"  {A_msb} -> {B_msb}  (A -> B)")
    print(f"  {B_msb} -> {A_msb}  (B -> A)")
    print(f"  {rot_A_msb} -> {rot_B_msb}  (rot(A,3) -> rot(B,3))")
    print(f"  {rot_B_msb} -> {rot_A_msb}  (rot(B,3) -> rot(A,3))")

    return rule


def main():
    rule = generate_c2_rule()
    json_rule = {str(k): v for k, v in rule.items()}
    with open(RULE_PATH, "w") as f:
        json.dump(json_rule, f, sort_keys=True, indent=2)
    print(f"\nSaved: {RULE_PATH}")


if __name__ == "__main__":
    main()
