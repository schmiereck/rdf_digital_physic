Write a Python module `src/engine_d4_spacetime_18.py` that implements a 3D+1 spacetime Lattice Gas Cellular Automaton (LGCA) on the D4 lattice with 18 channels per cell.

Do not use any custom runner response formats inside Python scripts. Just write a standard Python script and run it using the command line to verify it works.

Structure of `src/engine_d4_spacetime_18.py`:
1. Import numpy, math, itertools.
2. Define `D4_VECTORS_4D` (shape (18, 4)):
   - First 6 are temporal: (1,1,0,0), (0,0,1,1), (1,0,1,0), (0,1,0,1), (1,0,0,1), (0,1,1,0).
   - Next 12 are spatial: all 12 permutations of (1,-1,0,0).
3. Define shifts:
   - Temporal channels shift by their first 3 components (dx, dy, dz).
   - Spatial channels do not shift (shift = (0, 0, 0)).
4. Implement `project_to_3d(v4d)` which projects to 3D space.
5. Define `PROJECTED_VECTORS` (shape (18, 3)) as the projection of the 18 D4 vectors.
6. Generate all 48 signed permutations in 3D. For each, find the induced permutation of {0,...,17} on the projected vectors. Store this in `OH_GROUP` (length 48, each element is a tuple of length 18).
7. Implement orbit decomposition on the 2^18 = 262,144 states. For each orbit, compute the signature: Hamming weight, orbit size, stabilizer subgroup, and spatial momentum vector.
8. Implement `generate_symmetric_lut(seed)`:
   - Group orbits by signature (weight, size, stabilizer, momentum vector).
   - For each group of orbits, permute them randomly and pair them.
   - For each paired orbit, pick a representative, find a target candidate that is invariant under the stabilizer, and construct the full mapping equivariantly.
   - Verify that the resulting LUT is a bijection, preserves bits, and preserves spatial momentum.
9. Implement `stream(grid, reverse=False)` and `collide(grid, lut)` on grids of shape (L, L, L, 18).
10. Add a self-test when run as a script to verify that on a 4x4x4 grid, streaming and collision preserve bits and momentum exactly.

Write the code to `src/engine_d4_spacetime_18.py`, run it as a script to verify it is error-free, and print out the results.