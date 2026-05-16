**Goal:** Test Strategy A: Evolve a motion-first population towards bit conservation using a soft penalty.

**Tasks:**
1.  **Implement New Fitness Function:** In `src/fitness.py`, create a new class `LeakyConservationCollisionFitness`.
    - It should calculate a `staged_score` using the logic from `StagedCollisionFitness` (rewarding approach and recession).
    - It must also calculate the bit difference: `bit_error = abs(final_bits - initial_bits)`.
    - The final fitness score must be `staged_score / (1.0 + bit_error)`. This creates a soft penalty, allowing rules with good motion but imperfect conservation to still receive a non-zero score.
2.  **Create Evolution Script:** Create a new script `src/run_iter_192_leaky_evolution.py`.
    - The script must load the `warm_start_population.json` generated in `iter_191`, which contains mutants of the `g10_rule_001` glider rule.
    - It will run a standard evolutionary search for 10 generations using the new `LeakyConservationCollisionFitness` function.
    - Save the final population and champion rule to the results directory.
3.  **Success Criterion:** The experiment is successful if the evolutionary process finds a champion rule with a non-zero fitness score. The ideal outcome is a champion with a `staged_score > 0` and a `bit_error` lower than that of the original `g10_rule_001` parent. Record the champion's fitness, staged_score, and bit_error.