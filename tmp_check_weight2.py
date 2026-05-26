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
    print(f'=== Orbit {idx}: rep={o[0]}, size={len(o)} ===')
    for s in o:
        chs = [i for i in range(12) if (s >> i) & 1]
        print(f'  state {s}: chs={chs}, stab={stabs[s]}')
    
    rep = o[0]
    H = stabs[rep]
    valid = [t for t in o if stabs[t] == H]
    print(f'  Valid targets for rep {rep} (stab={H}): {valid}')
    print()

# Now check the antipodal transposition:
# ch0<->ch1, ch2<->ch3, ch4<->ch5, ch6<->ch9, ch7<->ch10, ch8<->ch11
antipodal_pairs = [(0,1), (2,3), (4,5), (6,9), (7,10), (8,11)]
for a, b in antipodal_pairs:
    sa = 1 << a
    sb = 1 << b
    print(f'{a} <-> {b}: states {sa} <-> {sb}')
    print(f'  stab[{sa}] = {stabs[sa]}')
    print(f'  stab[{sb}] = {stabs[sb]}')
    print(f'  Are they in the same orbit?', orbit_of[sa] == orbit_of[sb])
