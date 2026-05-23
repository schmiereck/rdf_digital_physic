Write a python script `src/find_annihilation.py` that:
1. Loads the LUT-08 glider rule from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Computes the 48 O_h transforms of the LUT-08 glider to identify those that propagate with the opposite velocity -v.
3. Performs a systematic search/sweep over:
   - Stable antiparticle candidates (those with velocity -v).
   - Relative phase delta_phi in {0, 1}.
   - Alignments (offsets dl, dr, dc in [-4, 4]).
4. For each setup, initializes a grid of size L=32 with the original glider at (6, 16, 6) and the antiparticle candidate at (26 + dl, 16 + dr, 26 + dc).
5. Simulates 80 steps.
6. Analyzes the state at step 80 to see if it meets the quantitative "clean annihilation" criteria:
   - Total bits == 8.
   - Bounding box of size 10x10x10 centered at (16, 16, 16) contains exactly 0 bits.
   - All 8 bits are isolated (pairwise Manhattan distance on torus >= 6, so they are independent, uncoupled 1-bit states).
7. If a clean annihilation is found, perform the CPT-symmetry reconstruction test:
   - Apply CPT to the state at step 80.
   - Simulate 80 steps forward.
   - Apply CPT again.
   - Check if the initial grid at step 0 is perfectly reconstructed (bit-level match).
8. Print out the best parameters and verification results.
Run this script and output the results.