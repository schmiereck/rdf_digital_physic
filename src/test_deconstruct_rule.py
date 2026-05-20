#!/usr/bin/env python3
"""
Test: Load champion rule, extract generator pairs, rebuild via _try_build_c2_rule,
and verify the rebuilt rule_dict is exactly identical to the original.
"""

import json
import sys
import os

# Ensure we can import from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.evolution import _try_build_c2_rule, _rotate_c2


def extract_generator_pairs(rule_dict: dict) -> list:
    """
    Extract the minimal set of generator pairs from a C2-symmetric rule_dict.

    For each entry (src, dst) the generator pair (a, b) = (src, dst) produces
    up to four C2-symmetric mappings:
        (a, b), (b, a), (rot180(a), rot180(b)), (rot180(b), rot180(a))

    We greedily pick an unprocessed entry, compute its full C2 orbit, remove
    all orbit members from the pool, and record the pair.
    """
    # Work with integer keys for rotation logic
    remaining = {(int(k), v) for k, v in rule_dict.items()}
    pairs: list = []

    while remaining:
        # Pick the first unprocessed entry as the generator pair representative
        a, b = next(iter(remaining))

        # Compute the C2-rotated counterparts
        rot_a = _rotate_c2(a)
        rot_b = _rotate_c2(b)

        # All four entries that a single (a, b) pair generates
        orbit_entries = [
            (a, b),
            (b, a),
            (rot_a, rot_b),
            (rot_b, rot_a),
        ]

        # Remove every orbit member that happens to be in the rule_dict
        for entry in orbit_entries:
            remaining.discard(entry)

        pairs.append((a, b))

    return pairs


def main():
    # ── 1. Load the champion rule ──────────────────────────────────────────────
    champion_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "archive",
        "iter_179",
        "results",
        "champion_rule.json",
    )

    with open(champion_path, "r") as f:
        champion = json.load(f)

    original_rule_dict = champion["rule_dict"]

    print("Original rule_dict ({} entries):".format(len(original_rule_dict)))
    for k, v in sorted(original_rule_dict.items(), key=lambda x: int(x[0])):
        print("  {} -> {}".format(k, v))

    # ── 2. Extract generator pairs ────────────────────────────────────────────
    pairs = extract_generator_pairs(original_rule_dict)

    print("\nExtracted {} generator pairs:".format(len(pairs)))
    for a, b in pairs:
        print("  ({}, {})".format(a, b))

    # ── 3. Rebuild the rule using _try_build_c2_rule ──────────────────────────
    rebuilt_rule_dict = _try_build_c2_rule(pairs)

    if rebuilt_rule_dict is None:
        print("\nERROR: _try_build_c2_rule returned None — pairs are inconsistent!")
        return

    print("\nRebuilt rule_dict ({} entries):".format(len(rebuilt_rule_dict)))
    for k, v in sorted(rebuilt_rule_dict.items(), key=lambda x: x[0]):
        print("  {} -> {}".format(k, v))

    # ── 4. Verify exact identity ──────────────────────────────────────────────
    # Build an integer-keyed dict from the original for comparison
    original_int = {int(k): v for k, v in original_rule_dict.items()}

    keys_match = set(original_int.keys()) == set(rebuilt_rule_dict.keys())
    values_match = all(
        original_int[k] == rebuilt_rule_dict[k] for k in original_int
    ) if keys_match else False

    identical = keys_match and values_match

    if not identical:
        print("\nDifferences found:")
        for k in set(original_int.keys()) | set(rebuilt_rule_dict.keys()):
            o = original_int.get(k, "<missing>")
            r = rebuilt_rule_dict.get(k, "<missing>")
            if o != r:
                print("  key {}: original={}  rebuilt={}".format(k, o, r))

    print("\n" + "=" * 55)
    print(
        "Verification: {} — rule_dicts are {}.".format(
            "PASS" if identical else "FAIL",
            "identical" if identical else "DIFFERENT",
        )
    )
    print("=" * 55)


if __name__ == "__main__":
    main()
