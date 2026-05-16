Run an evolutionary search using the new `RecessionBiasedFitness` function.

**Configuration:**
-   **Script:** Use the main evolutionary script `src/run_evolution.py`.
-   **Population:** Use the "warm-start" population from `archive/iter_191/results/warm_start_population.json`. This is the same population used successfully in `iter_192.1`.
-   **Fitness Function:** Specify `RecessionBiasedFitness` as the fitness class.
-   **Evolution Parameters:**
    -   Generations: 10
    -   Population Size: 100
    -   Elite Fraction: 0.1
    -   Mutation Rate: 0.05
-   **Seed:** Use the standard two-glider collision seed (`src/seeds/collision_6bit.json`).

**Goal:**
The primary goal is to find a champion rule with a fitness score significantly greater than the fusion baseline (which would be around `1.0 / (1 + bit_error)`). A high fitness score would indicate that the rule produces both approach and recession.

**Outputs:**
-   Log the fitness statistics for each generation.
-   Save the final population to `archive/iter_193/iter_002/results/final_population.json`.
-   Save the champion rule to `archive/iter_193/iter_002/results/champion_rule.json`.
-   Record the champion's fitness, staged score, and bit error in the final metrics.