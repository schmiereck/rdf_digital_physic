import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors, get_oh_permutations

def debug_oh_transforms():
    S = np.array(SHIFTS, dtype=float)
    S_pinv = np.linalg.pinv(S)
    C = fcc_neighbor_vectors().astype(float)
    C_pinv = np.linalg.pinv(C)
    B = S.T @ C_pinv.T
    
    print("S shape:", S.shape)
    print("C shape:", C.shape)
    print("B shape:", B.shape)
    
    P = []
    for i in range(12):
        v_proj = B @ C[i]
        diffs = np.linalg.norm(S - v_proj, axis=1)
        j = np.argmin(diffs)
        print(f"C[{i}] = {C[i]} -> v_proj = {v_proj} -> closest S[{j}] = {S[j]}, diff = {diffs[j]}")
        P.append(j)
        
    print("P:", P)
    if len(set(P)) < 12:
        print("WARNING: P is not a permutation! Unique elements:", len(set(P)))
        
    perms_cart = get_oh_permutations()
    print("Loaded", len(perms_cart), "Cartesian permutations")
    
    max_err = 0.0
    for idx, p_cart in enumerate(perms_cart):
        p_proj = [0] * 12
        for i in range(12):
            p_proj[P[i]] = P[p_cart[i]]
        p_proj = tuple(p_proj)
        S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        err = np.max(np.abs(S @ M_g.T - S_rot))
        if err > max_err:
            max_err = err
            print(f"Perm {idx} err = {err}")
    print("Max error:", max_err)

if __name__ == "__main__":
    debug_oh_transforms()
