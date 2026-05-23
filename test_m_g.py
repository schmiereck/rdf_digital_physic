import sys
import os
sys.path.append(os.path.abspath("src"))
import numpy as np
from search_3d_gliders import get_oh_permutations
from engine_3d import SHIFTS

S = np.array(SHIFTS, dtype=float)
S_pinv = np.linalg.pinv(S)
perms = get_oh_permutations()
for g in [0, 10]:
    perm = perms[g]
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    M_g = S_rot.T @ S_pinv.T
    print(f"g={g}:")
    print(M_g)
