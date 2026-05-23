Write `src/glider_charge_analysis.py` to systematically analyze the chirality \(\chi(t)\) and sub-lattice charge vector \(\mathbf{q}(t)\) of the canonical LUT-08 glider over 100 steps of vacuum propagation, and verify their properties under spatial reflection.

Make the script under 110 lines of clean, self-contained Python.
The script should:
1. Reconstruct `BT` and `BT_inv` projection matrices.
2. Load the canonical LUT-08 glider and its LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
3. Verify that the bits are mapped back to Cartesian FCC space.
4. Run a 100-step simulation of the glider in vacuum.
5. At each step \(t\):
   - Compute Cartesian coordinates of the 4 bits: \(\mathbf{r}_i = \text{cell\_position} \cdot B_{\text{inv}}^T\).
   - Sort them lexicographically to ensure order invariance.
   - Compute the signed volume: \(\chi(t) = (\mathbf{r}_2 - \mathbf{r}_1) \cdot [(\mathbf{r}_3 - \mathbf{r}_1) \times (\mathbf{r}_4 - \mathbf{r}_1)]\).
   - Categorize each bit's Cartesian coordinate into the 4 sub-lattices:
     - \(L_0\): all even
     - \(L_1\): \(x, y\) odd, \(z\) even
     - \(L_2\): \(x, z\) odd, \(y\) even
     - \(L_3\): \(y, z\) odd, \(x\) even
     Keep in mind the coordinates might be slightly off due to floating point precision, so round them to integers before checking parities.
     Compute the occupancy vector \(\mathbf{q}(t) = (q_0, q_1, q_2, q_3)\).
6. Verify if \(\chi(t)\) is invariant (modulo phase translation) and check if \(\mathbf{q}(t)\) satisfies a cyclic permutation permutation matrix \(M\).
7. Perform a spatial reflection of the glider's Cartesian coordinates (e.g., \(x \to -x\)), project it back to grid coordinates using `BT` to get the reflected grid particle representation, and simulate it in vacuum for 100 steps. Verify its stability and that its chirality is exactly \(-\chi(t)\).
8. Print a detailed step-by-step log of \(\chi(t)\) and \(\mathbf{q}(t)\), print the verified cyclic permutation matrix \(M\), and verify the reflection properties.
Write and run this script, and display its output.