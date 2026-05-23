import numpy as np
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.search_3d_gliders import get_oh_permutations

SHIFTS = [
    (0, 1, 0),    # Channel 0: dl=0, dr=1, dc=0
    (0, -1, 0),   # Channel 1: dl=0, dr=-1, dc=0
    (0, 0, 1),    # Channel 2: dl=0, dr=0, dc=1
    (0, 0, -1),   # Channel 3: dl=0, dr=0, dc=-1
    (0, 1, -1),   # Channel 4: dl=0, dr=1, dc=-1
    (0, -1, 1),   # Channel 5: dl=0, dr=-1, dc=1
    (1, 1, 1),    # Channel 6: dl=1, dr=1, dc=1
    (1, 1, 0),    # Channel 7: dl=1, dr=1, dc=0
    (1, 0, 1),    # Channel 8: dl=1, dr=0, dc=1
    (-1, -1, -1), # Channel 9: dl=-1, dr=-1, dc=-1
    (-1, -1, 0),  # Channel 10: dl=-1, dr=-1, dc=0
    (-1, 0, -1),  # Channel 11: dl=-1, dr=0, dc=-1
]

perms = get_oh_permutations()
S = np.array(SHIFTS, dtype=float)
S_pinv = np.linalg.pinv(S)

v_A = np.array([0.5, 0.0, 1.0])

for g, perm in enumerate(perms):
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    M_g = S_rot.T @ S_pinv.T
    det = np.linalg.det(M_g)
    is_ortho = np.allclose(M_g.T @ M_g, np.eye(3))
    
    # Let's apply M_g to v_A
    v_rot = M_g @ v_A
    if np.allclose(v_rot, -v_A):
         print(f"Perm {g}: det={det:.1f}, ortho={is_ortho}, v_rot={v_rot}")
