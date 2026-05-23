Write a Python script `src/test_vacuum_cpt.py` that implements a rigorous check of CPT-reversibility in vacuum for the LUT-08 glider.
The script must:
1. Load `archive/iter_224/results/glider_00_lut08_sub03.json` to get the rule (LUT) and reference glider.
2. Simulate the glider forward in vacuum on a 32^3 grid for 40 steps, saving each grid state.
3. Test the following candidate CPT-like states derived from the step 40 state:
   - Candidate A: Pure spatial parity P (negating coordinates l, r, c on the torus, keeping channel indices the same).
   - Candidate B: Pure channel negation T (mapping each channel ch to T_ch[ch], keeping coordinates the same).
   - Candidate C: Combined spatial parity and channel negation PT (negate coordinates and channels).
   - Candidate D: CPT (which reverses the coordinates AND channels, and evolves under the inverse LUT).
4. For each candidate:
   - Run the state forward for 40 steps on the torus (for A, B, C under the forward rule; for D under the inverse rule, i.e., stream reverse followed by collide with the inverse LUT).
   - Apply the corresponding inverse transformation to the step 40 state.
   - Check if it matches the initial step 0 grid perfectly (all bits match).
5. If none of these match, sweep other O_h coordinate transformations + channel permutations + time reversals to find if any combination acts as a physical antiparticle propagating with velocity -v under the forward rule.
6. Print out the detailed comparison and match results.
Run this script and output the results.