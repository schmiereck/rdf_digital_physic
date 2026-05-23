import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors, get_oh_permutations

def find_exact_mapping():
    # 1. Load SHIFTS as S
    S = np.array(SHIFTS, dtype=float)  # (12, 3)
    
    # 2. Load fcc_neighbor_vectors as C
    C = fcc_neighbor_vectors().astype(float)  # (12, 3)
    
    # 3. Find distinct indices i0, i1, i2 in C
    n = len(C)
    working_i = None
    working_BT = None
    working_P = None
    working_max_err = None
    
    # Let's search all distinct indices i0, i1, i2
    for i0 in range(n):
        for i1 in range(n):
            if i1 == i0:
                continue
            for i2 in range(n):
                if i2 == i0 or i2 == i1:
                    continue
                
                C_sub = C[[i0, i1, i2]]
                # Check invertibility
                if np.abs(np.linalg.det(C_sub)) < 1e-5:
                    continue
                
                # Compute candidate B^T = inv(C_sub) S[[0, 2, 6]]
                S_sub = S[[0, 2, 6]]
                BT_cand = np.linalg.inv(C_sub) @ S_sub
                
                # 4. Check if the candidate B^T projects C to S bijectively
                # we want for each i in C, C[i] @ BT_cand has a matching S[j] with dist < 1e-10
                P_cand = [-1] * 12
                valid = True
                max_err = 0.0
                
                for i in range(12):
                    v_proj = C[i] @ BT_cand
                    # find closest S[j]
                    dists = np.linalg.norm(S - v_proj, axis=1)
                    j = np.argmin(dists)
                    err = dists[j]
                    if err >= 1e-10:
                        valid = False
                        break
                    P_cand[i] = int(j)
                    max_err = max(max_err, err)
                
                if not valid:
                    continue
                
                # Check bijectivity: all elements of P_cand must be unique
                if len(set(P_cand)) != 12:
                    continue
                
                # We found a working one!
                working_i = (i0, i1, i2)
                working_BT = BT_cand
                working_P = P_cand
                working_max_err = max_err
                break
            if working_BT is not None:
                break
        if working_BT is not None:
            break
            
    if working_BT is None:
        print("Failed to find a working mapping!")
        return
        
    print(f"Working indices in C: i0={working_i[0]}, i1={working_i[1]}, i2={working_i[2]}")
    print("Exact B^T matrix:")
    print(working_BT)
    print("Exact 1-to-1 mapping P (Cartesian -> Projected):")
    print(working_P)
    print(f"Max projection error: {working_max_err}")
    
    # 6. Verify 48 O_h permutations reconstruction on S with error < 1e-12
    perms_cart = get_oh_permutations()
    transforms = []
    max_rec_err = 0.0
    S_pinv = np.linalg.pinv(S)
    
    for idx, p_cart in enumerate(perms_cart):
        p_proj = [0] * 12
        for i in range(12):
            p_proj[working_P[i]] = working_P[p_cart[i]]
        p_proj = tuple(p_proj)
        
        # reconstruct M_g
        S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        err = np.max(np.abs(S @ M_g.T - S_rot))
        max_rec_err = max(max_rec_err, err)
        transforms.append((p_proj, M_g))
        
    print(f"Max O_h reconstruction error: {max_rec_err}")
    assert max_rec_err < 1e-12, f"Reconstruction error too large: {max_rec_err}"
    print("O_h reconstruction verified successfully!")
    
    # 7. Print python code for build_oh_transforms()
    print("\n--- Python code for build_oh_transforms() ---")
    # Let's write the code block
    code = f"""def build_oh_transforms():
    \"\"\"Exact O_h transforms on projected shifts S (12x3).
    Reconstructed using 3-vector linear independence solver.
    \"\"\"
    import numpy as np
    from src.engine_3d import SHIFTS
    from src.search_3d_gliders import fcc_neighbor_vectors, get_oh_permutations
    
    S = np.array(SHIFTS, dtype=float)
    C = fcc_neighbor_vectors().astype(float)
    
    # Selected indices from 3-vector solver
    i0, i1, i2 = {working_i[0]}, {working_i[1]}, {working_i[2]}
    C_sub = C[[i0, i1, i2]]
    S_sub = S[[0, 2, 6]]
    
    BT = np.linalg.inv(C_sub) @ S_sub
    
    # Bijective mapping P (Cartesian -> Projected)
    P = {working_P}
    
    S_pinv = np.linalg.pinv(S)
    perms_cart = get_oh_permutations()
    
    transforms = []
    for p_cart in perms_cart:
        p_proj = [0] * 12
        for i in range(12):
            p_proj[P[i]] = P[p_cart[i]]
        p_proj = tuple(p_proj)
        
        S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        transforms.append((p_proj, M_g))
        
    return transforms
"""
    print(code)

if __name__ == "__main__":
    find_exact_mapping()
