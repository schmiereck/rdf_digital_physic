import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming
import numpy as np
perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbits, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

w2_orbits = [o for o in orbits if hamming(o[0]) == 2]
print('Number of weight-2 orbits:', len(w2_orbits))
for idx, o in enumerate(w2_orbits):
    rep = o[0]
    chs = [i for i in range(12) if (rep >> i) & 1]
    print(f'O_{idx}: rep={rep}, chs={chs}, size={len(o)}, stab_size={len(stabs[rep])}')
