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
    # print a few stabilizers
    for x in o[:3]:
        print(f'  state {x}: stab={stabs[x]}')
