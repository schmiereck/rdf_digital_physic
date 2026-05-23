You must write and execute the code directly using your own built-in file writing and command execution tools. DO NOT spawn any sub-agents (do not call run_agent or poll_agent) as the Claude API is currently hitting session limits.

Your task is to write a Python script `src/glider_annihilation_analysis.py` that implements the following self-contained protocol:

1. Load the LUT-08 glider rule from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Compute the velocity of the original glider pA in vacuum over 80 steps to establish its velocity vector v_A.
3. Use the 48 O_h symmetry transformations (imported or computed) to identify all stable antiparticle candidates pB that propagate with velocity -v_A.
4. Sweep over:
   - These stable antiparticle candidates pB.
   - Relative phase in {0, 1} (where phase 1 is obtained by simulating the original glider for 1 step).
   - Alignments: place the original glider at oa = (6, 16, 6) and the antiparticle at ob = (26 + dl, 16 + dr, 26 + dc) with dl, dr, dc swept in [-4, 4].
5. For each setup, simulate for 80 steps and check for "clean annihilation" at step 80:
   - Total bit count == 8.
   - Bounding box of size 10x10x10 centered at (16, 16, 16) is completely empty of any active bits.
   - All 8 bits are isolated (pairwise Manhattan distance on torus >= 6), proving they are independent, uncoupled 1-bit states.
6. If a clean annihilation is found, perform the CPT-symmetry reconstruction test:
   - Apply CPT to the state at step 80 (coordinates l,r,c become (-l)%L, (-r)%L, (-c)%L on torus L=32, channel remains unchanged).
   - Simulate for 80 steps forward under the forward rule.
   - Apply CPT again.
   - Verify that it perfectly matches the initial step 0 grid (to bit-level precision).
7. Write `archive/iter_243/results/annihilation_summary.json` and `archive/iter_243/results/CPT_annihilation_report.md`.

Execute the script with `python src/glider_annihilation_analysis.py` and print the output. Ensure everything is done using your own internal tools.