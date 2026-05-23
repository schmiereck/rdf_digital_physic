#!/usr/bin/env python3
import sys
from pathlib import Path
import numpy as np

# Ensure src is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors, get_oh_permutations

def main():
    # 1. Import SHIFTS from engine_3d
    # 2. Import fcc_neighbor_vectors from search_3d_gliders
    # 3. S is the 12x3 matrix of SHIFTS
    S = np.array(SHIFTS, dtype=float)
    
    # 4. C is the 12x3 matrix of Cartesian FCC neighbors
    C = fcc_neighbor_vectors().astype(float)
    
    # 5. Find the 3x3 matrix B that maps Cartesian to projected coordinates: B = S.T @ np.linalg.pinv(C).T
    C_pinv = np.linalg.pinv(C)
    B = S.T @ C_pinv.T
    
    print("Matrix B:")
    print(B)
    
    # 6. For each Cartesian neighbor C[i] (i=0..11), compute its projected vector v_proj = B @ C[i].
    # Find which row S[j] of S is closest to v_proj.
    # This defines a 1-to-1 permutation map P of length 12 such that P[i] = j.
    P = []
    for i in range(12):
        v_proj = B @ C[i]
        diffs = np.linalg.norm(S - v_proj, axis=1)
        j = np.argmin(diffs)
        # Check if they are extremely close
        if diffs[j] > 1e-10:
            print(f"Warning: minimum distance for C[{i}] is {diffs[j]:.2e}")
        P.append(j)
    
    print(f"Mapping P: {P}")
    
    # 7. Verify that P is indeed a bijection (contains all numbers 0..11)
    is_bijection = len(set(P)) == 12 and sorted(P) == list(range(12))
    print(f"P is bijection: {is_bijection}")
    assert is_bijection, "P is not a bijection!"
    
    # 8. Compute the inverse mapping P_inv of length 12 such that P_inv[P[i]] = i
    P_inv = [0] * 12
    for i in range(12):
        P_inv[P[i]] = i
    print(f"P_inv: {P_inv}")
    
    # 9. The 48 Cartesian permutations are perms_cart = get_oh_permutations()
    perms_cart = get_oh_permutations()
    print(f"Loaded {len(perms_cart)} Cartesian permutations.")
    
    # 10. For each Cartesian permutation p_cart, its corresponding projected permutation p_proj is:
    # p_proj[P[i]] = P[p_cart[i]] for all i=0..11.
    # 11. With this p_proj, compute the 3x3 coordinate transform matrix M_g = S_rot.T @ np.linalg.pinv(S).T,
    # where row i of S_rot is S[p_proj[i]].
    # 12. Verify that the reconstruction error err = np.max(np.abs(S @ M_g.T - S_rot)) is extremely small (< 1e-12) for all 48 permutations!
    max_error = 0.0
    S_pinv = np.linalg.pinv(S)
    
    for idx, p_cart in enumerate(perms_cart):
        p_proj = [0] * 12
        for i in range(12):
            p_proj[P[i]] = P[p_cart[i]]
        
        # Verify p_proj is also a bijection
        assert len(set(p_proj)) == 12 and sorted(p_proj) == list(range(12))
        
        S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        
        err = np.max(np.abs(S @ M_g.T - S_rot))
        if err > max_error:
            max_error = err
            
    print(f"Maximum reconstruction error over all 48 permutations: {max_error:.2e}")
    assert max_error < 1e-12, f"Reconstruction error too large! {max_error:.2e}"
    print("SUCCESS: Zero-error O_h coordinate transformation matrices verified!")

if __name__ == "__main__":
    main()
