Write and run a python script `src/find_projection_mapping.py` to find the exact 3x3 projection matrix and 1-to-1 channel mapping between standard Cartesian FCC vectors and `SHIFTS` in `engine_3d.py`.

The script must:
1. Import `SHIFTS` from `engine_3d`.
2. Import `fcc_neighbor_vectors` from `search_3d_gliders`.
3. S is the 12x3 matrix of `SHIFTS`.
4. C is the 12x3 matrix of Cartesian FCC neighbors.
5. Solve for the 3x3 matrix M_proj that maps C to S: M_proj = S.T @ np.linalg.pinv(C).T.
6. Verify if M_proj maps each row of C to a row of S. Find the exact permutation map `C_to_S` (a list of 12 indices) such that `S[C_to_S[i]]` is equal to `M_proj @ C[i]` (rounded) for all i=0..11.
7. Print `M_proj` and `C_to_S`.
8. Check if we can translate the 48 Cartesian permutations `perms = get_oh_permutations()` to projected permutations:
   `perm_proj[C_to_S[i]] = C_to_S[perm_cart[i]]`
9. For each of the 48 translated permutations, compute `M_g = S_rot.T @ np.linalg.pinv(S).T`, where `S_rot[i] = S[perm_proj[i]]`.
10. Check if the maximum reconstruction error `max_err = np.max(np.abs(S @ M_g.T - S_rot))` over all 48 permutations is extremely small (< 1e-12).
11. Print the results. Ensure this runs successfully.