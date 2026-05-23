import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors

def main():
    S = np.array(SHIFTS, dtype=float)
    C = fcc_neighbor_vectors().astype(float)
    
    i0, i1, i2 = 0, 4, 8
    C_sub = C[[i0, i1, i2]]
    S_sub = S[[0, 2, 6]]
    
    BT = np.linalg.inv(C_sub) @ S_sub
    print("BT:")
    print(BT)
    
    P = [0, 10, 7, 1, 2, 11, 8, 3, 6, 4, 5, 9]
    for i in range(12):
        v_proj = C[i] @ BT
        j = P[i]
        diff = np.linalg.norm(v_proj - S[j])
        print(f"C[{i}] = {C[i]} projected: {v_proj} matches S[{j}] = {S[j]} (diff = {diff:.6e})")

    # Now verify inverse mapping transforms grid shifts to Cartesian fcc_neighbor_vectors
    BT_inv = np.linalg.inv(BT)
    print("\nBT_inv:")
    print(BT_inv)
    
    for i in range(12):
        j = P[i]
        # s @ BT_inv should map back to c
        v_back = S[j] @ BT_inv
        diff_back = np.linalg.norm(v_back - C[i])
        print(f"S[{j}] = {S[j]} mapped back: {v_back} matches C[{i}] = {C[i]} (diff = {diff_back:.6e})")

if __name__ == "__main__":
    main()
