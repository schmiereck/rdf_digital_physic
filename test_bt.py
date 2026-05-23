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
    B = BT.T
    print("B:")
    print(B)
    print("Determinant of B:", np.linalg.det(B))
    
    B_inv = np.linalg.inv(B)
    print("B_inv:")
    print(B_inv)

if __name__ == "__main__":
    main()
