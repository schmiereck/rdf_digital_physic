import numpy as np
from src.engine_3d import SHIFTS
from src.search_3d_gliders import get_oh_permutations

S = np.array(SHIFTS, dtype=float)
S_pinv = np.linalg.pinv(S)
perms = get_oh_permutations()
print('SHIFTS shape:', S.shape)
print('S_pinv shape:', S_pinv.shape)

for g, perm in enumerate(perms):
    S_rot = np.array([S[perm[i]] for i in range(12)], dtype=float)
    M_g = S_rot.T @ S_pinv.T
    pred = S @ M_g.T
    err = np.max(np.abs(pred - S_rot))
    # Check if M_g is orthogonal/reflection (det is +/- 1)
    det = np.linalg.det(M_g)
    print(f'Perm {g:02d}: err={err:.6f}, det={det:.6f}')
