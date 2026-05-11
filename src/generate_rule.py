#!/usr/bin/env python3
"""
Generate a 6-fold symmetric CA rule from a kernel pair (A, B) and save to
src/symmetric_rule_next.json.

Encoding used (MSB = center, same as simulate_hex.py and rule_generator.py):
  state = center*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
Directions: b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE

The second valid kernel from find_center_flipping_kernel.py is A=3, B=10
in LSB encoding (bit0=center). Converting to MSB encoding:
  LSB A=3  (c=1, b1=1)          -> MSB A=96  (1100000)
  LSB B=10 (c=0, b1=1, b3=1)   -> MSB B=40  (0101000)
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_FILE = Path(__file__).parent / "symmetric_rule_next.json"

# Second valid kernel in MSB encoding (derived from LSB A=3, B=10)
A_MSB = 96   # 1100000: center=1, b1(E)=1
B_MSB = 40   # 0101000: center=0, b1(E)=1, b3(SW)=1


def rotate60(state: int) -> int:
    """60-degree CW rotation of a 7-bit neighborhood state (MSB=center).

    Permutation: b1->b2, b2->b3, b3->b4, b4->b5, b5->b6, b6->b1
    Equivalently: new_b1=old_b6, new_b2=old_b1, ..., new_b6=old_b5
    """
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def apply_n_rotations(state: int, n: int) -> int:
    for _ in range(n):
        state = rotate60(state)
    return state


def generate_rule(A: int, B: int) -> dict:
    """Generate a 6-fold symmetric rule from kernel pair (A, B).

    Starts with identity for all 128 states, then applies rule[A_rot]=B_rot
    and rule[B_rot]=A_rot for each of the 6 rotations.
    """
    rule = {i: i for i in range(128)}

    print(f"Generating symmetric rule: A={A} ({A:07b}), B={B} ({B:07b})")
    print("Rotation mappings:")
    for i in range(6):
        a_rot = apply_n_rotations(A, i)
        b_rot = apply_n_rotations(B, i)
        print(f"  rot={i*60:3d}deg: {a_rot} ({a_rot:07b}) <-> {b_rot} ({b_rot:07b})")
        rule[a_rot] = b_rot
        rule[b_rot] = a_rot

    print("\nNon-identity mappings:")
    for k in sorted(rule):
        if rule[k] != k:
            print(f"  {k} ({k:07b}) -> {rule[k]} ({rule[k]:07b})")

    errors = []
    for src, dst in rule.items():
        if bin(src).count('1') != bin(dst).count('1'):
            errors.append(f"popcount mismatch: {src}->{dst}")
        if rule.get(dst) != src:
            errors.append(f"not involution: {src}->{dst}->{rule.get(dst)}")
    if errors:
        print("\nVerification ERRORS:")
        for e in errors:
            print(f"  {e}")
    else:
        print("\nVerification passed: bit-conserving and involution.")

    return rule


def main():
    rule = generate_rule(A_MSB, B_MSB)
    rule_str = {str(k): v for k, v in rule.items()}
    with open(RULE_FILE, "w") as f:
        json.dump(rule_str, f, indent=2, sort_keys=True)
    print(f"\nRule saved to: {RULE_FILE}")


if __name__ == "__main__":
    main()
