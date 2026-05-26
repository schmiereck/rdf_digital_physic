import numpy as np
from src.search_3d_gliders import get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming

perms = get_oh_permutations(verbose=False)
action = precompute_perm_action(perms)
orbits, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

# Correct antipodal pairs: 0<->3, 1<->2, 4<->7, 5<->6, 8<->11, 9<->10
antipode = [0]*12
pairs = [(0,3),(1,2),(4,7),(5,6),(8,11),(9,10)]
for a,b in pairs:
    antipode[a]=b
    antipode[b]=a

# Build additive LUT
additive_lut = np.zeros(4096, dtype=np.uint16)
w1_out = np.zeros(12, dtype=np.uint16)
for ch in range(12):
    w1_out[ch] = 1 << antipode[ch]
for s in range(4096):
    out = 0
    for ch in range(12):
        if (s >> ch) & 1:
            out |= w1_out[ch]
    additive_lut[s] = out

# Build a non-additive LUT: keep additive for weight != 2, 
# but for orbit 2 (rep=3), use target 48 instead of additive target
modified_lut = additive_lut.copy()

# For orbit 2 (rep=3, size=12), valid targets with same stabilizer: [3, 12, 48, 192]
# In additive: 3 -> 12
# Let's try 3 -> 48
rep = 3
target = 48
for g in range(len(perms)):
    s = int(action[g, rep])
    d = int(action[g, target])
    modified_lut[s] = d

# Check if this is bijective
unique = len(np.unique(modified_lut))
print(f"Modified LUT unique outputs: {unique} (should be 4096)")

# Check O_h symmetry
sym_ok = True
for g in range(len(perms)):
    lhs = modified_lut[action[g]]
    rhs = action[g, modified_lut]
    if not np.array_equal(lhs, rhs):
        sym_ok = False
        print(f'Symmetry violated at perm {g}')
        break
print(f'O_h symmetric: {sym_ok}')

# Check bit conservation
pops_in = np.array([bin(s).count('1') for s in range(4096)])
pops_out = np.array([bin(int(modified_lut[s])).count('1') for s in range(4096)])
print(f'Bit conserving: {np.array_equal(pops_in, pops_out)}')

# Specifically check weight-2 states
w2_states = [s for s in range(4096) if hamming(s) == 2]
w2_out = [int(modified_lut[s]) for s in w2_states]
print(f'All weight-2 outputs are weight-2: {all(hamming(o) == 2 for o in w2_out)}')
print(f'Weight-2 outputs unique: {len(set(w2_out))} == {len(w2_out)}: {len(set(w2_out)) == len(w2_out)}')

# Check weight-3 outputs
w3_states = [s for s in range(4096) if hamming(s) == 3]
w3_out = [int(modified_lut[s]) for s in w3_states]
print(f'All weight-3 outputs are weight-3: {all(hamming(o) == 3 for o in w3_out)}')
print(f'Weight-3 outputs unique: {len(set(w3_out))} == {len(w3_out)}: {len(set(w3_out)) == len(w3_out)}')

# Show an example of the modified orbit
print("\nOrbit 2 mapping (rep=3):")
for g in range(min(12, len(perms))):
    s = int(action[g, 3])
    d_old = int(additive_lut[s])
    d_new = int(modified_lut[s])
    print(f"  state {s} -> old={d_old}, new={d_new}")
