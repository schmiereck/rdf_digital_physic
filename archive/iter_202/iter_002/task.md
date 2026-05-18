**Context:** The `CumulativeDisplacementFitness` function was developed and validated in `iter_202.1`. It has been shown to be robust against the phase-sampling exploit that invalidated the results of `iter_200`. We are now ready to restart the search for a genuine `v<c` glider.

**Goal:** Evolve a rule that produces a stable, bit-conserving, `v<c` (sub-light speed) glider using the new, robust fitness function.

**Task:**
1.  Configure and run an evolutionary search using the `src/main_v2.py` script.
2.  **Use the `CumulativeDisplacementFitness` function** validated in the previous step.
3.  Use the standard evolutionary parameters outlined in the project's `goal.md`:
    *   Seed Particle: 3-bit L-Tromino
    *   Grid Size: 128x128 Torus
    *   Population Size: 100 rules
    *   Elite Anteil: 10%
4.  Run the evolution for at least 15 generations to allow for a potential phase transition in fitness.
5.  Identify the champion rule (the rule with the highest fitness score) from the final generation.
6.  Save the champion rule to `archive/iter_202/results/champion_rule.json`.
7.  Write a summary of the evolutionary run, including the final fitness score of the champion and the number of generations run, to `archive/iter_202/results/evolution_summary.txt`.