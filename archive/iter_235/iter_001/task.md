Create a python script `src/check_oh_transform.py`. This script should:
1. Load `SHIFTS` from `src/engine_3d.py`.
2. Generate the 48 channel permutations using `get_oh_permutations()` from `src/search_3d_gliders.py`.
3. For each permutation, compute the corresponding 3x3 spatial rotation/reflection matrix $M_g$ that maps the 12 shifts under the permutation (i.e., $S[\sigma_g(i)] = M_g S[i]$ for all $i$).
4. Verify that $M_g$ is indeed an orthogonal matrix with entries in $\{-1, 0, 1\}$ (a signed permutation matrix), and that the permutation holds exactly for all 12 shifts.
5. Create a function `transform_particle(particle, g)` that rotates/reflects a glider particle (its cell offsets and channel indices) under permutation $g$.
6. Test transforming the standard LUT-08 glider particle under all 48 permutations, verifying that the transformed particles are valid and preserve bit counts.
7. Run the script and output the results to a file `archive/iter_235/results/oh_transform_check.txt`.
