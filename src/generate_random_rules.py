#!/usr/bin/env python3
"""
generate_random_rules.py

Generates 20 random, reversible, C6-symmetric, non-conserving rules and saves
each to archive/iter_082/rules/random_rule_XX.json.

Neighborhood encoding (7 bits, MSB = center):
  state = center*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
Directions: b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE

60-degree CW rotation: new_b1=old_b6, new_b2=old_b1, ..., new_b6=old_b5
"""

import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RULES_DIR = PROJECT_ROOT / "archive" / "iter_082" / "rules"

NUM_RULES = 20
MAX_ATTEMPTS = 10000


def rotate60(state: int) -> int:
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


def try_build_rule(pairs: list) -> dict | None:
    """Build C6-symmetric involution rule from kernel pairs. Returns None on conflict."""
    rule = {}
    for a, b in pairs:
        for rot in range(6):
            a_rot = apply_n_rotations(a, rot)
            b_rot = apply_n_rotations(b, rot)
            for src, dst in [(a_rot, b_rot), (b_rot, a_rot)]:
                if src in rule:
                    if rule[src] != dst:
                        return None  # conflict
                else:
                    rule[src] = dst
    return rule


def is_nonconserving(pairs: list) -> bool:
    """True if at least one pair changes bit count."""
    return any(bin(a).count('1') != bin(b).count('1') for a, b in pairs)


def generate_random_rule(rng: random.Random) -> tuple[dict, list]:
    """Generate one random rule. Returns (rule_dict, kernel_pairs)."""
    for _ in range(MAX_ATTEMPTS):
        k = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))

        if not is_nonconserving(pairs):
            continue

        rule = try_build_rule(pairs)
        if rule is not None:
            return rule, pairs

    raise RuntimeError("Failed to generate valid rule after many attempts")


def main():
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)

    print(f"Generating {NUM_RULES} random C6-symmetric non-conserving rules...")
    print(f"Saving to: {RULES_DIR}\n")

    for i in range(1, NUM_RULES + 1):
        rule, pairs = generate_random_rule(rng)

        non_identity = [(k, v) for k, v in rule.items() if k != v]
        nc_pairs = [(a, b) for a, b in pairs if bin(a).count('1') != bin(b).count('1')]

        rule_path = RULES_DIR / f"random_rule_{i:02d}.json"
        rule_str = {str(k): v for k, v in rule.items()}
        with open(rule_path, "w") as f:
            json.dump(rule_str, f, sort_keys=True, indent=2)

        print(f"  Rule {i:02d}: pairs={pairs}, "
              f"non-identity mappings={len(non_identity)}, "
              f"nc-pairs={len(nc_pairs)}")

    print(f"\nDone. {NUM_RULES} rules saved.")


if __name__ == "__main__":
    main()
