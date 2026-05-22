Write a Python script `src/check_oh_transform.py`. This script must:
1. Import `SHIFTS` from `src/engine_3d.py`.
2. Generate the 48 permutations of FCC channels from `get_oh_permutations()` in `src/search_3d_gliders.py`.
3. For each of the 48 permutations, construct the unique 3x3 signed permutation matrix $M_g$ representing the rotation/reflection.
4. Verify that $S[\sigma_g(i)] = M_g S[i]$ holds exactly for all 12 channels.
5. Implement a function `transform_particle(particle, g)` that rotates the cell offsets `(dl, dr, dc)` using $M_g$ and maps the channel `ch` using $\sigma_g$.
6. For each permutation $g \in \{0..47\}$, print out the rotated version of the standard LUT-08 sub-light glider particle.
7. Run the script and write the verified results to a text file: `archive/iter_235/results/oh_transform_check.txt`. Make sure the file contains the detailed list of rotated particles for each of the 48 permutations.
Verify that the python script can be executed successfully without any errors.
