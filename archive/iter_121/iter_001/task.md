
Create a new script, `src/run_ash_evolution_gen1.py`, to generate and evaluate an initial population of rules using the ash-based fitness metric.

**1. Rule Generation:**
- Implement a function to generate a population of 100 random, C2-symmetric, reversible, non-conserving rules.
- Use the method from iter_095: each rule is defined by `k` (randomly chosen between 2 and 4) kernel pairs `(A, B)`. This creates a mix of sparse rules.
- Save the generated population to `archive/iter_121/population/`.

**2. Fitness Evaluation:**
- For each of the 100 generated rules, calculate its fitness using the ash-based environment.
- **Procedure per rule:**
    a. Load the canonical ash pattern from `src/ash_pattern.json`. This file contains the initial set of live cells.
    b. Simulate the rule on a 150x150 grid for 200 steps.
    c. Calculate the fitness using the metric validated in iter_120: `fitness = displacement / (1 + abs(final_bits - initial_bits) + abs(final_objects - initial_objects))`.
        - `initial_bits` and `initial_objects` are 325 and 72, respectively.
        - `displacement` is the net movement of the center of mass of all live cells.
        - `final_bits` and `final_objects` are the counts after 200 steps.
- Save all fitness scores and component metrics (final_bits, final_objects, displacement) to `archive/iter_121/results/fitness_scores.csv`.

**3. Report Summary:**
- After evaluating the entire population, create `archive/iter_121/result.yaml` with the following keys:
    - `population_size`: 100.
    - `inert_baseline_fitness`: The value from iter_120 (0.052432).
    - `rules_beating_baseline`: The count of rules with a fitness score > 0.052432.
    - `top_fitness_score`: The highest fitness score found in the population.
    - `top_rule_id`: The filename of the rule that achieved the top score.
    - `top_rule_displacement`: The displacement value for the top-scoring rule.
    - `top_rule_final_bits`: The final bit count for the top-scoring rule.
    - `top_rule_final_objects`: The final object count for the top-scoring rule.
