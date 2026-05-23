Create and execute a Python script `src/fcc_antiparticle_annihilation.py` that implements the following steps to thoroughly investigate CPT symmetry, vacuum stability, and mutual annihilation under the LUT-08 CA rule on the 3D FCC grid:

1. Load the rule (LUT) and reference glider from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Define the discrete Parity P operator (negating coordinates l, r, c on the torus L=64) and Time-Reversal T operator (negating the velocity channels, mapping ch -> T_ch[ch] where T_ch = [1, 0, 3, 2, 5, 4, 9, 10, 11, 6, 7, 8]).
3. Construct the CPT-conjugate state of the glider: apply coordinate negation (P) and channel negation (T) to the glider at step 0.
4. Verify the vacuum propagation of this CPT-conjugate state:
   - First, simulate it forward under the FORWARD rule (forward stream + forward collide with LUT) for 100 steps. Measure its stability, bit count, and velocity. Does it disintegrate?
   - Second, simulate it forward under the INVERSE rule (reverse stream + collide with inverse LUT) for 100 steps. Measure its stability, bit count, and velocity. Does it propagate stably with velocity -v?
5. Verify CPT symmetry mathematically: show that the CPT-conjugate state under the inverse rule perfectly mirrors the original glider's vacuum propagation under the forward rule, and compare their chirality sequences and sub-lattice parities over 100 steps. Confirm if the chirality sequence of the antiparticle under the inverse rule is the negated and time-reversed sequence of the original glider.
6. Investigate head-on collisions and mutual annihilation:
   - Conduct a systematic sweep over relative phase alignments (delta_phi in {0, 1}) and impact offsets (dl, dr, dc in [-4, 4]) on a 64^3 grid.
   - For each setup, place the original glider at (16, 32, 16) and the CPT-conjugate at (48+dl, 32+dr, 16+dc), and simulate for 100 steps under the FORWARD rule.
   - Analyze the final state at t = 100 to check for "clean annihilation" (i.e. zero bound states of size >= 2 bits in the collision region, exactly 8 bits total, all propagating as independent 1-bit states at the speed of light v=1c).
   - If a clean annihilation is found, report it. If not, document this honest null result and explain the physical mechanism behind the lack of clean annihilation under the forward rule (i.e., due to the asymmetry of the forward rule and the instability of the antiparticle under it).
7. Save all results to `archive/iter_244/results/annihilation_summary.json` and write a detailed markdown report to `archive/iter_244/results/CPT_annihilation_report.md`.
Output all findings and stdout.