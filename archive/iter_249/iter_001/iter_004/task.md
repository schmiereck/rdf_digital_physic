Write a Python script that:
1. Loads LUT-08 and O_h permutations, action, stabilizers, and orbits.
2. Identifies the weight-2 orbits.
3. For each of the weight-2 orbits:
   - Finds its size, a representative pair of channels (ch_i, ch_j), and the dot product of their FCC vectors.
   - Finds all other states in the SAME orbit that have the exact same stabilizer as the representative.
   - For each same-stabilizer state, shows its channel indices and its relationship to the representative (whether it keeps the same cycles or swaps them).
   - Shows the output state of the representative under LUT-08 (which is additive).
4. Writes the detailed text report of this analysis to 'src/weight2_orbit_analysis.txt'.
Run the script to generate this file.