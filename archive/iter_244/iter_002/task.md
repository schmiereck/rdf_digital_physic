Create and execute a Python script `src/test_vacuum_cpt.py` that:
1. Loads the reference glider and LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Runs the glider in vacuum on a 32^3 grid for 40 steps, saving each grid state.
3. Applies a candidate CPT transformation to the step 40 state:
   - Try candidate 1: Spatial parity P alone (negating coordinates l, r, c on the torus).
   - Try candidate 2: Channel negation T alone (replacing each channel ch with T_ch[ch], where T_ch = [1, 0, 3, 2, 5, 4, 9, 10, 11, 6, 7, 8]).
   - Try candidate 3: PT combined (negating coordinates and channels).
   - Try candidate 4: CPT (where time reversal for a glider in a reversible CA uses the inverse LUT).
4. For each candidate, simulates 40 steps forward under the forward rule (with forward collide and stream), and then applies the same transformation again.
5. Checks if the final state matches the step 0 state.
Print the results of these 4 candidates and report which one (if any) successfully reconstructs the step 0 state.