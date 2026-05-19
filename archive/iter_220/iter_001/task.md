**Goal:** Discover a rule supporting a stable, bit-conserving `v<c` (sub-light speed) glider through evolutionary search.

**Context:** The platform is now stable and the `DisplacementConsistencyFitness` function has been validated as exploit-resistant (iter_220). The previous blocker (a supposed dependency error) has been cleared. This is the first attempt at a full evolutionary search with these validated components.

**Task for the Planner:**
1.  **Setup and Run Evolution:**
    *   Configure and launch a multi-generational evolutionary search using the standard framework (`src/evolution.py` or a dedicated script if needed).
    *   **Fitness Function:** You MUST use `DisplacementConsistencyFitness`.
    *   **Seed Particle:** Use the standard 3-bit L-Tromino.
    *   **Population Size:** 100 rules.
    *   **Generations:** Run for at least 10 generations, and continue up to 20 if fitness is still improving.

2.  **Identify Champion:**
    *   Throughout the run, track the best rule found in any generation.
    *   The final "champion" is the single rule with the highest fitness score achieved during the entire search.

3.  **Produce Outputs:**
    *   Save the final champion rule's definition to `archive/iter_220/results/champion_rule.json`.
    *   Save a summary of the evolutionary process (e.g., best/mean fitness per generation) to `archive/iter_220/results/evolution_summary.csv`.
    *   Provide a brief analysis of the run: Did fitness plateau? Was there a clear phase transition?
