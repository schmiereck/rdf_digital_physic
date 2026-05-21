Create a robust, fully-tested Python module `src/engine_d4_spacetime_18.py` that implements a 3D+1 spacetime Lattice Gas Cellular Automaton (LGCA) on the D4 lattice with 18 channels per cell.

Key requirements:
1. Define the 18 channels:
   - 6 future-directed temporal channels (T = (x+y+z+w)/2 = 1, x^2+y^2+z^2+w^2 = 2): these propagate to future-directed neighbors with spatial shifts (dx, dy, dz) as defined in engine_d4_spacetime.py.
   - 12 spatial channels (dT = 0, x^2+y^2+z^2+w^2 = 2): these do not move across the grid (shift = (0, 0, 0)).
2. Implement project_to_3d() to get the 3D physical coordinates (X, Y, Z) for both the 6 temporal and 12 spatial vectors in the projected 3D space, which define their physical velocity vectors.
3. Construct the O_h symmetry group: all 48 signed permutations acting on the 18 channels. Verify that the group action on the 18 channels is closed and forms unique permutations of {0,...,17}.
4. Perform orbit decomposition of the 2^{18} (262,144) states under O_h. For each orbit, compute the signature: (Hamming weight, orbit size, stabilizer subgroup, and spatial momentum vector).
5. Implement a generator `generate_symmetric_lut(seed)` that builds a bijective, bit-conserving, momentum-conserving, and O_h-symmetric LUT of size 262,144. To ensure non-trivial physics, the generator should pair orbits that have the same Hamming weight, same momentum vector, and compatible stabilizers, and map them bijectively.
6. Implement `stream(grid, reverse=False)` and `collide(grid, lut)` functions for a 3D grid of shape (L, L, L, 18).
7. Implement verification helpers to check:
   - LUT bijection
   - LUT bit conservation
   - LUT momentum conservation
   - LUT O_h symmetry
   - Grid reversibility
   - Grid bit and momentum conservation
8. Run a self-test when the file is executed as a script (e.g., verifying a grid round-trip and conservation on a small 4x4x4 grid over multiple steps).

Ensure the code is clean, well-commented, and robust.