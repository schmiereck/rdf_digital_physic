#!/usr/bin/env python3
"""Quick test to verify 13-channel orbit classification before full implementation."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
from search_3d_gliders import (
    get_oh_permutations,
    hamming,
    fcc_neighbor_vectors,
)

# Build 13-channel permutations
perms_12 = get_oh_permutations(verbose=False)
perms_13 = [sigma + (12,) for sigma in perms_12]

# Precompute 13-channel action for 8192 states
n_perms = len(perms_13)
action_13 = np.zeros((n_perms, 8192), dtype=np.uint16)
s_arr = np.arange(8192, dtype=np.uint32)
for g, sigma in enumerate(perms_13):
    out = np.zeros(8192, dtype=np.uint32)
    for i in range(13):
        mask = (s_arr >> i) & 1
        out |= mask << int(sigma[i])
    action_13[g] = out.astype(np.uint16)

# Compute orbits for 8192 states
def compute_orbits_13(action):
    n_perms = action.shape[0]
    orbit_of = -np.ones(8192, dtype=np.int32)
    orbits = []
    for s in range(8192):
        if orbit_of[s] >= 0:
            continue
        members = {s}
        stack = [s]
        while stack:
            t = stack.pop()
            for g in range(n_perms):
                u = int(action[g, t])
                if u not in members:
                    members.add(u)
                    stack.append(u)
        oid = len(orbits)
        for t in members:
            orbit_of[t] = oid
        orbits.append(sorted(members))
    return orbits, orbit_of

orbits_13, orbit_of_13 = compute_orbits_13(action_13)

# Compute stabilizers for 8192 states
def compute_all_stabilizers_13(action):
    n_perms = action.shape[0]
    stabs = []
    for s in range(8192):
        stab = [g for g in range(n_perms) if int(action[g, s]) == s]
        stabs.append(tuple(stab))
    return stabs

stabs_13 = compute_all_stabilizers_13(action_13)

print(f"Total orbits: {len(orbits_13)}")
print(f"Total states: {sum(len(o) for o in orbits_13)}")

# Weight-2 orbits
w2_orbits = [(idx, o) for idx, o in enumerate(orbits_13) if hamming(o[0]) == 2]
print(f"Weight-2 orbits: {len(w2_orbits)}")

fcc_vecs = fcc_neighbor_vectors()
CARTESIAN_PAIRS = [(0,3), (1,2), (4,7), (5,6), (8,11), (9,10)]
antiparallel_states = {(1<<a)|(1<<b) for a,b in CARTESIAN_PAIRS}

for idx, o in w2_orbits:
    rep = o[0]
    chs = [i for i in range(13) if (rep >> i) & 1]
    has_rest = 12 in chs
    if has_rest:
        label = "E (rest+prop)"
    elif rep in antiparallel_states:
        label = "A (antiparallel)"
    else:
        i, j = chs
        dot = int(np.dot(fcc_vecs[i], fcc_vecs[j]))
        if dot == -1:
            label = "B (obtuse, dot=-1)"
        elif dot == 0:
            label = "C (perpendicular, dot=0)"
        elif dot == 1:
            label = "D (acute, dot=+1)"
        else:
            label = f"UNKNOWN (dot={dot})"
    print(f"  Orbit {idx}: size={len(o):2d}, rep={rep:4d} ch{chs}, |Stab|={len(stabs_13[rep]):2d}, {label}")

# Verify counts
counts = {"A":0, "B":0, "C":0, "D":0, "E":0}
for idx, o in w2_orbits:
    rep = o[0]
    chs = [i for i in range(13) if (rep >> i) & 1]
    has_rest = 12 in chs
    if has_rest:
        counts["E"] += len(o)
    elif rep in antiparallel_states:
        counts["A"] += len(o)
    else:
        i, j = chs
        dot = int(np.dot(fcc_vecs[i], fcc_vecs[j]))
        if dot == -1:
            counts["B"] += len(o)
        elif dot == 0:
            counts["C"] += len(o)
        elif dot == 1:
            counts["D"] += len(o)
print(f"\nVerification: A={counts['A']}, B={counts['B']}, C={counts['C']}, D={counts['D']}, E={counts['E']}")
print(f"Total: {sum(counts.values())} (expected 78)")

# Check cross-orbit stabilizer matches for C<->E and B<->D
print("\n--- Cross-orbit stabilizer analysis ---")
c_orbits = [(idx, o) for idx, o in w2_orbits if 12 not in [i for i in range(13) if (o[0]>>i)&1] and o[0] not in antiparallel_states and int(np.dot(fcc_vecs[[i for i in range(13) if (o[0]>>i)&1][0]], fcc_vecs[[i for i in range(13) if (o[0]>>i)&1][1]])) == 0]
e_orbits = [(idx, o) for idx, o in w2_orbits if 12 in [i for i in range(13) if (o[0]>>i)&1]]
b_orbits = [(idx, o) for idx, o in w2_orbits if 12 not in [i for i in range(13) if (o[0]>>i)&1] and o[0] not in antiparallel_states and int(np.dot(fcc_vecs[[i for i in range(13) if (o[0]>>i)&1][0]], fcc_vecs[[i for i in range(13) if (o[0]>>i)&1][1]])) == -1]
d_orbits = [(idx, o) for idx, o in w2_orbits if 12 not in [i for i in range(13) if (o[0]>>i)&1] and o[0] not in antiparallel_states and int(np.dot(fcc_vecs[[i for i in range(13) if (o[0]>>i)&1][0]], fcc_vecs[[i for i in range(13) if (o[0]>>i)&1][1]])) == 1]

print(f"C orbits: {len(c_orbits)}, E orbits: {len(e_orbits)}")
print(f"B orbits: {len(b_orbits)}, D orbits: {len(d_orbits)}")

if c_orbits and e_orbits:
    c_idx, c_orb = c_orbits[0]
    e_idx, e_orb = e_orbits[0]
    c_rep = c_orb[0]
    e_rep = e_orb[0]
    c_stab = stabs_13[c_rep]
    e_stab = stabs_13[e_rep]
    e_targets = [s for s in e_orb if stabs_13[s] == c_stab]
    c_targets = [s for s in c_orb if stabs_13[s] == e_stab]
    print(f"C rep {c_rep} stab size {len(c_stab)} -> valid E targets: {len(e_targets)}")
    print(f"E rep {e_rep} stab size {len(e_stab)} -> valid C targets: {len(c_targets)}")

if b_orbits and d_orbits:
    b_idx, b_orb = b_orbits[0]
    d_idx, d_orb = d_orbits[0]
    b_rep = b_orb[0]
    d_rep = d_orb[0]
    b_stab = stabs_13[b_rep]
    d_stab = stabs_13[d_rep]
    d_targets = [s for s in d_orb if stabs_13[s] == b_stab]
    b_targets = [s for s in b_orb if stabs_13[s] == d_stab]
    print(f"B rep {b_rep} stab size {len(b_stab)} -> valid D targets: {len(d_targets)}")
    print(f"D rep {d_rep} stab size {len(d_stab)} -> valid B targets: {len(b_targets)}")
