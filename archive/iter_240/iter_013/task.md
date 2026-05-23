Write and run a python script `src/find_perfect_permutation.py` that finds the exact mapping between Cartesian FCC neighbors and `SHIFTS` in `engine_3d.py` and uses it to construct the perfect, zero-error O_h coordinate transformation matrices on the (l, r, c) coordinates.

The script must:
1. Import `SHIFTS` from `engine_3d`.
2. Import `fcc_neighbor_vectors` from `search_3d_gliders`.
3. S is the 12x3 matrix of `SHIFTS`.
4. C is the 12x3 matrix of Cartesian FCC neighbors (from `fcc_neighbor_vectors()`).
5. Find the 3x3 matrix B that maps Cartesian to projected coordinates: B = S.T @ np.linalg.pinv(C).T.
6. For each Cartesian neighbor C[i] (i=0..11), compute its projected vector `v_proj = B @ C[i]`. Find which row S[j] of S is closest to `v_proj`. This defines a 1-to-1 permutation map `P` of length 12 such that `P[i] = j` (meaning Cartesian channel i corresponds to projected channel j).
7. Verify that P is indeed a bijection (contains all numbers 0..11).
8. Compute the inverse mapping `P_inv` of length 12 such that `P_inv[P[i]] = i`.
9. The 48 Cartesian permutations are `perms_cart = get_oh_permutations()`.
10. For each Cartesian permutation `p_cart`, its corresponding projected permutation `p_proj` is:
    `p_proj[P[i]] = P[p_cart[i]]` for all i=0..11.
11. With this `p_proj`, compute the 3x3 coordinate transform matrix `M_g = S_rot.T @ np.linalg.pinv(S).T`, where row i of `S_rot` is `S[p_proj[i]]`.
12. Verify that the reconstruction error `err = np.max(np.abs(S @ M_g.T - S_rot))` is extremely small (< 1e-12) for all 48 permutations!
13. Print the permutation `P` and the maximum reconstruction error.
14. If the error is small, rewrite `src/rigorous_glider_audit.py` to use this correct permutation mapping so that the O_h transforms are exact and have zero reconstruction error! Run the audit script and ensure it completes successfully and writes the audited files. Print the stdout of the audit!