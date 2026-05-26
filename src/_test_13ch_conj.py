#!/usr/bin/env python3
"""Check if stabilizers are conjugate across orbits."""
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

a_orbit = b_orbit = c_orbit = d_orbit = e_orbit = None
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

# Function to conjugate a stabilizer by a group element
def conjugate_stab(stab, g):
    """Return the conjugated stabilizer g * stab * g^{-1} as a sorted tuple of perm indices."""
    # perm_13[g] is the permutation sigma_g
    # For h in stab, the conjugate is sigma_g * sigma_h * sigma_g^{-1}
    # We need to compute this as a permutation index
    sigma_g = perms_13[g]
    # Build inverse of sigma_g
    inv_g = [0]*13
    for i, s in enumerate(sigma_g):
        inv_g[s] = i
    
    conj = []
    for h in stab:
        sigma_h = perms_13[h]
        # compute sigma_g * sigma_h * sigma_g^{-1}
        comp = [0]*13
        for i in range(13):
            comp[i] = sigma_g[sigma_h[inv_g[i]]]
        # Find which permutation this is
        comp_t = tuple(comp)
        # Search for it in perms_13
        try:
            idx = perms_13.index(comp_t)
            conj.append(idx)
        except ValueError:
            pass
    return tuple(sorted(conj))

# Check if any stabilizer in C is conjugate to any stabilizer in E
print("=== Conjugacy check C vs E ===")
c_stabs = list(set(stabs[s] for s in c_orbit))
e_stabs = list(set(stabs[s] for s in e_orbit))
found_ce = False
for c_stab in c_stabs:
    for g in range(n_perms):
        conj = conjugate_stab(c_stab, g)
        if conj in e_stabs:
            print(f"C stab (size {len(c_stab)}) conjugate to E stab by perm {g}")
            found_ce = True
            break
    if found_ce:
        break
if not found_ce:
    print("NO conjugate stabilizers found between C and E")

# Check B vs D
print("\n=== Conjugacy check B vs D ===")
b_stabs = list(set(stabs[s] for s in b_orbit))
d_stabs = list(set(stabs[s] for s in d_orbit))
found_bd = False
for b_stab in b_stabs:
    for g in range(n_perms):
        conj = conjugate_stab(b_stab, g)
        if conj in d_stabs:
            print(f"B stab (size {len(b_stab)}) conjugate to D stab by perm {g}")
            found_bd = True
            break
    if found_bd:
        break
if not found_bd:
    print("NO conjugate stabilizers found between B and D")

# Also check: are all stabilizers within an orbit conjugate to each other?
print("\n=== Intra-orbit conjugacy ===")
for name, orb in [("A", a_orbit), ("B", b_orbit), ("C", c_orbit), ("D", d_orbit), ("E", e_orbit)]:
    stab_set = list(set(stabs[s] for s in orb))
    ref = stab_set[0]
    all_conj = True
    for s in stab_set[1:]:
        is_conj = False
        for g in range(n_perms):
            if conjugate_stab(ref, g) == s:
                is_conj = True
                break
        if not is_conj:
            all_conj = False
            break
    print(f"Orbit {name}: all {len(stab_set)} stabilizers conjugate? {all_conj}")
