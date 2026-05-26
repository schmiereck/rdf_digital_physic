import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming
import numpy as np

perms = get_oh_permutations(verbose=False)
action = precompute_perm_action(perms)
orbit_list, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

w2_orbits = []
for idx, o in enumerate(orbit_list):
    if hamming(o[0]) == 2:
        rep = o[0]
        H = stabs[rep]
        valid = [t for t in o if stabs[t] == H]
        w2_orbits.append({
            "global_idx": idx,
            "rep": rep,
            "orbit_members": sorted(o),
            "stab_size": len(H),
            "valid_targets": sorted(valid),
        })

w2_orbits.sort(key=lambda d: d["rep"])

print(f"Number of weight-2 orbits: {len(w2_orbits)}")
for i, d in enumerate(w2_orbits):
    print(f"\nO_{i}: rep={d['rep']}, size={len(d['orbit_members'])}, stab_size={d['stab_size']}")
    print(f"  valid_targets ({len(d['valid_targets'])}): {d['valid_targets']}")

# Total configurations
total = 1
for d in w2_orbits:
    total *= len(d['valid_targets'])
print(f"\nTotal configurations: {total}")
