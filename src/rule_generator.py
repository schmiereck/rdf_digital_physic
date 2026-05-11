#!/usr/bin/env python3
"""
Rule generator: applies 6-fold rotational symmetry to the arrowhead-glider kernel
to produce a fully symmetric CA rule saved to src/symmetric_rule.json.

Neighborhood encoding (7 bits, MSB = center):
  state = center*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
Directions: b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE

60-degree CW rotation permutation on neighbors: b1->b2, b2->b3, ..., b6->b1
meaning the content of position b1 moves to position b2, so:
  new_b1 = old_b6, new_b2 = old_b1, ..., new_b6 = old_b5
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULE_FILE = Path(__file__).parent / "symmetric_rule.json"

# Kernel pairs for East-moving arrowhead glider (from iter_024)
# Each pair (a, b) means rule[a]=b and rule[b]=a
KERNEL_PAIRS = [
    (4,  64),   # Cell A: 0->1
    (12, 68),   # Cell B: 0->1
    (70, 70),   # Cell C: identity
    (97, 49),   # Cell D: 1->0
    (88, 28),   # Cell E: 1->0
]


def rotate60(state: int) -> int:
    """Rotate a 7-bit neighborhood state by 60 degrees CW.

    Permutation: b1->b2, b2->b3, b3->b4, b4->b5, b5->b6, b6->b1
    In terms of new values: new_b1=old_b6, new_b2=old_b1, ..., new_b6=old_b5
    Center is unchanged.
    """
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    # After 60-deg CW: what was at b6 (NE) is now at b1 (E), etc.
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def apply_n_rotations(state: int, n: int) -> int:
    for _ in range(n):
        state = rotate60(state)
    return state


def generate_symmetric_rule():
    rule = {}
    conflicts = 0

    for rot in range(6):
        for a, b in KERNEL_PAIRS:
            a_rot = apply_n_rotations(a, rot)
            b_rot = apply_n_rotations(b, rot)

            for src, dst in [(a_rot, b_rot), (b_rot, a_rot)]:
                if src in rule:
                    if rule[src] != dst:
                        print(f"  CONFLICT at state {src}: existing={rule[src]}, new={dst} "
                              f"(rotation={rot*60}deg, pair=({a},{b}))")
                        conflicts += 1
                else:
                    rule[src] = dst

    return rule, conflicts


def rotate_neighborhood(state: int) -> int:
    """60-degree CW rotation of a 7-bit neighborhood state (alias for rotate60)."""
    return rotate60(state)


RULE_FILE_A3_B6 = Path(__file__).parent / "symmetric_rule_A3_B6.json"


def generate_rule_A3_B6() -> dict:
    """Generate symmetric rule from kernel pair A=3 ('0000011'), B=6 ('0000110').

    Initializes all 128 states to identity, then applies 6-fold rotational
    closure of (A, B): rule[A_rot]=B_rot and rule[B_rot]=A_rot for each rotation.
    Returns the rule dict (int keys, int values).
    """
    A, B = 3, 6

    rule = {i: i for i in range(128)}

    print(f"Generating symmetric rule A={A} ('{A:07b}'), B={B} ('{B:07b}')")
    print("Rotation mappings:")
    for i in range(6):
        a_rot = apply_n_rotations(A, i)
        b_rot = apply_n_rotations(B, i)
        print(f"  rot={i*60:3d}deg: A_rot={a_rot} ('{a_rot:07b}'), B_rot={b_rot} ('{b_rot:07b}')")
        rule[a_rot] = b_rot
        rule[b_rot] = a_rot

    print("\nFinal explicit overrides (non-identity):")
    for k in sorted(rule):
        if rule[k] != k:
            print(f"  {k} ('{k:07b}') -> {rule[k]} ('{rule[k]:07b}')")

    rule_str = {str(k): v for k, v in rule.items()}
    with open(RULE_FILE_A3_B6, "w") as f:
        json.dump(rule_str, f, indent=2, sort_keys=True)
    print(f"\nRule saved to: {RULE_FILE_A3_B6}")
    return rule


def main():
    print("Generating 6-fold symmetric rule from arrowhead-glider kernel...")
    print(f"Kernel pairs: {KERNEL_PAIRS}")

    rule, conflicts = generate_symmetric_rule()

    print(f"\nConflicts found: {conflicts}")
    print(f"Total mappings:  {len(rule)}")

    # Show all mappings grouped by rotation
    print("\nMappings by rotation:")
    for rot in range(6):
        print(f"  {rot*60:3d} deg:", end="")
        for a, b in KERNEL_PAIRS:
            a_rot = apply_n_rotations(a, rot)
            b_rot = apply_n_rotations(b, rot)
            print(f"  {a_rot}->{b_rot}", end="")
        print()

    # Verify bit conservation and involution
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

    # Save as JSON with string keys (JSON requires string keys)
    rule_str_keys = {str(k): v for k, v in rule.items()}
    with open(RULE_FILE, "w") as f:
        json.dump(rule_str_keys, f, indent=2, sort_keys=True)
    print(f"\nRule saved to: {RULE_FILE}")

    return conflicts, len(rule)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "A3_B6":
        generate_rule_A3_B6()
        sys.exit(0)
    conflicts, total = main()
    sys.exit(0 if conflicts == 0 else 1)
