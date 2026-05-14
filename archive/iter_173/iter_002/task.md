Validate the new `StableVelocityFitness` metric against the pathological champion rules from `iter_170` and `iter_171`.

**Procedure:**

1.  Identify the champion rule file from `iter_170` (the "annihilator") and `iter_171` (the "puffer"). These should be available in their respective `archive/iter_NNN/results/` directories.
2.  Use the `src/evaluate.py` script with the `--fitness-metric StableVelocityFitness` option to calculate the fitness for both of these rules.
3.  The evaluation for each rule should use the standard 3-bit asymmetric 'L-tromino' seed.
4.  **Success Criterion:** Both rules must achieve a fitness score below 0.1.
5.  Create a CSV file at `archive/iter_173/results/validation_scores.csv` with the following columns: `rule_source`, `fitness_score`, `mean_velocity`, `std_dev_velocity`, `initial_bits`, `final_bits`. Populate it with the results for the two pathological rules.