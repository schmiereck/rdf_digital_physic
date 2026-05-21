Create the python file `src/engine_d4_spacetime_18.py` that implements the 18-channel D4 LGCA.

Write a complete, high-quality, fully documented script that implements:
1. Classification of channels:
   - 6 temporal vectors in 4D: D4_VECTORS_4D[:6] = [
       [1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]
     ]
   - 12 spatial vectors in 4D: all 12 permutations of [1, -1, 0, 0].
2. Spatial shifts on the 3D grid:
   - Temporal channels shift by their first 3 components: (dx, dy, dz) from D4_VECTORS_4D[i][:3].
   - Spatial channels do not shift: (0, 0, 0).
3. Orthogonal projection `project_to_3d(v4d)` using:
   - X = (x - y + z - w) // 2
   - Y = (x - y - z + w) // 2
   - Z = (x + y - z - w) // 2
   (Note: Use integer division since all components are even or balance to integers. Or use float and round/cast to int).
4. Symmetries: Construct the 48 signed permutation matrices in 3D. For each, find the induced permutation of {0,...,17} on the projected vectors. Store as `OH_GROUP` (list of 48 tuples of length 18).
5. State packing and unpacking between 18-bit integers and numpy boolean arrays of shape (..., 18).
6. Orbit decomposition of states in range(262144). For each state, apply all 48 permutations to find its orbit. Store as a list of orbits.
7. Orbit signature: (Hamming weight, size, stabilizer subgroup, and integer momentum vector).
8. `generate_symmetric_lut(seed)`:
   - Group orbits by signature.
   - For each signature group, pair them randomly (or map each orbit to itself/another orbit in the group) based on a random seed.
   - For each paired orbit, construct the mapping of the representatives and extend it equivariantly to all states in the orbits.
   - Verify that the resulting LUT is bijective, preserves bits, and preserves spatial momentum exactly.
9. `stream(grid, reverse=False)` and `collide(grid, lut)` for a grid of shape (L, L, L, 18).
10. A `main()` self-test to verify:
   - Number of temporal/spatial vectors (6 and 12).
   - Orbit decomposition covers all 262,144 states.
   - LUT is bijective and conserved.
   - A grid of size 4x4x4 initialized with some random bits undergoes 10 forward steps and 10 reverse steps, successfully recovering the initial grid, while preserving both bit count and total momentum at each step.

Write the code and run it as a script to verify that it is completely correct and prints details.