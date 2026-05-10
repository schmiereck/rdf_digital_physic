"""
Generate and validate a 2-bit/cell 1D cellular automaton rule.

Hypothesis: A non-trivial, reversible, bit-conserving rule exists for a
1D, 3-neighborhood, 2-bit/cell lattice.
"""

import itertools
from collections import defaultdict
import yaml
import os

# State space: each cell has 2 bits, so 4 possible states
CELL_STATES = ['00', '01', '10', '11']

def hamming_weight(state: str) -> int:
    return state.count('1')

def neighborhood_weight(neighborhood: tuple) -> int:
    return sum(hamming_weight(s) for s in neighborhood)

def build_neighborhoods():
    return list(itertools.product(CELL_STATES, repeat=3))

def group_by_hamming_weight(neighborhoods):
    groups = defaultdict(list)
    for n in neighborhoods:
        w = neighborhood_weight(n)
        groups[w].append(n)
    return dict(groups)

def build_test_rule(neighborhoods):
    rule = {n: n for n in neighborhoods}
    # Stationary particle oscillation pair
    n1 = ('00', '01', '00')
    n2 = ('00', '10', '00')
    rule[n1] = n2
    rule[n2] = n1
    return rule

def is_nontrivial(rule):
    return any(k != v for k, v in rule.items())

def main():
    neighborhoods = build_neighborhoods()
    assert len(neighborhoods) == 64

    groups = group_by_hamming_weight(neighborhoods)
    hamming_group_sizes = {f"W{w}": len(states) for w, states in sorted(groups.items())}

    assert sum(hamming_group_sizes.values()) == 64

    rule = build_test_rule(neighborhoods)

    # Verify bit conservation: output weight == input weight for every mapping
    for inp, out in rule.items():
        assert neighborhood_weight(inp) == neighborhood_weight(out), (
            f"Bit conservation violated: {inp} -> {out}"
        )

    # Verify reversibility: the mapping must be a bijection
    outputs = list(rule.values())
    assert len(outputs) == len(set(outputs)), "Rule is not reversible (not a bijection)"

    nontrivial = is_nontrivial(rule)

    result = {
        'rule_found': bool(nontrivial),
        'state_space_size': 64,
        'hamming_group_sizes': hamming_group_sizes,
    }

    out_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'iter_003', 'result.yaml'
    )
    out_path = os.path.normpath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, 'w') as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)

    print(f"rule_found: {result['rule_found']}")
    print(f"state_space_size: {result['state_space_size']}")
    print(f"hamming_group_sizes: {result['hamming_group_sizes']}")
    print(f"Result written to: {out_path}")

if __name__ == '__main__':
    main()
