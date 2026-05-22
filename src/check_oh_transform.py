import os
import json
import numpy as np

from src.engine_3d import SHIFTS
from src.search_3d_gliders import get_oh_permutations

# S is (12, 3) shift vectors
S = np.array(SHIFTS, dtype=float)

# Compute pseudo-inverse of S of shape (3, 12)
S_pinv = np.linalg.pinv(S)

perms = get_oh_permutations()

results = []

# Verify each of the 48 permutations
for g, perm in enumerate(perms):
    # S_rot: row i is S[perm[i]]
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    
    # Compute the 3x3 matrix M_g such that S_rot = S @ M_g.T
    # This implies M_g = S_rot.T @ S_pinv.T
    M_g = S_rot.T @ S_pinv.T
    
    # Verify the mapping is exact
    pred = S @ M_g.T
    err = np.max(np.abs(pred - S_rot))
    
    M_g_rounded = np.round(M_g, 4)
    
    results.append({
        "g": g,
        "perm": perm,
        "M_g": M_g_rounded.tolist(),
        "err": float(err)
    })

# Write verification report
os.makedirs("archive/iter_235/results", exist_ok=True)
report_path = "archive/iter_235/results/oh_transform_check.txt"
with open(report_path, "w") as f:
    f.write("OCTAHEDRAL GROUP GRID COORDINATE TRANSFORM VERIFICATION\n")
    f.write("=====================================================\n\n")
    for r in results:
        f.write(f"Permutation {r['g']}:\n")
        f.write(f"  Channel Perm: {r['perm']}\n")
        f.write(f"  3x3 Matrix M_g:\n")
        for row in r['M_g']:
            f.write(f"    {row}\n")
        f.write(f"  Max Reconstruction Error: {r['err']:.2e}\n\n")

print(f"Verification complete. Max error over all 48 permutations is {max(r['err'] for r in results):.2e}")
