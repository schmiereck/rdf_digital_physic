"""
iter_015: existence-2D-hex
Analyze 2D hexagonal lattice (7-cell neighborhood, 1 bit/cell) rule space.
"""

import math
from collections import defaultdict


def hamming_weight(state: int, bits: int = 7) -> int:
    return bin(state).count('1')


def build_hamming_groups(bits: int = 7) -> dict[int, list[int]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for state in range(2 ** bits):
        w = hamming_weight(state, bits)
        groups[w].append(state)
    return dict(groups)


def construct_swap_rule(groups: dict[int, list[int]], bits: int = 7) -> dict[int, int]:
    # Start with identity
    rule = {s: s for s in range(2 ** bits)}

    # Pick W=1 group, swap first two states
    w1 = sorted(groups[1])
    a, b = w1[0], w1[1]
    rule[a] = b
    rule[b] = a

    return rule


def validate_rule(rule: dict[int, int], bits: int = 7) -> tuple[bool, bool, bool]:
    n = 2 ** bits
    states = list(range(n))

    # Non-trivial: at least one state maps to a different state
    non_trivial = any(rule[s] != s for s in states)

    # Reversible: bijective (injective => surjective for finite sets)
    reversible = len(set(rule.values())) == n

    # Bit-conserving: hamming weight preserved
    bit_conserving = all(hamming_weight(rule[s]) == hamming_weight(s) for s in states)

    return non_trivial, reversible, bit_conserving


def main():
    import os
    import yaml

    bits = 7
    state_space_size = 2 ** bits

    groups = build_hamming_groups(bits)
    rule = construct_swap_rule(groups, bits)
    non_trivial, reversible, bit_conserving = validate_rule(rule, bits)

    rule_found = non_trivial and reversible and bit_conserving

    hamming_group_sizes = {f"W{w}": len(groups[w]) for w in range(bits + 1)}
    total = sum(hamming_group_sizes.values())

    print(f"State space size: {state_space_size}")
    print(f"Hamming group sizes: {hamming_group_sizes}")
    print(f"Sum of group sizes: {total}")
    print(f"Non-trivial: {non_trivial}")
    print(f"Reversible: {reversible}")
    print(f"Bit-conserving: {bit_conserving}")
    print(f"Rule found: {rule_found}")

    # Verify binomial coefficients
    for w in range(bits + 1):
        expected = math.comb(bits, w)
        actual = hamming_group_sizes[f"W{w}"]
        assert actual == expected, f"W{w}: expected {expected}, got {actual}"
    print("Binomial coefficient check: PASSED")

    # Write result
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'archive', 'iter_015')
    os.makedirs(out_dir, exist_ok=True)

    result = {
        'state_space_size': state_space_size,
        'rule_found': rule_found,
        'hamming_group_sizes': hamming_group_sizes,
        'validation': {
            'non_trivial': non_trivial,
            'reversible': reversible,
            'bit_conserving': bit_conserving,
        },
        'swapped_states': {
            'a': bin(sorted(groups[1])[0]),
            'b': bin(sorted(groups[1])[1]),
        },
    }

    out_path = os.path.join(out_dir, 'result.yaml')
    with open(out_path, 'w') as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)

    print(f"Result written to: {out_path}")
    return result


if __name__ == '__main__':
    main()
