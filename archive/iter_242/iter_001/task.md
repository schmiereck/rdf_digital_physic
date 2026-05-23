Create a script `src/test_vacuum_charge.py` that loads the canonical LUT-08 glider and its LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
The script should:
1. Reconstruct the Cartesian coordinate projection mapping `BT` and its inverse.
2. Verify that the inverse mapping transforms grid shifts `SHIFTS` to Cartesian `fcc_neighbor_vectors`.
3. Simulate the glider in vacuum for 100 steps on a 32^3 grid.
4. At each step, identify the positions of the 4 occupied bits, convert their grid positions to Cartesian coordinates, sort them lexicographically, and compute:
   - The signed volume of the tetrahedron formed by the 4 bits: \(\chi = (\mathbf{r}_2 - \mathbf{r}_1) \cdot [(\mathbf{r}_3 - \mathbf{r}_1) \times (\mathbf{r}_4 - \mathbf{r}_1)]\)
   - The sub-lattice occupancy \(\mathbf{q} = (q_0, q_1, q_2, q_3) \in \mathbb{Z}^4\) based on Cartesian coordinate parities (all even, two-odd-one-even parity classes).
5. Print these values for the first 50 steps.
6. Check if \(\chi(t)\) is invariant or periodic, and if \(\mathbf{q}(t)\) satisfies a cyclic permutation \(\mathbf{q}(t+1) = M \mathbf{q}(t)\).
Run the script and display its output.