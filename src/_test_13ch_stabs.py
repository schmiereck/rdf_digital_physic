#!/usr/bin/env python3
"""Thorough stabilizer analysis for 13-channel cross-orbit mappings."""
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

perms_12 = get_oh_permutations(verbose=False)
perms_13 = [sigma + (12,) for sigma in perms_12]

n_perms = len(perms_13)
action_13 = np.zeros((n_perms, 8192), dtype=np.uint16)
s_arr = np.arange(8192, dtype=np.uint32)
for g, sigma in enumerate(perms_13):
    out = np.zeros(8192, dtype=np.uint32)
    for i in range(13):
        mask = (s_arr >> i) & 1
        out |= mask << int(sigma[i])
    action_13[g] = out.astype(np.uint16)

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
            u = int(action_13[g, t])
            if u not in members:
                members.add(u)
                stack.append(u)
    oid = len(orbits)
    for t in members:
        orbit_of[t] = oid
    orbits.append(sorted(members))

stabs = []
for s in range(8192):
    stab = [g for g in range(n_perms) if int(action_13[g, s]) == s]
    stabs.append(tuple(stab))

fcc_vecs = fcc_neighbor_vectors()
CARTESIAN_PAIRS = [(0,3), (1,2), (4,7), (5,6), (8,11), (9,10)]
antiparallel_states = {(1<<a)|(1<<b) for a,b in CARTESIAN_PAIRS}

w2_orbits = [(idx, o) for idx, o in enumerate(orbits) if hamming(o[0]) == 2]

# Identify orbits
a_orbit = None
b_orbit = None
c_orbit = None
d_orbit = None
e_orbit = None

for idx, o in w2_orbits:
    rep = o[0]
    chs = [i for i in range(13) if (rep >> i) & 1]
    if 12 in chs:
        e_orbit = o
    elif rep in antiparallel_states:
        a_orbit = o
    else:
        i, j = chs
        dot = int(np.dot(fcc_vecs[i], fcc_vecs[j]))
        if dot == -1:
            b_orbit = o
        elif dot == 0:
            c_orbit = o
        elif dot == 1:
            d_orbit = o

print("=== Stabilizer class analysis ===")
for name, orb in [("A", a_orbit), ("B", b_orbit), ("C", c_orbit), ("D", d_orbit), ("E", e_orbit)]:
    stab_classes = {}
    for s in orb:
        stab_classes.setdefault(stabs[s], []).append(s)
    print(f"\nOrbit {name} (size {len(orb)}):")
    for stab, members in stab_classes.items():
        print(f"  |Stab|={len(stab):2d}, count={len(members):2d}, reps={members[:3]}...")

# Check if any stabilizer in C equals any stabilizer in E
print("\n=== Cross-orbit stabilizer equality ===")
c_stabs = set(stabs[s] for s in c_orbit)
e_stabs = set(stabs[s] for s in e_orbit)
common_ce = c_stabs & e_stabs
print(f"C and E common stabilizers: {len(common_ce)}")

b_stabs = set(stabs[s] for s in b_orbit)
d_stabs = set(stabs[s] for s in d_orbit)
common_bd = b_stabs & d_stabs
print(f"B and D common stabilizers: {len(common_bd)}")

# For each common stabilizer, show examples
if common_ce:
    for stab in list(common_ce)[:3]:
        c_examples = [s for s in c_orbit if stabs[s] == stab][:2]
        e_examples = [s for s in e_orbit if stabs[s] == stab][:2]
        print(f"  Stab size {len(stab)}: C examples {c_examples}, E examples {e_examples}")

if common_bd:
    for stab in list(common_bd)[:3]:
        b_examples = [s for s in b_orbit if stabs[s] == stab][:2]
        d_examples = [s for s in d_orbit if stabs[s] == stab][:2]
        print(f"  Stab size {len(stab)}: B examples {b_examples}, D examples {d_examples}")
