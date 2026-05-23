import numpy as np
from itertools import permutations, product

def fcc_neighbor_vectors():
    vecs = []
    for i in range(3):
        for j in range(i + 1, 3):
            for si in (-1, 1):
                for sj in (-1, 1):
                    v = [0, 0, 0]
                    v[i] = si
                    v[j] = sj
                    vecs.append(tuple(v))
    return np.array(vecs, dtype=int)

SHIFTS = [
    (0, 1, 0),    # Channel 0
    (0, -1, 0),   # Channel 1
    (0, 0, 1),    # Channel 2
    (0, 0, -1),   # Channel 3
    (0, 1, -1),   # Channel 4
    (0, -1, 1),   # Channel 5
    (1, 1, 1),    # Channel 6
    (1, 1, 0),    # Channel 7
    (1, 0, 1),    # Channel 8
    (-1, -1, -1), # Channel 9
    (-1, -1, 0),  # Channel 10
    (-1, 0, -1),  # Channel 11
]

vecs = fcc_neighbor_vectors()
S = np.array(SHIFTS, dtype=float)

# Let's find three linearly independent vectors in vecs.
# For example: vecs[0], vecs[4], vecs[8]
# vecs[0] = (1, 1, 0), vecs[4] = (1, 0, 1), vecs[8] = (0, 1, 1)
v_indices = [0, 4, 8]
V_sub = vecs[v_indices].T # shape (3, 3)
assert np.abs(np.linalg.det(V_sub)) > 1e-5

# We search for three indices in SHIFTS: i0, i1, i2
found = False
for i0, i1, i2 in permutations(range(12), 3):
    S_sub = S[[i0, i1, i2]].T # shape (3, 3)
    if np.abs(np.linalg.det(S_sub)) < 1e-5:
        continue
    # A = S_sub @ V_sub^-1
    A = S_sub @ np.linalg.inv(V_sub)
    
    # Check if this A maps each vector in vecs to some vector in S in a 1-to-1 manner
    mapped_indices = []
    ok = True
    for v in vecs:
        Sv = A @ v
        # Find if Sv is in SHIFTS
        diffs = np.linalg.norm(S - Sv, axis=1)
        closest = np.argmin(diffs)
        if diffs[closest] < 1e-5:
            mapped_indices.append(closest)
        else:
            ok = False
            break
    if ok and len(set(mapped_indices)) == 12:
        print("Success!")
        print("Matrix A:")
        print(A)
        print("Mapping from vecs index to SHIFTS index:")
        print(mapped_indices)
        # Check if A preserves the group structure or is an isomorphism
        found = True
        break

if not found:
    print("Could not find a linear mapping!")
