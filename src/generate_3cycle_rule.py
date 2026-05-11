#!/usr/bin/env python3
"""
Generate the 6-fold symmetric 3-cycle rule from the W=3 kernel triplet found in iter_061:
  A = 7  ('0000111' LSB) — center + E + SE
  B = 11 ('0001011' LSB) — center + E + SW
  C = 14 ('0001110' LSB) — E + SE + SW (no center)

The rule implements a 3-cycle: A -> B -> C -> A (and all 6 hexagonal rotations).
18 non-identity mappings total.

LSB encoding: bit 0 = center, bits 1-6 = neighbors clockwise (E, SE, SW, W, NW, NE)
MSB encoding (used in rule dict & simulation): bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE

Saves rule to src/symmetric_rule_w3_3cycle.json.
"""

import json
from pathlib import Path

KERNEL_A_LSB = 7    # 0b0000111: center + E + SE
KERNEL_B_LSB = 11   # 0b0001011: center + E + SW
KERNEL_C_LSB = 14   # 0b0001110: E + SE + SW (no center)

RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_3cycle.json"


def rotate_lsb(state: int, steps: int) -> int:
    """Rotate 7-bit state by steps*60 degrees clockwise (LSB encoding)."""
    center = state & 1
    neighbors = (state >> 1) & 0x3F
    steps = steps % 6
    if steps == 0:
        return state
    rotated = ((neighbors << steps) | (neighbors >> (6 - steps))) & 0x3F
    return center | (rotated << 1)


def lsb_to_msb(state: int) -> int:
    """Convert 7-bit state from LSB to MSB encoding."""
    result = 0
    for i in range(7):
        bit = (state >> i) & 1
        result |= bit << (6 - i)
    return result


def generate_3cycle_rule() -> dict:
    rule = {i: i for i in range(128)}

    A_lsb, B_lsb, C_lsb = KERNEL_A_LSB, KERNEL_B_LSB, KERNEL_C_LSB
    A_msb, B_msb, C_msb = lsb_to_msb(A_lsb), lsb_to_msb(B_lsb), lsb_to_msb(C_lsb)

    print(f"Kernel LSB: A={A_lsb} ('{A_lsb:07b}'), B={B_lsb} ('{B_lsb:07b}'), C={C_lsb} ('{C_lsb:07b}')")
    print(f"Kernel MSB: A={A_msb} ('{A_msb:07b}'), B={B_msb} ('{B_msb:07b}'), C={C_msb} ('{C_msb:07b}')")

    non_identity = 0
    for i in range(6):
        a_rot_lsb = rotate_lsb(A_lsb, i)
        b_rot_lsb = rotate_lsb(B_lsb, i)
        c_rot_lsb = rotate_lsb(C_lsb, i)

        a_rot = lsb_to_msb(a_rot_lsb)
        b_rot = lsb_to_msb(b_rot_lsb)
        c_rot = lsb_to_msb(c_rot_lsb)

        # 3-cycle: A -> B -> C -> A
        rule[a_rot] = b_rot
        rule[b_rot] = c_rot
        rule[c_rot] = a_rot

        print(f"  rot {i}: {a_rot}('{a_rot:07b}') -> {b_rot}('{b_rot:07b}') -> {c_rot}('{c_rot:07b}') -> {a_rot}")
        non_identity += 3

    errors = []
    for src, dst in rule.items():
        if bin(src).count('1') != bin(dst).count('1'):
            errors.append(f"popcount mismatch: {src}({bin(src).count('1')}) -> {dst}({bin(dst).count('1')})")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
    else:
        print(f"Rule verified: bit-conserving, {non_identity} non-identity mappings")

    cycle_errors = []
    for src, dst in rule.items():
        if src == dst:
            continue
        dst2 = rule.get(dst, dst)
        dst3 = rule.get(dst2, dst2)
        if dst3 != src:
            cycle_errors.append(f"not 3-cycle: {src} -> {dst} -> {dst2} -> {dst3}")
    if cycle_errors:
        for e in cycle_errors:
            print(f"ERROR: {e}")
    else:
        print("Rule verified: all non-identity mappings form valid 3-cycles")

    return rule


def main():
    rule = generate_3cycle_rule()
    json_rule = {str(k): v for k, v in rule.items()}
    with open(RULE_PATH, 'w') as f:
        json.dump(json_rule, f, sort_keys=True, indent=2)
    print(f"Saved: {RULE_PATH}")
    return rule


if __name__ == "__main__":
    main()
