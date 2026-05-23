import numpy as np
import sys
from pathlib import Path

# Insert the parent directory to sys.path so we can import src
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors, get_oh_permutations

def main():
    S = np.array(SHIFTS, dtype=float)
    C = fcc_neighbor_vectors().astype(float)
    print("S shape:", S.shape)
    print("C shape:", C.shape)
    
    # B = S.T @ pinv(C).T
    pinv_C = np.linalg.pinv(C)
    B = S.T @ pinv_C.T
    print("B:")
    print(B)
    
    B_inv = np.linalg.inv(B)
    print("B_inv:")
    print(B_inv)

if __name__ == "__main__":
    main()
