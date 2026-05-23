Write a python script `src/rigorous_glider_audit.py` to rigorously audit, filter, and verify all 163 discovered gliders in `archive/iter_240/results/new_glider_*.json` and the reference LUT-08 glider in `archive/iter_224/results/glider_00_lut08_sub03.json`.

The script must:
1. Load all glider JSON files.
2. Implement the correct, full 48-element O_h group symmetry coordinate and channel transformations to canonicalize particles. Use the logic from `src/check_oh_transform.py` to compute the 3x3 coordinate transformation matrix M_g for each channel permutation `perm` of the 48 permutations. Specifically, for each of the 48 channel permutations, compute M_g = S_rot.T @ np.linalg.pinv(S).T, where S is the 12x3 matrix of SHIFTS and S_rot is S permuted by `perm`. This maps the (l, r, c) coordinates perfectly.
3. Canonicalize each particle under the full 48 O_h symmetries and group them into equivalence classes.
4. For each unique equivalence class:
   a. Run the representative particle for 200 steps (5 complete periods, since the period is 40 steps) on an L=32 toroidal grid in vacuum using `engine_3d.py`.
   b. Verify perfect bit conservation on every step.
   c. Verify that the bounding extent on every step is <= 6 (no growth/dispersal).
   d. Determine the exact period P (the smallest step where the canonical shape matches the initial canonical shape).
   e. Calculate the coordinate speed v_coord = ||cumulative_displacement|| / 200.
   f. Normalize the velocity against the speed of light c = sqrt(2) approx 1.41421356, i.e., v/c = v_coord / sqrt(2).
5. Identify which classes correspond to the reference LUT-08 glider class.
6. Print a detailed audit of each unique class.
7. Write a clean, audited JSON summary to `archive/iter_240/results/audited_glider_taxonomy.json` and a detailed markdown report to `archive/iter_240/results/audited_glider_taxonomy_report.md`.
8. Execute this script and report the output. Ensure there are no coordinate rounding errors or index out of bound issues during matrix multiplication (round coordinates to the nearest integer after matrix multiplication).