import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path('src').resolve()))
from engine_3d import SHIFTS
from search_3d_gliders import fcc_neighbor_vectors

S = np.array(SHIFTS, dtype=float)
C = fcc_neighbor_vectors().astype(float)

print("C (Cartesian FCC) norms:")
for i, c in enumerate(C):
    print(f"C[{i}] = {c}, norm^2 = {np.sum(c**2)}")

print("\nS (SHIFTS) norms:")
for i, s in enumerate(S):
    print(f"S[{i}] = {s}, norm^2 = {np.sum(s**2)}")
