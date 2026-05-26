import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming
import numpy as np
perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbits, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

w2_orbits = [o for o in orbits if hamming(o[0]) == 2]
for idx, o in enumerate(w2_orbits):
    rep = o[0]
    w = hamming(rep)
    sz = len(o)
    stab_set = frozenset(stabs[x] for x in o)
    print(f'O_{idx}: rep={rep}, w={w}, sz={sz}, stab_set_size={len(stab_set)}')

# Check if O_2 and O_3 have same stab_set
o2_stab_set = frozenset(stabs[x] for x in w2_orbits[2])
o3_stab_set = frozenset(stabs[x] for x in w2_orbits[3])
print('O2 stab set == O3 stab set:', o2_stab_set == o3_stab_set)

# Check all signatures
sigs = {}
for idx, o in enumerate(orbits):
    rep = o[0]
    w = hamming(rep)
    sz = len(o)
    stab_set = frozenset(stabs[x] for x in o)
    sig = (w, sz, stab_set)
    sigs.setdefault(sig, []).append(idx)

for sig, idxs in sorted(sigs.items()):
    print(f'sig (w={sig[0]}, sz={sig[1]}, stab_set_size={len(sig[2])}): {len(idxs)} orbits')
