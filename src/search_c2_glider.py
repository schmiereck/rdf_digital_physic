#!/usr/bin/env python3
"""
search_c2_glider.py

Exhaustive search for period-1 and period-2 gliders under C2-symmetric rules
in the hexagonal 7-bit neighborhood CA.

For each asymmetric seed S and displacement d, enumerates candidate intermediate
states Q and checks if S -> Q -> S+d is achievable with a single consistent
C2-symmetric rule.
"""

import sys, random
from pathlib import Path
from itertools import combinations

sys.path.insert(0, str(Path(__file__).parent))
from run_c2_dense_motion_evolution import (
    rotate_c2, ALL_SEEDS, HEX_DIRS, _neighborhood,
    _translate_normalize, _center_of_mass, step_cells, evaluate_seed
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def c2_physical_rotate(cells):
    return frozenset((-q, -r) for q, r in cells)


def is_c2_symmetric(cells):
    return _translate_normalize(cells) == _translate_normalize(c2_physical_rotate(cells))


def get_candidates(cells):
    """All cells adjacent to (or in) the live pattern."""
    cands = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            cands.add((q + dq, r + dr))
    return cands


def compute_required_mappings(S, Q):
    """
    Compute which neighborhood states need non-identity mappings for S -> Q.
    Returns dict {state: target_center_bit} or None on internal conflict.
    """
    required = {}
    for q, r in get_candidates(S):
        state = _neighborhood(S, q, r)
        target_center = 1 if (q, r) in Q else 0
        default_center = (state >> 6) & 1
        if default_center == target_center:
            continue  # identity already correct
        if state in required:
            if required[state] != target_center:
                return None  # conflict: same state -> different targets
        else:
            required[state] = target_center
    return required


def propagate_c2(required):
    """
    Propagate C2 symmetry constraint: for each (s -> tc), also set C2(s) -> tc.
    Returns updated dict, or None on conflict.
    """
    full = dict(required)
    for state, tc in list(required.items()):
        conj = rotate_c2(state)
        if conj in full:
            if full[conj] != tc:
                return None  # C2 conflict
        else:
            full[conj] = tc
    return full


def merge_requirements(req1, req2):
    """Merge two requirement dicts. Returns None on conflict."""
    merged = dict(req1)
    for state, tc in req2.items():
        if state in merged:
            if merged[state] != tc:
                return None
        else:
            merged[state] = tc
    return merged


def build_engine_rule(required, rng=None):
    """
    Build a minimal C2-symmetric rule satisfying the required mappings.
    For each required (state, target_center), pairs state with a partner
    state that has the target center bit.
    Returns dict (rule) or None if impossible.
    """
    if rng is None:
        rng = random.Random(0)

    rule = {}
    mapped = set()

    # Process each required mapping
    for state, tc in required.items():
        if state in mapped:
            # Already handled (could have been paired as C2-conjugate)
            if state in rule:
                if (rule[state] >> 6) & 1 != tc:
                    return None  # conflict
            continue

        ra = rotate_c2(state)
        # ra must also be mapped to a state with center bit = tc
        if ra in mapped:
            if ra in rule:
                if (rule[ra] >> 6) & 1 != tc:
                    return None
            continue

        # Find partner p not yet mapped, with center bit = tc
        # Prefer states that are "unusual" (won't appear near small patterns)
        candidates_p = [
            p for p in range(128)
            if p not in mapped
            and ((p >> 6) & 1) == tc
            and p != state and p != ra
            and rotate_c2(p) != state and rotate_c2(p) != ra
        ]
        if not candidates_p:
            return None

        # Pick partner: prefer high bit-count (less likely to appear near small seeds)
        candidates_p.sort(key=lambda p: -bin(p).count('1'))
        p = candidates_p[0]
        rp = rotate_c2(p)

        # Verify quad is valid
        quad = {state, p, ra, rp}
        if len(quad) != 4:
            return None
        if quad & mapped:
            return None

        # Add mappings
        rule[state] = p
        rule[p] = state
        rule[ra] = rp
        rule[rp] = ra
        mapped |= quad

    return rule


def simulate_period(rule, seed, max_period=200, max_cells=500):
    """Check if seed produces a glider under rule. Returns (period, displacement) or None."""
    current = frozenset(seed)
    history = {_translate_normalize(current): (0, _center_of_mass(current))}

    for t in range(max_period):
        current = step_cells(current, rule)
        if len(current) == 0 or len(current) > max_cells:
            return None
        shape = _translate_normalize(current)
        com = _center_of_mass(current)
        if shape in history:
            prev_t, prev_com = history[shape]
            period = (t + 1) - prev_t
            dq = com[0] - prev_com[0]
            dr = com[1] - prev_com[1]
            import math
            disp = math.sqrt(dq*dq + dr*dr)
            if disp > 1e-9:
                return period, disp
            return None  # oscillator, not glider
        history[shape] = (t + 1, com)
    return None


# ── Period-2 glider search ────────────────────────────────────────────────────

DISPLACEMENTS = [
    (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1),   # 1-step
    (2, 0), (-2, 0), (0, 2), (0, -2), (2, -1), (-2, 1),    # 2-step
    (1, 1), (-1, -1), (2, -2), (-2, 2), (1, -2), (-1, 2),  # diagonals
]


def search_period2_glider(S, d, max_extra=3, verbose=False):
    """
    Search for period-2 glider: S -> Q -> S+d.
    Enumerates possible intermediate states Q.
    Returns (Q, rule) or None.
    """
    S = frozenset(S)
    dq, dr = d
    T = frozenset((q + dq, r + dr) for q, r in S)  # target

    S_cands = get_candidates(S)
    T_cands = get_candidates(T)
    all_cands = list(S_cands | T_cands)

    # Cells that CANNOT be in Q (they must die in S -> Q, i.e., in S but not T, and must not be born again)
    # Actually, we don't force S_only cells to be absent from Q - they could be in Q and die in Q->T.
    # But for simplicity and efficiency, try all subsets of all_cands.

    n_total = len(all_cands)
    # Limit: try Q of similar size to S ± max_extra
    min_size = max(0, len(S) - 1)
    max_size = min(n_total, len(S) + max_extra)

    for size in range(min_size, max_size + 1):
        for Q_tuple in combinations(all_cands, size):
            Q = frozenset(Q_tuple)

            # Required mappings for S -> Q
            req1 = compute_required_mappings(S, Q)
            if req1 is None:
                continue

            # Required mappings for Q -> T
            req2 = compute_required_mappings(Q, T)
            if req2 is None:
                continue

            # Merge requirements
            merged = merge_requirements(req1, req2)
            if merged is None:
                continue

            # Propagate C2 symmetry
            full_req = propagate_c2(merged)
            if full_req is None:
                continue

            # Build engine rule
            rule = build_engine_rule(full_req)
            if rule is None:
                continue

            # Verify by simulation
            actual_Q = step_cells(S, rule)
            if actual_Q != Q:
                # Q might differ due to C2-conjugate mappings causing extra events
                # Accept if it still maps to T
                pass

            actual_T = step_cells(actual_Q, rule)
            actual_T_norm = _translate_normalize(actual_T)
            T_norm = _translate_normalize(T)

            if actual_T_norm == T_norm:
                if verbose:
                    print(f"  Found period-2 glider! Q={sorted(actual_Q)} T_norm matches")
                return actual_Q, rule

    return None


def search_all_seeds(verbose=True):
    """Search all asymmetric seeds for period-2 gliders."""
    results = []
    for seed_name, seed_cells in ALL_SEEDS.items():
        if is_c2_symmetric(seed_cells):
            if verbose:
                print(f"  {seed_name}: symmetric, skipping")
            continue
        if verbose:
            print(f"  {seed_name}: asymmetric, searching...")
        for d in DISPLACEMENTS:
            result = search_period2_glider(seed_cells, d, max_extra=3, verbose=False)
            if result is not None:
                Q, rule = result
                # Verify with full simulation
                sim = simulate_period(rule, seed_cells, max_period=500)
                if sim is not None:
                    period, disp = sim
                    if verbose:
                        print(f"    GLIDER FOUND! seed={seed_name} d={d} period={period} disp={disp:.4f}")
                    results.append({
                        'seed_name': seed_name,
                        'seed_cells': seed_cells,
                        'displacement': d,
                        'Q': Q,
                        'rule': rule,
                        'period': period,
                        'disp': disp,
                    })
    return results


if __name__ == "__main__":
    print("Searching for C2-compatible period-2 gliders...")
    results = search_all_seeds(verbose=True)
    if results:
        print(f"\nFound {len(results)} glider(s)!")
        for r in results:
            print(f"  seed={r['seed_name']} d={r['displacement']} period={r['period']} disp={r['disp']:.4f}")
            print(f"  rule ({len(r['rule'])} active states): {r['rule']}")
    else:
        print("No period-2 gliders found.")
    sys.exit(0 if results else 1)
