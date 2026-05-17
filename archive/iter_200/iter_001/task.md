Your goal is to discover a stable, `v<c` (sub-light speed) glider in the 2D hexagonal lattice. You must use the new, exploit-resistant `SparseGliderFitness` function located in `src/fitness_v2.py`.

**Methodology: Evolutionary Search**
1.  **Setup:** Create a new experiment script, `src/run_v_less_than_c_search.py`.
2.  **Configuration:** Use the established standard configuration for 2D hex evolution:
    *   **Seed Particle:** 3-bit L-Tromino.
    *   **Grid:** 128x128 torus.
    *   **Population:** 100 C2-symmetric rules.
    *   **Elitism:** 10%.
    *   **Fitness Function:** `SparseGliderFitness`.
3.  **Execution:** Run the evolutionary search for at least 10 generations. Log the fitness of the best rule from each generation.
4.  **Analysis:** Identify the single best rule (the 'champion') from the entire run.
5.  **Output:**
    *   Save the champion rule to `archive/iter_200/results/champion_v_lt_c_rule.json`.
    *   Generate an animation of the champion rule acting on the L-tromino seed for 500 steps and save it to `archive/iter_200/results/champion_v_lt_c_glider.gif`.
    *   Write a summary of the evolutionary run (top fitness per generation) to `archive/iter_200/results/evolution_summary.csv`.

Your primary objective is to find a rule that results in a non-zero, stable fitness score, indicating successful `v<c` motion.