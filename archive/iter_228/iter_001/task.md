Create a robust, fully-tested Python module `src/engine_d4_spacetime.py` that implements a 3D+1 spacetime Lattice Gas Cellular Automaton (LGCA) on the D4 lattice.

Key requirements:
1. Define the 6 channels corresponding to the 6 future-directed light-like D4 vectors:
   - D0 = (1, 1, 0, 0) -> spatial shift (1, 1, 0)
   - D1 = (0, 0, 1, 1) -> spatial shift (0, 0, 1)
   - D2 = (1, 0, 1, 0) -> spatial shift (1, 0, 1)
   - D3 = (0, 1, 0, 1) -> spatial shift (0, 1, 0)
   - D4 = (1, 0, 0, 1) -> spatial shift (1, 0, 0)
   - D5 = (0, 1, 1, 0) -> spatial shift (0, 1, 1)

2. Implement the Octahedral Symmetry Group ($O_h$) of 48 permutations acting on the 6 channels:
   - To do this, represent each channel as a 3D projected vector $(X, Y, Z)$ as defined by the projection:
     X = (x - y) / sqrt(2)
     Y = (z - w) / sqrt(2)
     Z = (x + y - z - w) / 2
     where (x, y, z, w) are the 4D coordinates of the 6 D4 vectors (D0..D5).
   - Generate all 48 signed permutation matrices in 3D. Apply each matrix to the 6 projected vectors. If a matrix maps the set of 6 vectors to itself, record the induced permutation of $\{0, 1, 2, 3, 4, 5\}$. Verify that we obtain exactly 48 unique permutations of $\{0, 1, 2, 3, 4, 5\}$.

3. Perform Orbit Decomposition of the 64 states of $\{0, 1\}^6$:
   - Group the 64 states into orbits under the action of the 48 channel permutations.
   - For each orbit, compute its signature: (Hamming weight, orbit size, stabilizer subgroup).
   - Implement `generate_symmetric_lut(seed)` which builds an $O_h$-equivariant, bit-conserving, bijective (reversible) lookup table (LUT) of size 64. Ensure that orbits with matching signatures are paired equivariantly, extending the map $f(g \cdot r) = g \cdot t$ for all $g$.

4. Implement `stream(grid, reverse=False)`:
   - For a 3D numpy array of shape $(L, L, L, 6)$, roll the bits in channel $i$ by the respective 3D spatial shift $(dx_i, dy_i, dz_i)$ (or negative of that if reverse=True).

5. Implement `collide(grid, lut)`:
   - Pack the 6-channel bits into integers $0..63$, apply the LUT, and unpack.

6. Implement verification functions for Reversibility, Bit conservation, and $O_h$-symmetry of the LUT.

Write unit tests or a diagnostic script within the file (under `if __name__ == "__main__":`) to verify that the generated LUTs pass all checks (bijection, bit conservation, $O_h$-symmetry) and that the LGCA stream/collide functions are perfectly reversible. Run this file to verify correctness.