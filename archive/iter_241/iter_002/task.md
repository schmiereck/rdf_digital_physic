Write a robust Python script `src/fcc_symmetry.py` that implements the O_h symmetry group checker for the 3D FCC grid as specified.

Requirements:
1. Define fcc_neighbor_vectors() and get_oh_permutations() following the logic of src/search_3d_gliders.py.
2. Define SHIFTS from src/engine_3d.py.
3. Compute the basis change matrix B = S.T @ pinv(C).T and its inverse B_inv, where S is SHIFTS and C is Cartesian FCC vectors.
4. For each of the 48 octahedral symmetries, compute the projected transformation matrix M_proj = B @ M_cart @ B_inv, where M_cart is the 3x3 Cartesian signed-permutation matrix.
5. Implement translation_canonicalize(particle) which translates coordinates so the lexicographically-first bit is at (0, 0, 0) and sorts.
6. Implement rotate_particle(particle, g) which rotates cell coordinates by M_proj for symmetry index g and permutes the channel of each bit by the g-th channel permutation.
7. Implement get_lut08_orbit_shapes(lut_path) which loads the LUT-08 reference particle, simulates it for 40 steps (the period of LUT-08), extracts the canonical translated shape at each step, rotates all 40 shapes under all 48 O_h symmetries, and returns the union of these shapes as a set of tuples of tuples.
8. Implement is_lut08_equivalent(particle, lut08_orbit_shapes) which returns True if translation_canonicalize(particle) is in the set, and False otherwise.
9. Run a self-test when the script is executed to verify that the checker is perfectly accurate:
   - Groups all 48 rotated versions of the original LUT-08 particle into LUT-08 equivalents.
   - Accurately reports a random 4-bit particle as not equivalent.
   - Standard stdout success marker: "Symmetry self-test PASSED."

Write the script to `src/fcc_symmetry.py` and run it to verify it passes.