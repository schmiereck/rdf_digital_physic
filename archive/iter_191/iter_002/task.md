**Goal:** Evolve a rule with elastic collision dynamics, starting from a "warm-start" population of known glider-producing rules.

**Background:** Sub-task `191.1` created a population file `archive/iter_191/results/warm_start_population.json`. This population consists of 100 rules, all of which are slight mutations of the stable glider rule `g10_rule_001`. This task will now use this population to seed an evolutionary search.

**Tasks:**
1.  **Modify the evolutionary framework (`src/run_evolution.py`):**
    *   Add a new command-line argument `--initial_population_path` that allows loading a pre-existing population from a JSON file, bypassing the random population generation step.
    *   Ensure the `StagedCollisionFitness` function from `iter_190` is used as the fitness metric. This function rewards rules based on three stages:
        1.  **Approach:** Particles get closer (Score > 0).
        2.  **Recession:** Particles move apart after approaching (Score > 1).
        3.  **Elasticity:** Post-collision velocity vectors are preserved (Score > 2).
    *   Bit conservation must be strictly enforced for any non-zero score.

2.  **Execute the evolutionary search:**
    *   Run the modified script with the following configuration:
        *   `--initial_population_path`: `archive/iter_191/results/warm_start_population.json`
        *   `--generations`: 20
        *   `--population_size`: 100
        *   `--elite_size`: 10
    *   Log the fitness of the best rule from each generation.
    *   Save the final champion rule to `archive/iter_191/results/champion_rule.json`.

**Success Criterion:**
The evolutionary search completes, and the final champion rule achieves a fitness score greater than 0. A score of >= 2.0 would be a major success, indicating a potentially elastic collision. The absence of any progress (all fitness scores remaining 0.0) would also be a significant result.