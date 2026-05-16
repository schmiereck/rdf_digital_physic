**Goal:** Test Strategy B: Evolve a conservation-first population towards motion.

**Tasks:**
1.  **Pre-screen Population:**
    - Create a new script `src/run_iter_192_prescreen.py`.
    - This script must generate and test **10,000** new, random C2-symmetric rules.
    - For each rule, it must run a 200-step simulation using the standard two-glider collision initial state.
    - It must check for perfect bit conservation (`final_bits == initial_bits`).
    - All rules that pass this check must be saved into a new population file: `archive/iter_192/iter_002/results/conserving_population.json`.
    - The script must log how many rules were tested and how many were found to be conserving.
2.  **Run Evolution on Screened Population:**
    - Create a new evolution script `src/run_iter_192_screened_evolution.py`.
    - This script must load the `conserving_population.json` generated in the previous step.
    - It must use the **`StagedCollisionFitness`** function (from `iter_190`), which requires perfect bit conservation and rewards approach and recession.
    - It will run a standard evolutionary search for 10 generations on this pre-screened population.
3.  **Success Criterion:** The experiment is successful if the evolutionary process finds a champion rule with a `fitness > 0`. This would indicate the existence of a rule that is both perfectly bit-conserving and exhibits, at minimum, the "approach" dynamic. Record the number of conserving rules found and the best fitness achieved during evolution.