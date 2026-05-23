import numpy as np
from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors

vecs = fcc_neighbor_vectors()
print("FCC Neighbor Vectors:")
for i, v in enumerate(vecs):
    print(f"  {i:2d}: {list(v)}")

print("\nSHIFTS:")
for i, s in enumerate(SHIFTS):
    print(f"  {i:2d}: {list(s)}")
