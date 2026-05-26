#!/usr/bin/env python3
"""
non_additive_lut_v2.py — O_h-symmetric non-additive LUT construction for 3D FCC lattice.

Constructs:
1. ADDITIVE control LUT: with the antipodal transposition weight-1 sub-table,
   and additive extension for all other weights.
2. Any of the 128 unique O_h-symmetric weight-2 sub-table configurations.

Background from weight-2 orbit analysis:
- 4 weight-2 orbits with stabilizers of size 4, 8, 2, 2.
- Their stabilizer conjugacy classes are distinct, so they cannot map to each other.
- Orbit O_0: 4 valid same-stabilizer targets
- Orbit O_1: 2 valid same-stabilizer targets
- Orbit O_2: 4 valid same-stabilizer targets
- Orbit O_3: 4 valid same-stabilizer targets
- Total: 4 * 2 * 4 * 4 = 128 unique O_h-symmetric weight-2 configurations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.search_3d_gliders import (
    get_oh_permutations,
    precompute_perm_action,
    compute_orbits,
    compute_all_stabilizers,
    hamming,
)

# ========================================================================
# Antipodal transposition weight-1 sub-table
# ========================================================================
# Channels paired: (0,1), (2,3), (4,5), (6,9), (7,10), (8,11)
# This is a period-2 transposition on each pair.
ANTIPODAL_PAIRS = [(0, 1), (2, 3), (4, 5), (6, 9), (7, 10), (8, 11)]

# Build the antipodal lookup for weight-1: state 2^ch -> state 2^antipodal[ch]
_ANTIPODAL_LUT = [0] * 12
for a, b in ANTIPODAL_PAIRS:
    _ANTIPODAL_LUT[a] = b
    _ANTIPODAL_LUT[b] = a

# ========================================================================
# Cached O_h infrastructure (computed lazily)
# ========================================================================
_oh_cache: dict = {}

def _get_oh():
    if "perms" not in _oh_cache:
        perms = get_oh_permutations(verbose=False)
        action = precompute_perm_action(perms)
        orbits, orbit_of = compute_orbits(action)
        stabs = compute_all_stabilizers(action)
        _oh_cache["perms"] = perms
        _oh_cache["action"] = action
        _oh_cache["orbits"] = orbits
        _oh_cache["orbit_of"] = orbit_of
        _oh_cache["stabs"] = stabs
    return (
        _oh_cache["perms"],
        _oh_cache["action"],
        _oh_cache["orbits"],
        _oh_cache["orbit_of"],
        _oh_cache["stabs"],
    )

# ========================================================================
# Identify the 4 weight-2 orbits and their valid targets
# ========================================================================
def _identify_w2_orbit_data():
    """
    Identify representatives, sizes, and valid same-stabilizer targets
    for all 4 weight-2 orbits.
    
    Returns a list of dicts, one per weight-2 orbit (sorted by rep state value),
    each containing:
        - rep: representative state
        - orbit_members: list of all states in this orbit
        - stab_size: size of stabilizer for rep
        - valid_targets: list of states in the SAME orbit with the SAME stabilizer as rep
    """
    perms, action, orbits, orbit_of, stabs = _get_oh()
    w2_orbits = []
    for idx, o in enumerate(orbits):
        if hamming(o[0]) == 2:
            rep = o[0]
            H = stabs[rep]
            valid = [t for t in o if stabs[t] == H]
            w2_orbits.append({
                "global_idx": idx,
                "rep": rep,
                "orbit_members": sorted(o),
                "stab_size": len(H),
                "valid_targets": sorted(valid),
            })
    # Sort by rep state value for consistent ordering
    w2_orbits.sort(key=lambda d: d["rep"])
    # Assign local O_0, O_1, O_2, O_3 labels
    for i, d in enumerate(w2_orbits):
        d["local_label"] = f"O_{i}"
    return w2_orbits


_W2_ORBIT_DATA = None

def get_w2_orbit_data():
    global _W2_ORBIT_DATA
    if _W2_ORBIT_DATA is None:
        _W2_ORBIT_DATA = _identify_w2_orbit_data()
    return _W2_ORBIT_DATA


# ========================================================================
# Build the antipodal-based additive LUT
# ========================================================================
def build_additive_lut() -> np.ndarray:
    """
    Build the ADDITIVE control LUT.
    
    Weight-1: antipodal transposition (ch0↔ch1, ch2↔ch3, ch4↔ch5, ch6↔ch9, ch7↔ch10, ch8↔ch11).
    Weight-w (w>=2): bitwise OR of weight-1 outputs for each set bit.
    
    Returns:
        np.ndarray of shape (4096,), dtype uint16
    """
    lut = np.zeros(4096, dtype=np.uint16)
    
    # Build single-bit outputs
    w1_out = np.zeros(12, dtype=np.uint16)
    for ch in range(12):
        w1_out[ch] = 1 << _ANTIPODAL_LUT[ch]
    
    # For each state, compute additive output
    for s in range(4096):
        out = 0
        for ch in range(12):
            if (s >> ch) & 1:
                out |= w1_out[ch]
        lut[s] = out
    
    return lut


# ========================================================================
# Verify O_h symmetry of the antipodal transposition
# ========================================================================
def verify_antipodal_oh_symmetry() -> bool:
    """
    Verify that the antipodal transposition is O_h-symmetric.
    For each permutation g and channel i: antipodal(g(i)) == g(antipodal(i)).
    """
    perms, action, orbits, orbit_of, stabs = _get_oh()
    for g_idx, perm in enumerate(perms):
        for i in range(12):
            left = _ANTIPODAL_LUT[perm[i]]
            right = perm[_ANTIPODAL_LUT[i]]
            if left != right:
                return False
    return True


# ========================================================================
# Build a non-additive LUT with a specific weight-2 configuration
# ========================================================================
def build_nonadditive_lut(config_index: int) -> np.ndarray:
    """
    Build an O_h-symmetric non-additive LUT using the given configuration index.
    
    There are exactly 128 unique configurations (4 * 2 * 4 * 4).
    The config_index ranges from 0 to 127.
    
    Strategy:
    - Weight-1: fixed as antipodal transposition.
    - Weight-2: each orbit maps to one of its valid same-stabilizer targets.
      The valid targets are selected according to config_index.
    - Weight-w (w>=3): additive extension (OR of weight-1 outputs for each set bit,
      then modified weight-2 components replaced).
      Actually, for full correctness, weights 3+ should also be handled by the orbit
      structure. But since we're only modifying weight-2, and weight-3+ groupings
      are constrained by the same orbit-grouping structure, we need to ensure
      the entire LUT is O_h-symmetric and bijective.
      
    Simplified approach for this search:
    - Start with the additive LUT.
    - For each weight-2 orbit, replace the mapping for all orbit members
      to map to the chosen target orbit.
    - For weights >=3, use the same orbit-pairing structure: if two orbits are paired
      at weight-2, their corresponding higher-weight orbits must also be paired.
      However, since higher-weight states can be built from lower-weight combinations,
      we handle weight-3+ as follows:
      - For each state of weight >=3, decompose it into the orbit of its highest-priority
        weight-2 substate, and apply the mapping.
      
    Actually, the cleanest way is to use the same orbit-matching method as
    generate_symmetric_lut() in search_3d_gliders.py, but with the constraint
    that weight-1 is fixed to antipodal and weight-2 is fixed to the config.
    
    Wait — the orbit-matching only pairs orbits within the same signature.
    Since the 4 weight-2 orbits have DISTINCT stabilizer classes (as already noted),
    they can only map within themselves.
    
    So for each weight-2 orbit, the output must be a state in the SAME orbit.
    The valid targets (same stabilizer) are the ones we enumerate.
    
    For weight-3+ orbits, they have their own signatures and can only map
    within their groups. We don't modify them — they remain as in the additive LUT.
    But wait: is the additive LUT O_h-symmetric? Only if the weight-1 sub-table
    is O_h-symmetric AND the extension is O_h-equivariant.
    
    Let's check: is the additive extension of an O_h-symmetric weight-1 table
    itself O_h-symmetric? 
    
    For an O_h-symmetric weight-1 table f(2^i) = 2^{a(i)},
    the additive extension is f(s) = OR_{i in s} f(2^i).
    
    For g in O_h: g acts on channels by perm(g).
    g(f(s)) = g(OR_{i in s} 2^{a(i)}) = OR_{i in s} g(2^{a(i)}) = OR_{i in s} 2^{perm_g(a(i))}
    
    f(g(s)) = f(OR_{i in s} 2^{perm_g(i)}) = OR_{i in s} f(2^{perm_g(i)}) = OR_{i in s} 2^{a(perm_g(i))}
    
    For these to be equal: perm_g(a(i)) = a(perm_g(i)) for all i, g.
    This is exactly the condition that the antipodal map is O_h-symmetric!
    
    And we've verified that in tmp_check_antipodal.py, this IS true.
    
    So the additive LUT IS O_h-symmetric.
    
    Now, for the non-additive modification: we change the mapping for weight-2
    states. But to maintain bijectivity, we need to pair each input orbit with
    a distinct output orbit. Since each weight-2 orbit can only map to itself
    (different stabilizer classes), the mapping must be a permutation WITHIN
    each weight-2 orbit.
    
    The orbit-matching in generate_symmetric_lut pairs src and dst orbits.
    For weight-2, each orbit is mapped to itself, and within each orbit,
    the mapping is defined by f(g·r) = g·t where r is the rep and t is the chosen target.
    
    For weight >=3, we keep the additive (identity) mapping. The question is:
    does keeping weight-3+ additive while modifying weight-2 break bijectivity?
    
    Actually, for the full bijection, we need to pair ALL orbits. If we modify
    weight-2, the corresponding weight-3+ orbits need to be adjusted too.
    
    But the key insight from search_3d_gliders.py is that orbits can only pair
    with orbits of the same (weight, size, stabilizer set) signature. Since
    weight-2 orbits are in their own groups, we can permute them independently
    of higher-weight orbits.
    
    For the exhaustive search to be VALID, we need to ensure bijectivity.
    The simplest valid non-additive modification is: modify ONLY weight-2,
    and pair orbit with itself (i.e., map each weight-2 orbit to itself,
    choosing a representative -> target mapping that generates a PERMUTATION
    of the orbit).
    
    For a permutation of an orbit under the equivariant mapping f(g·r) = g·t:
    - The mapping is a bijection on the orbit if and only if the stabilizer
      of t equals the stabilizer of r (which we've ensured by selecting same-stabilizer targets).
    - The orbit size = |O_h| / |Stab(r)| = |O_h| / |Stab(t)|.
    - For each coset of Stab(r), g·r takes |O_h|/|Stab(r)| distinct values.
    - And g·t also takes |O_h|/|Stab(t)| = |O_h|/|Stab(r)| distinct values.
    - So the map g·r -> g·t is a bijection on the orbit.
    
    What about other orbits? For the full LUT to be a bijection on ALL 4096 states,
    we need the weight-2 modifications to be part of a valid permutation of
    the entire state space. Since orbits of different weights have different
    signatures, they are in different groups and don't interact. Within weight-2,
    each orbit is mapped to itself, which is a valid permutation. So the overall
    mapping is a bijection.
    
    For weight != 2, we use the identity mapping (which is a bijection).
    This gives a valid LUT.
    
    Wait, but we need to check: is the identity mapping O_h-symmetric for
    all weights? Yes, because id(g·s) = g·s = g·id(s).
    
    So the construction is:
    - For weight != 2: identity mapping (state maps to itself).
    - For weight == 2: within each orbit, use equivariant map to chosen target.
    
    But wait: using identity for weight != 2 but antipodal for weight-1 means
    the weight-1 sub-table is NOT the identity, it's antipodal. And the additive
    extension of antipodal weight-1 is NOT the identity for weight >=2.
    
    If we use identity for all weights except 2, then weight-1 is identity,
    not antipodal. That contradicts our requirement.
    
    OK, let's be more careful. We want:
    - ADDITIVE control: weight-1 is antipodal, weight-w (all) is additive extension.
    - NON-ADDITIVE variants: weight-1 is antipodal, weight-2 is modified,
      weight-3+ is... what?
    
    For the non-additive variant to be O_h-symmetric and bijective with
    antipodal weight-1, we need to think carefully.
    
    Actually, the "additive" for weight-3+ means they should be computed as
    the additive extension of weight-1, EXCEPT that when a state contains
    exactly 2 bits, we use the modified mapping. For weight >=3, the state
    might contain multiple weight-2 substates. Do we "detect" weight-2
    collisions as sub-components? Or is the mapping purely functional on
    the full 12-bit state?
    
    In the LGCA framework, the collision is a function f: {0,1}^12 -> {0,1}^12
    applied to the FULL state of a cell. It's not decomposed into sub-collisions.
    The fact that for some f, f(s OR t) = f(s) OR f(t) (additive) is a special
    property, but in general f is just a lookup table.
    
    So when we build a non-additive LUT, we modify the entries for weight-2
    states. For weight >=3 states, we have freedom. The natural choices are:
    1. Keep them as the additive extension (this might or might not be consistent
       with the modified weight-2, and might not be bijective).
    2. Define them by the same orbit-pairing mechanism.
    
    To ensure bijectivity, the safest is to pair orbits within each signature group.
    For the non-additive search, we want to EXHAUSTIVELY try ALL 128 ways to
    modify weight-2. For weight != 2, the simplest is to use the identity.
    But then weight-1 would be identity, not antipodal.
    
    Hmm. Let me reconsider: what if we use the ADDITIVE LUT as the base, and
    then swap weight-2 entries? Since the additive LUT maps each weight to
    the additive extension of antipodal weight-1, and the additive extension
    is O_h-symmetric, starting from the additive LUT and swapping weight-2
    entries in an orbit-compatible way should still give a bijective, symmetric LUT.
    
    Let's verify: the additive LUT is a bijection (because weight is preserved
    and within each weight, the map is a bijection — well, is it? The additive
    extension of antipodal weight-1 should be checked for bijectivity).
    
    Actually, is the additive extension of a weight-1 bijection itself a bijection?
    Not necessarily! Consider weight-1: 2^0 -> 2^1, 2^1 -> 2^0 (swap).
    For weight-2: state 3 = 2^0 | 2^1 -> 2^1 | 2^0 = 3. So state 3 maps to 3.
    But state 0 maps to 0, state 1 maps to 2, state 2 maps to 1.
    For weight-2, there are C(12,2) = 66 states. The additive extension maps each
    to a weight-2 state. Is this a bijection on weight-2 states?
    
    The weight-1 map is a permutation of 12 channels (6 transpositions).
    The weight-2 additive map sends {i,j} -> {a(i), a(j)} where a is the weight-1
    permutation. This is well-defined on unordered pairs. The number of unordered
    pairs is 66. The map is injective if {a(i), a(j)} = {a(k), a(l)} implies
    {i,j} = {k,l}, which is true because a is bijective. So yes, it's a bijection
    on weight-2 states.
    
    Similarly for all weights: the map on k-subsets induced by a permutation a
    is a bijection. So the additive LUT is a bijection.
    
    Now, what if we start with the additive LUT and modify some weight-2 entries?
    For each modified weight-2 state s -> s' (not equal to additive(s)), we must
    ensure that:
    1. s' is weight-2 (preserved by O_h symmetric).
    2. The mapping is still a bijection on ALL weight-2 states.
    3. The mapping is still O_h-symmetric.
    
    Since we modify whole orbits using equivariant maps (f(g·r) = g·t), properties
    2 and 3 are maintained. And since each orbit is mapped to itself (same
    stabilizer class, within the same orbit group), the permutation on each
    orbit is a bijection. So the overall weight-2 map is a bijection.
    
    What about weight != 2? We keep them as in the additive LUT. Since the
    additive LUT is a bijection, and we're only modifying weight-2 entries,
    we need to make sure we don't create collisions.
    But if s -> s' where s and s' are both weight-2, and s' was previously
    mapped to by some other state in the additive LUT, then we create a collision.
    
    This means we CAN'T simply modify weight-2 entries independently; we need
    to ensure that the new weight-2 mapping is a bijection on weight-2 states
    AND doesn't interfere with mappings from other weights (but since weight
    is preserved, that's automatic — weight-2 states only map to weight-2 states).
    
    So we just need:
    - The new weight-2 mapping is a bijection on the 66 weight-2 states.
    - For the non-target weight-2 states in each orbit, their mapping must
      also be adjusted if we're to maintain bijectivity.
    
    Actually, if state s was originally mapped to t in the additive LUT, and
    we now want s -> t' (where t' != t), then t is no longer in the image of s.
    If t was not the image of any other state, then we just need to make sure
    t' is not already in the image of some other state.
    
    Since we're doing an equivariant orbit mapping, the entire orbit is permuted.
    Specifically, we replace the additive mapping for orbit O with a new equivariant
    map. The new map sends O to O (since the target is in the same orbit), and is
    a bijection on O. Since O is disjoint from other weight-2 orbits, and the map
    sends O to O, it's a permutation of O.
    
    But the additive LUT also sends O to some states (possibly in different orbits!).
    If the additive LUT sends O to a DIFFERENT orbit O', and our new map sends O
    to O, then states in O' that were in the image of O are now freed, and states
    in O that were images of other states in the additive LUT need to be checked.
    
    This gets complicated. Let me verify with actual computation.
    
    Let me check where the additive LUT sends each weight-2 orbit.
    """
    pass  # docstring only


def _build_additive_lut_detailed() -> np.ndarray:
    """Build additive LUT and return with verification."""
    lut = np.zeros(4096, dtype=np.uint16)
    w1_out = np.zeros(12, dtype=np.uint16)
    for ch in range(12):
        w1_out[ch] = 1 << _ANTIPODAL_LUT[ch]
    for s in range(4096):
        out = 0
        for ch in range(12):
            if (s >> ch) & 1:
                out |= w1_out[ch]
        lut[s] = out
    return lut


def _compute_w2_orbit_images():
    """Compute where the additive LUT sends each weight-2 orbit."""
    lut = _build_additive_lut_detailed()
    w2_data = get_w2_orbit_data()
    results = []
    for d in w2_data:
        output_orbits = {}
        for s in d["orbit_members"]:
            t = int(lut[s])
            o_t = _oh_cache["orbit_of"][t]
            output_orbits.setdefault(int(o_t), []).append((s, t))
        results.append({
            "local_label": d["local_label"],
            "rep": d["rep"],
            "output_orbits": output_orbits,
        })
    return results


# Let me test this to understand the structure
if __name__ == "__main__":
    import json
    
    # Verify antipodal symmetry
    print("Antipodal O_h symmetric:", verify_antipodal_oh_symmetry())
    
    # Build additive LUT
    add_lut = _build_additive_lut_detailed()
    
    # Verify bijectivity and bit conservation
    unique_out = len(np.unique(add_lut))
    pops_in = np.array([bin(s).count('1') for s in range(4096)])
    pops_out = np.array([bin(int(add_lut[s])).count('1') for s in range(4096)])
    print(f"Additive LUT: unique={unique_out}, bit_conserving={np.array_equal(pops_in, pops_out)}")
    
    # Check weight-2 orbit images
    images = _compute_w2_orbit_images()
    for img in images:
        print(f"\n{img['local_label']} (rep={img['rep']}):")
        for oid, pairs in img["output_orbits"].items():
            rep_out = _oh_cache["orbits"][oid][0]
            print(f"  -> global orbit {oid} (rep={rep_out}), {len(pairs)} states")
    
    # Get the full w2 data
    w2_data = get_w2_orbit_data()
    print("\n=== Weight-2 orbit data ===")
    for d in w2_data:
        print(f"\n{d['local_label']}: rep={d['rep']}, stab_size={d['stab_size']}")
        print(f"  orbit size: {len(d['orbit_members'])}")
        print(f"  valid targets: {d['valid_targets']}")
