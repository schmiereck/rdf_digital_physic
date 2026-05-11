#!/usr/bin/env python3
"""
Generate the 6-fold symmetric rule from the W=3 kernel found in iter_049:
  A = 7  ('0000111' LSB) — center + E + SE
  B = 14 ('0001110' LSB) — E + SE + SW (no center)

Encoding used internally (MSB-center):
  bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE

Saves the rule to src/symmetric_rule_w3_a7_b14.json with string keys.
"""

import json
from pathlib import Path

KERNEL_A_LSB = 7
KERNEL_B_LSB = 14

RULE_PATH = Path(__file__).parent / "symmetric_rule_w3_a7_b14.json"


def lsb_to_msb(state: int) -> int:
    result = 0
    for i in range(7):
        bit = (state >> i) & 1
        result |= bit << (6 - i)
    return result


def rotate60_msb(state: int) -> int:
    """60-degree CW rotation: new_b1=old_b6, new_b2=old_b1, ..., new_b6=old_b5."""
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def generate_w3_rule() -> dict:
    A = lsb_to_msb(KERNEL_A_LSB)
    B = lsb_to_msb(KERNEL_B_LSB)

    print(f"Kernel LSB: A={KERNEL_A_LSB} ('{KERNEL_A_LSB:07b}'), B={KERNEL_B_LSB} ('{KERNEL_B_LSB:07b}')")
    print(f"Kernel MSB: A={A} ('{A:07b}'), B={B} ('{B:07b}')")

    rule = {i: i for i in range(128)}

    a_rot, b_rot = A, B
    for i in range(6):
        rule[a_rot] = b_rot
        rule[b_rot] = a_rot
        print(f"  rot {i*60:3d}deg: {a_rot} ('{a_rot:07b}') <-> {b_rot} ('{b_rot:07b}')")
        a_rot = rotate60_msb(a_rot)
        b_rot = rotate60_msb(b_rot)

    # Verify: bit-conserving involution
    errors = []
    for src, dst in rule.items():
        if bin(src).count("1") != bin(dst).count("1"):
            errors.append(f"popcount mismatch: {src}->{dst}")
        if rule.get(dst) != src:
            errors.append(f"not involution: {src}->{dst}->{rule.get(dst)}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        non_id = sum(1 for k, v in rule.items() if k != v)
        print(f"Rule verified: bit-conserving involution, {non_id} non-identity mappings")

    return rule


def main():
    rule = generate_w3_rule()
    json_rule = {str(k): v for k, v in rule.items()}
    with open(RULE_PATH, "w") as f:
        json.dump(json_rule, f, sort_keys=True, indent=2)
    print(f"Saved: {RULE_PATH}")
    return rule


if __name__ == "__main__":
    main()
