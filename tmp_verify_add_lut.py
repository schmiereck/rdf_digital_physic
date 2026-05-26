import numpy as np
from src.search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming

perms = get_oh_permutations(verbose=False)
print(f"perms: {len(perms)}")
action = precompute_perm_action(perms)
print(f"action shape: {action.shape}")
orbits, orbit_of = compute_orbits(action)
print(f"orbits: {len(orbits)}")
stabs = compute_all_stabilizers(action)
print(f"stabs computed")

# Correct antipodal pairs: 0<->3, 1<->2, 4<->7, 5<->6, 8<->11, 9<->10
antipode = [0]*12
pairs = [(0,3),(1,2),(4,7),(5,6),(8,11),(9,10)]
for a,b in pairs:
    antipode[a]=b
    antipode[b]=a

# Build additive LUT with correct antipodal mapping
lut = np.zeros(4096, dtype=np.uint16)
w1_out = np.zeros(12, dtype=np.uint16)
for ch in range(12):
    w1_out[ch] = 1 << antipode[ch]
for s in range(4096):
    out = 0
    for ch in range(12):
        if (s >> ch) & 1:
            out |= w1_out[ch]
    lut[s] = out

# Verify O_h symmetry
sym_ok = True
for g in range(len(perms)):
    lhs = lut[action[g]]
    rhs = action[g, lut]
    if not np.array_equal(lhs, rhs):
        sym_ok = False
        print(f'Symmetry violated at perm {g}')
        break
print(f'O_h symmetric: {sym_ok}')

# Check bijectivity
unique = len(np.unique(lut))
print(f'Unique outputs: {unique}')

# Check bit conservation
pops_in = np.array([bin(s).count('1') for s in range(4096)])
pops_out = np.array([bin(int(lut[s])).count('1') for s in range(4096)])
print(f'Bit conserving: {np.array_equal(pops_in, pops_out)}')

# Check weight-2 orbit images
for idx, o in enumerate(orbits):
    if hamming(o[0]) == 2:
        rep = o[0]
        out_orbits = {}
        for s in o:
            t = int(lut[s])
            o_t = int(orbit_of[t])
            oreg = int(orbits[o_t][0])
            out_orbits[o_t] = out_orbits.get(o_t, (oreg, 0))
            out_orbits[o_t] = (out_orbits[o_t][0], out_orbits[o_t][1] + 1)
        print(f'Orbit {idx} (rep={rep}, size={len(o)}, stab={len(stabs[rep])}):')
        for oid, (oreg, count) in out_orbits.items():
            same = 'SAME' if oid == idx else 'DIFF'
            print(f'  -> orbit {oid} (rep={oreg}, count={count}) [{same}]')
