1. Create a python script 'src/run_warm_start_evolution_v2.py' to run a warm-start evolutionary search for a sub-light speed (v<c) glider.
2. In this script:
   - Load the 179 champion rule 'archive/iter_179/results/champion_rule.json' and extract its generator pairs.
   - Initialize a population of 100 C2-symmetric rules, where 10 are the exact champion rule and 90 are mutated versions of it.
   - Implement C2-preserving mutations on the generator pairs list: adding, removing, or modifying pairs, and rebuilding via '_try_build_c2_rule' from 'src/evolution.py'.
   - The fitness evaluation of a rule should:
     a. Run 500-step simulation of the L-tromino seed.
     b. If at any step, the bit count is > 6 or < 2, or the final bit count at step 500 is not exactly equal to the initial bit count (3), return 0.0 (strict mass conservation).
     c. If the average velocity (displacement/steps) is >= 0.9c (or 0.9 cells/step), return 0.0 (sub-light velocity gating).
     d. Otherwise, return the score from DisplacementConsistencyFitness with num_windows=5.
3. Run the script for 30 generations. Ensure it is robust, has no pandas dependency, and writes outputs (champion_v2_rule.json, evolution_summary_v2.csv) to 'archive/iter_220/results/'.
4. Check if a high-fitness rule is found and report its details (fitness, average velocity, bit conservation, stability).
5. If a true v<c glider is found, render a GIF showing its motion and save it to 'archive/iter_220/results/champion_v2_glider.gif'.