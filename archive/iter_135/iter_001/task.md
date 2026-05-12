
Create a new script, `src/run_local_evolution.py`, to test if a localized fitness metric can evolve sustained motion for a specific pair of objects.

**1. Identify Target Objects and Load Predecessors:**
   - The script must load the object data from `archive/iter_133/results/remnant_objects.json`.
   - From this data, it must programmatically identify the two closest oscillators. These are the "target objects" for the fitness calculation. (Note: iter_134 identified these as objects with indices 2 and 3, which are a p4 4-cell and p3 6-cell oscillator).
   - Load the top 5 elite rules from the Gen-3 population, identified in `archive/iter_131/results/gen3_fitness_scores.csv`.

**2. Implement the Local Fitness Metric:**
   - Create a fitness function that takes a rule and the full 37-object remnant pattern as input.
   - This function will simulate the rule for 200 steps on a 200x200 grid with wrapping boundaries.
   - The fitness will be calculated based *only* on the cells belonging to the two target oscillators:
     - `com_100`: Center of mass of the target objects' cells at step 100.
     - `com_200`: Center of mass of the target objects' cells at step 200.
     - `displacement`: The Euclidean distance between `com_100` and `com_200`.
     - `bit_ratio`: The ratio of the target objects' final bit count (at step 200) to their initial bit count.
     - `fitness = displacement / (1 + abs(1 - bit_ratio))`
   - This metric rewards sustained motion of the target pair while penalizing growth or decay *of that pair*.

**3. Evolve and Evaluate New Generation (Gen-4):**
   - Breed a new population of 100 rules from the top 5 Gen-3 elites using the established crossover and 10% mutation methodology.
   - Evaluate each of the 100 new rules using the local fitness metric.
   - Save the full results to `archive/iter_135/results/gen4_local_fitness_scores.csv`.
   - Save the best performing rule to `archive/iter_135/population/best_local_rule.json`.

**4. Establish Baseline and Report:**
   - Calculate the local fitness score for the previous champion rule from the *global* evolution (`archive/iter_131/population/rule_011.json`). This serves as the baseline to beat.
   - Create the final `archive/iter_135/result.yaml` file with the following metrics:
     - `top_local_fitness_gen4`: The highest fitness score achieved by any rule in the new Gen-4 population.
     - `baseline_local_fitness_gen3_champ`: The local fitness score of the previous global champion (`rule_011`).
     - `rules_beating_baseline`: The number of rules in the Gen-4 population that scored higher than the baseline.
