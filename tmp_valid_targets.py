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
    H = stabs[rep]
    valid = [t for t in o if stabs[t] == H]
    print(f'O_{idx}: rep={rep}, size={len(o)}, stab_size={len(H)}, valid_targets={len(valid)}')
    print(f'  valid targets: {valid}')
