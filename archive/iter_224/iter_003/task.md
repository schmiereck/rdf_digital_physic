Design and implement a symmetric, bit-conserving, reversible 3D CA rule generator and search for 3D gliders in `src/search_3d_gliders.py`.

Requirements:
1. Symmetries of the Cuboctahedron:
   - Generate the 48 permutations of {0..11} corresponding to the O_h symmetry group of the cuboctahedron.
   - To do this, represent the 12 nearest-neighbor vectors of the FCC lattice in R^3, apply all 48 signed permutation matrices of coordinate transformations, and find the corresponding permutations on the indices 0..11.
2. Orbit Decomposition:
   - Partition the 4096 states of {0, 1}^12 into orbits under the O_h group.
   - Group the orbits by Hamming weight.
3. Symmetric LUT Generation:
   - Implement a function `generate_symmetric_lut()` that creates a bijective, bit-conserving LUT of size 4096 that is invariant under the O_h symmetry group.
   - To ensure symmetry, any state s in an orbit O_1 must be mapped to a state s' in an orbit O_2 such that the mapping commutes with the O_h symmetry group. If O_1 is mapped to O_2, then they must have the same size and same Hamming weight, and the mapping of canonical representatives must preserve their stabilizers.
   - Alternatively, you can map each orbit to itself using a symmetric permutation (e.g., identity, or a permutation that commutes with the group action).
   - Let's verify that the generated LUT is indeed a bijection, is bit-conserving, and is fully symmetric under all 48 O_h permutations.
4. Glider Search:
   - Seed a periodic 3D grid of shape (16, 16, 16, 12) with a small, asymmetric particle (e.g., 3-6 bits placed close to the center of the grid, or a random local configuration).
   - Simulate for 100 steps using `src/engine_3d.py`.
   - Calculate the 3D center of mass (unwrapped to handle torus boundaries) and bit count over time.
   - Find rules where:
     - The bit count remains exactly stable (or periodic).
     - The net 3D displacement of the center of mass is non-zero (velocity > 0).
     - The particle does not expand or decay (size stays bounded).
5. Implement and run this search in `src/search_3d_gliders.py`. Print detailed logs of any discovered 3D gliders and save the best rules to `archive/iter_224/results/`. Run the script and report the results.