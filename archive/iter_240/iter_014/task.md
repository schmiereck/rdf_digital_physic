1. Edit `src/rigorous_glider_audit.py` to fix `build_oh_transforms()` using the mapping B and P from Cartesian standard coordinates to projected layer-row-column coordinates.
   Specifically:
   - Import `fcc_neighbor_vectors` from `src.search_3d_gliders`.
   - In `build_oh_transforms()`, implement:
     ```python
     def build_oh_transforms():
         S = np.array(SHIFTS, dtype=float)
         S_pinv = np.linalg.pinv(S)
         C = fcc_neighbor_vectors().astype(float)
         C_pinv = np.linalg.pinv(C)
         B = S.T @ C_pinv.T
         P = []
         for i in range(12):
             v_proj = B @ C[i]
             diffs = np.linalg.norm(S - v_proj, axis=1)
             j = np.argmin(diffs)
             P.append(j)
         perms_cart = get_oh_permutations()
         transforms = []
         max_err = 0.0
         for p_cart in perms_cart:
             p_proj = [0] * 12
             for i in range(12):
                 p_proj[P[i]] = P[p_cart[i]]
             p_proj = tuple(p_proj)
             S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
             M_g = S_rot.T @ S_pinv.T
             err = np.max(np.abs(S @ M_g.T - S_rot))
             max_err = max(max_err, err)
             transforms.append((p_proj, M_g))
         assert max_err < 1e-10, f"O_h transform reconstruction error too large: {max_err}"
         return transforms
     ```
2. Run `python3 src/rigorous_glider_audit.py`.
3. Verify that the script executes cleanly, showing the exact number of unique O_h equivalence classes among the 163 candidates and reference, and whether they are STABLE or UNSTABLE.
4. If successful, print the summary of the output.