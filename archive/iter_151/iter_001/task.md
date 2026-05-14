## Goal

Re-evaluate the 100 random rules from `iter_150` with a new composite fitness metric to verify that it correctly penalizes inactive "settler" rules.

## New Fitness Metric

The new metric is `total_displacement / (1 + std_dev)`.

## Task

1.  Create a new Python script `src/re_evaluate_fitness.py`.
2.  The script must read the CSV file located at `archive/iter_150/results/fitness_scores.csv` using the `pandas` library.
3.  For each rule (row) in the CSV, calculate a `new_fitness` score using the formula `row['total_displacement'] / (1 + row['std_dev'])`.
4.  After calculating the new fitness for all rules, compute the following statistics for the `new_fitness` scores:
    *   Mean
    *   Maximum
    *   Median
    *   Standard Deviation
5.  Identify the rule (`rule_id`) that had the highest *original* fitness in the `iter_150` data. From the CSV, this is `rule_086` with a fitness of `0.98104101`. Report the `new_fitness` score for this specific rule.
6.  Create the output directory `archive/iter_151/results/`.
7.  Write a summary of the results to `archive/iter_151/results/re_evaluation.txt`. The summary should be human-readable and contain all the computed statistics.

## Final Output

Your final response MUST be a YAML block containing the following:
- `status`: `ok` if successful.
- `artifacts`: A list containing the path to the summary file, `archive/iter_151/results/re_evaluation.txt`.
- `metrics`: A dictionary with the new `mean_fitness`, `max_fitness`, and `median_fitness`. Also include `new_fitness_for_rule_086`.
- `experimenter_view`: A brief description of what you did and the results.
```