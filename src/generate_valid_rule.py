#!/usr/bin/env python3
"""
Generate symmetric rule from kernel (A=3, B=6) via hexagonal rotations.

Neighborhood encoding (7 bits, MSB = center):
  state = center*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
Directions: b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE

60° CW rotation maps: E→SE, SE→SW, SW→W, W→NW, NW→NE, NE→E
In bit terms (right-rotate the lower 6 bits by 1):
  new_b1(E)  = old_b6(NE)  [old bit0 → new bit5]
  new_b2(SE) = old_b1(E)   [old bit5 → new bit4]
  ...
  new_b6(NE) = old_b5(NW)  [old bit1 → new bit0]
"""

import json
from pathlib import Path

A = 3   # 0b0000011: b5=NW=1, b6=NE=1
B = 6   # 0b0000110: b4=W=1,  b5=NW=1

RULE_OUT = Path(__file__).parent / "symmetric_rule_A3B6.json"


def rotate(state: int) -> int:
    """One step 60° CW rotation of the 6 neighbor bits; center bit unchanged."""
    center = state & 0x40
    nb = state & 0x3F
    rotated = ((nb >> 1) | ((nb & 1) << 5)) & 0x3F
    return center | rotated


def main():
    rule = {i: i for i in range(128)}

    a_rot, b_rot = A, B
    for _ in range(6):
        rule[a_rot] = b_rot
        rule[b_rot] = a_rot
        a_rot = rotate(a_rot)
        b_rot = rotate(b_rot)

    non_id = {k: v for k, v in rule.items() if k != v}
    print(f"Non-identity mappings ({len(non_id)}):")
    for k, v in sorted(non_id.items()):
        print(f"  {k:3d} ({k:07b}) -> {v:3d} ({v:07b})")

    out = {str(k): v for k, v in sorted(rule.items())}
    with open(RULE_OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved rule ({len(rule)} entries) to {RULE_OUT}")


if __name__ == "__main__":
    main()
