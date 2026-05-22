Create and execute a Python script `src/check_oh_transform.py`.

The script must:
1. Load `SHIFTS` from `src/engine_3d.py` as a 12x3 numpy array (S).
2. Generate the 48 channel permutations using `get_oh_permutations()` from `src/search_3d_gliders.py` (perms).
3. Compute the pseudo-inverse of S: `S_pinv = np.linalg.pinv(S.T)`.
4. For each of the 48 permutations g, construct `S_rot` of shape 12x3 where row `i` is `S[perms[g][i]]`.
5. Compute the 3x3 transformation matrix `M_g = S_rot.T @ S_pinv.T`.
6. Verify that `M_g @ S[i]` is exactly equal to `S[perms[g][i]]` for all 12 channels. If it is, then `M_g` is the exact 3D grid coordinate transformation matrix for permutation `g`.
7. Define a function `rotate_particle(particle, g, perms)` that takes the standard LUT-08 particle list (where each element is `(dl, dr, dc, ch)`) and returns the rotated particle where each cell's offset is rotated by `M_g` and its channel is mapped using `perms[g]`.
8. Write a report to `archive/iter_235/results/oh_transform_check.txt` detailing the 48 matrices and the rotated LUT-08 particles, and confirm that bit count is exactly preserved.

Please execute the script, make sure it runs without any errors, and write the report file.
