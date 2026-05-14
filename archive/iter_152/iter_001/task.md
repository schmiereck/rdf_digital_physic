Run the second generation of the evolutionary algorithm using the validated composite fitness metric.

**Inputs:**
- The results from `archive/iter_151/results/rules_and_fitness.csv` serve as the starting population (Gen-1).

**Process:**
1.  Load the 100 rules and their fitness scores from the Gen-1 CSV file.
2.  Select the top 10% of rules from Gen-1 as the elite parent pool.
3.  Generate a new population of 100 rules (Gen-2) through crossover and mutation of the selected elites.
4.  Evaluate the fitness of each of the 100 new rules in Gen-2 using the exact same simulation parameters (150x150 soup, 25% density, 1600 steps) and the composite fitness function (`total_displacement / (1 + std_dev)`) as defined and used in iter_151.
5.  Save the new population (Gen-2) and their fitness scores to `archive/iter_152/results/gen_2_rules_and_fitness.csv`.
6.  Calculate and save summary statistics (mean, median, max fitness) for the Gen-2 population into the final YAML report.

**Command:**
This process should be orchestrated by the main evolutionary script. A command might look like this (adapt as necessary based on the existing `src/evolve.py` script):
`python src/evolve.py --generation 2 --input_population archive/iter_151/results/rules_and_fitness.csv --output_dir archive/iter_152/results/ --elite_fraction 0.1`

**Executor YAML block:**
At the end of your execution, provide the results in the standard YAML format, including `status`, `metrics` (mean_fitness, median_fitness, max_fitness for Gen-2), and a brief `experimenter_view`.
```yaml
status: ok
artifacts:
  - "archive/iter_152/results/gen_2_rules_and_fitness.csv"
metrics:
  mean_fitness: ...
  median_fitness: ...
  max_fitness: ...
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: ""
```