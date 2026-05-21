Create the python script `src/analyze_d4_collision_18.py` that analyzes the physical properties and transitions of the 18-channel D4 LGCA LUT.

The script should:
1. Import `numpy as np`, `json`, `os`, and functions from `src.engine_d4_spacetime_18` (`generate_symmetric_lut`, `compute_momentum`, `PROJECTED_VECTORS`, `NUM_STATES`).
2. Generate the symmetric LUT with seed 42.
3. Calculate:
   - Total number of states with non-identity transitions (scattering states) and percentage.
   - Break down by Hamming weight (from 0 to 18): number of states, number of scattering states, and scattering percentage.
4. Focus on 2-bit states (Hamming weight 2) and analyze head-on collisions (where total momentum is (0,0,0)):
   - How many head-on 2-bit states exist?
   - What are their inputs (e.g., temporal-temporal, spatial-spatial)?
   - What are their outputs under the collision?
   - Catalog how many light-to-light, light-to-matter (temporal-temporal to spatial-spatial), matter-to-light (spatial-spatial to temporal-temporal), and matter-to-matter transitions occur.
5. Save the detailed results to `archive/iter_228/results/collision_analysis.json`.
6. Print out a beautiful Markdown table of the results and transition statistics.

Write the code, execute it, and print the results. Success criterion: stdout contains head-on transition statistics.