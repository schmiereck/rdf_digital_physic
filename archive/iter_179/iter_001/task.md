The previous attempt in iter_178.1 failed due to a code error. This is a direct retry of that task.

The goal is to determine if any rules from a prior, promising evolutionary run are actually stable gliders when assessed by the new, more robust `CheckpointFitness` metric.

**Instructions:**
1. Load the final population of rules saved from the evolutionary run in `iter_176` (located at `archive/iter_176/results/final_population.json`).
2. Implement and use the `CheckpointFitness` metric, as defined in `iter_177.3`. It should use the 'L-tromino' seed and enforce bit-count stability at steps 50, 100, 150, and 200.
3. Evaluate all rules in the loaded population using this metric.
4. Save the results (rule hash, fitness score) to a CSV file at `archive/iter_179/results/reevaluation_scores.csv`.
5. Identify the rule with the highest fitness score. If the top score is greater than 0.0, report it as a key metric. Otherwise, report the top score as 0.0.
