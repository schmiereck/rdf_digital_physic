Write a Python script `src/test_vacuum_cpt.py` that loads the rule and reference glider from `archive/iter_224/results/glider_00_lut08_sub03.json`.
The script should:
1. Run the glider in vacuum on a 32^3 grid for 40 steps, saving each grid state.
2. Define the channel negation mapping: `T_ch = [1, 0, 3, 2, 5, 4, 9, 10, 11, 6, 7, 8]`.
3. Test 4 candidates for the CPT-reversed state at step 40:
   - Candidate A (P alone): Negate coordinates `(l, r, c) -> (-l, -r, -c)` on the torus, keep channel indices same.
   - Candidate B (T alone): Keep coordinates same, replace channel `ch` with `T_ch[ch]`.
   - Candidate C (PT combined): Negate coordinates AND replace channel `ch` with `T_ch[ch]`.
   - Candidate D (CPT with inverse rule): Reverses the coordinates AND channels, and evolves under the inverse LUT and inverse stream.
4. For each candidate, simulate 40 steps forward (for A, B, C under forward rule; for D under inverse rule).
5. Apply the corresponding inverse transformation to the final state and check if it matches the initial step 0 grid perfectly.
Run the script and output the results.