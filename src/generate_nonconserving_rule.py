#!/usr/bin/env python3
"""
Generate the non-conserving 2-cycle rule from kernel (A=3, B=14) found in iter_065.

Encoding:
  LSB (for rotation): bit0=center, bits 1-6 = E,SE,SW,W,NW,NE
  MSB (stored in rule): bit6=center, bits 5-0 = E,SE,SW,W,NW,NE

A=3  ('0000011' LSB): center + E, popcount=2
B=14 ('0001110' LSB): E + SE + SW, popcount=3

Rule: A_rot <-> B_rot for all 6 rotations → 12 non-identity mappings.
Non-conserving because popcount(A) != popcount(B).
"""

import json
from pathlib import Path

A_LSB = 3    # center + E, popcount=2
B_LSB = 14   # E + SE + SW, popcount=3

RULE_PATH = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"


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


def generate_nonconserving_rule() -> dict:
    rule = {i: i for i in range(128)}

    A_msb = lsb_to_msb(A_LSB)
    B_msb = lsb_to_msb(B_LSB)
    print(f"A: LSB={A_LSB} ('{A_LSB:07b}'), MSB={A_msb} ('{A_msb:07b}') pc={bin(A_LSB).count('1')}")
    print(f"B: LSB={B_LSB} ('{B_LSB:07b}'), MSB={B_msb} ('{B_msb:07b}') pc={bin(B_LSB).count('1')}")

    non_identity = 0
    for i in range(6):
        a_lsb = rotate_lsb(A_LSB, i)
        b_lsb = rotate_lsb(B_LSB, i)
        a_msb = lsb_to_msb(a_lsb)
        b_msb = lsb_to_msb(b_lsb)

        rule[a_msb] = b_msb
        rule[b_msb] = a_msb
        non_identity += 2

        print(f"  rot {i}: {a_msb:3d}('{a_msb:07b}') <-> {b_msb:3d}('{b_msb:07b}')")

    print(f"Total non-identity mappings: {non_identity}")
    return rule


def main():
    rule = generate_nonconserving_rule()
    json_rule = {str(k): v for k, v in rule.items()}
    with open(RULE_PATH, "w") as f:
        json.dump(json_rule, f, sort_keys=True, indent=2)
    print(f"Saved: {RULE_PATH}")


if __name__ == "__main__":
    main()
