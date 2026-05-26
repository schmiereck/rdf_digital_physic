import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming
import numpy as np
perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbits, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

w2_orbits = [(idx, o) for idx, o in enumerate(orbits) if hamming(o[0]) == 2]
for idx, o in w2_orbits:
    print(f'Orbit {idx}: rep={o[0]}, size={len(o)}')
    for s in o:
        chs = [i for i in range(12) if (s >> i) & 1]
        print(f'  state {s}: chs={chs}, stab={stabs[s]}')
    print()
