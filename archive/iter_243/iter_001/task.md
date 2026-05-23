Write a python script `src/test_reversibility_and_cpt.py` that:
1. Loads the LUT-08 glider rule from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Sets up a grid with the glider.
3. Simulates 10 steps of the glider under the forward rule to get states S_0, S_1, ..., S_10.
4. Checks if the LUT is self-inverse, or what its inverse is.
5. Tests if applying channel reversal T (defined by T_map) to S_10, then simulating 10 steps forward (or using some other combination of T/inverse) reconstructs S_0 or T(S_0).
6. Tests if applying P (spatial reflection or spatial inversion) and T is required.
7. Print the results clearly to stdout.
Run this script and output the results.