
Create a script `src/run_density_scan.py` to investigate the impact of rule density on the emergence of sustained motion.

**1. General Setup:**
- The script will evaluate rules using the "late-displacement" fitness metric on the canonical `ash_pattern.json`.
- Fitness is calculated based on displacement between steps 100 and 200.
- A rule is considered "viable" if its fitness is > 0 AND its final bit count at step 200 is less than a chaos threshold of 1000 bits.

**2. Rule Generation:**
- Implement a function `generate_c2_rule(n_pairs, seed)` that creates a random, C2-symmetric, reversible rule with exactly `n_pairs` kernel pairs.

**3. Density Scan Logic:**
- The script will test three density levels:
  - Low Density: `n_pairs = 4` (16 non-identity mappings)
  - Medium Density: `n_pairs = 8` (32 non-identity mappings)
  - High Density: `n_pairs = 16` (64 non-identity mappings)
- For each density level:
  a. Generate a population of 100 rules using a consistent but unique seed range for that density.
  b. Evaluate each of the 100 rules using the late-displacement fitness metric.
  c. Record the number of viable rules, the top fitness score, and the average fitness for the population.

**4. Reporting:**
- The script must create a final `archive/iter_129/result.yaml` file that summarizes the findings across all three density levels. The YAML should contain the following structure:

```yaml
low_density:
  viable_rules: <count>
  top_fitness: <float>
  mean_fitness: <float>
  chaotic_rules: <count>
  static_rules: <count>
medium_density:
  viable_rules: <count>
  top_fitness: <float>
  mean_fitness: <float>
  chaotic_rules: <count>
  static_rules: <count>
high_density:
  viable_rules: <count>
  top_fitness: <float>
  mean_fitness: <float>
  chaotic_rules: <count>
  static_rules: <count>
```

- Also, save the detailed fitness scores for each population to separate CSV files: `archive/iter_129/results/low_density_scores.csv`, `medium_density_scores.csv`, and `high_density_scores.csv`.
