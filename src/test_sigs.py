import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming
import numpy as np
from collections import defaultdict

perms = get_oh_permutations(verbose=False)
action = precompute_perm_action(perms)
orbit_list, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

# Group orbits by signature
sigs = defaultdict(list)
for idx, o in enumerate(orbit_list):
    rep = o[0]
    w = hamming(rep)
    sz = len(o)
    stab_set = frozenset(stabs[x] for x in o)
    sig = (w, sz, stab_set)
    sigs[sig].append(idx)

print("Signature groups:")
for sig, orbit_indices in sorted(sigs.items(), key=lambda x: (x[0][0], x[0][1])):
    w, sz, _ = sig
    print(f"  weight={w}, size={sz}: {len(orbit_indices)} orbits -> {orbit_indices}")
