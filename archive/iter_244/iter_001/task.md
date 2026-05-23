Read `src/pre_registration.md`. Run `src/glider_annihilation_analysis.py` to see if it successfully finds a clean annihilation of the LUT-08 sub-light glider and its antiparticle under the forward rule on the 32^3 grid. If there are any bugs, fix them. 
Then, write and execute a Python script `src/fcc_antiparticle_annihilation.py` that strictly implements the pre-registered protocol:
1. Construct the CPT-conjugate (antiparticle) of the LUT-08 glider.
2. Simulate the antiparticle in vacuum for 100 steps on a 64^3 FCC grid to confirm stability, constant velocity, and bit conservation.
3. Compute and track the chirality and sub-lattice parities of the antiparticle to verify CPT symmetry. Show that its chirality sequence is the negated and time-reversed sequence of the original glider.
4. Set up a head-on collision between the LUT-08 glider and its antiparticle (using the optimal phase alignment and spatial offset discovered from `src/glider_annihilation_analysis.py` but adjusted for a 64^3 grid), simulating for 100 steps.
5. Analyze the asymptotic state (t = 80 to 100) to verify that all 8 bits are in independent, non-interacting single-bit channels propagating at v=1c, and that zero stationary or bound-state remnants remain (i.e. zero bound states of size >= 2 bits).
6. Save all results to `archive/iter_244/results/` (create JSON and markdown report).
Output all findings and logs.