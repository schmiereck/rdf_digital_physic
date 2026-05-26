import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming
import numpy as np

perms = get_oh_permutations(verbose=False)
action = precompute_perm_action(perms)
orbit_list, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

for idx, o in enumerate(orbit_list):
    w = hamming(o[0])
    if w == 1:
        print(f"Weight-1 orbit {idx}: rep={o[0]}, size={len(o)}, stab_size={len(stabs[o[0]])}")
        print(f"  members: {o}")

# Check where Cartesian transposition sends each weight-1 state
PAIRS = [(0, 3), (1, 2), (4, 7), (5, 6), (8, 11), (9, 10)]
trans = [0] * 12
for a, b in PAIRS:
    trans[a] = b
    trans[b] = a

print("\nCartesian transposition mapping:")
for s in range(12):
    t = 1 << trans[s]
    print(f"  2^{s} ({s}) -> 2^{trans[s]} ({t})")
    
# Check orbit images
print("\nOrbit images under Cartesian transposition:")
for idx, o in enumerate(orbit_list):
    if hamming(o[0]) == 1:
        images = set()
        for s in o:
            ch = (s & -s).bit_length() - 1
            t = 1 << trans[ch]
            images.add(t)
        image_orbits = set()
        for t in images:
            image_orbits.add(int(orbit_of[t]))
        print(f"  Orbit {idx} (rep={o[0]}) -> orbit(s) {image_orbits}")
