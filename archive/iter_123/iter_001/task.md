This task continues the successful ash-based evolutionary search by breeding and evaluating Generation 3.

**1. Identify Gen-2 Elites:**
- Load the fitness data from `archive/iter_122/results/fitness_scores.csv`.
- The elites are the 12 rules that beat the Gen-1 top score. Their `rule_id`s are listed in the `is_elite` column.
- Load these 12 elite rules from `archive/iter_121/population/`. (Note: The Gen-2 population was bred from Gen-1 rules, so the files are in the iter_121 archive).

**2. Breed Gen-3 Population:**
- Create a new population of 100 rules for Gen-3.
- **Elitism:** Carry over the top 2 rules from Gen-2 (rule_010 and rule_055 from iter_121) directly.
- **Breeding:** Generate the remaining 98 rules using the same crossover and mutation strategy from iter_122:
    a. Randomly select two distinct parents from the 12 elites.
    b. Create a child's rule by taking half of the generator pairs from each parent.
    c. Apply a 10% mutation probability (add/delete a random generator pair, or flip a bit in a generator's state).
- Save the 100 new Gen-3 rules to `archive/iter_123/population/`.

**3. Evaluate Gen-3 Population:**
- For each of the 100 new rules, calculate its fitness using the canonical ash environment (`src/ash_pattern.json`) and the established fitness metric: `displacement / (1 + abs(final_bits - 325) + abs(final_objects - 72))`.
- The simulation for each rule should run for 200 steps.
- Save the full results (rule_id, fitness, displacement, final_bits, final_objects) to `archive/iter_123/results/fitness_scores.csv`.

**4. Report Summary:**
- After evaluation, create the final `result.yaml` in `archive/iter_123/`.
- The YAML must contain these keys:
    - `gen2_mean_fitness`: The mean fitness of Gen-2 (use the value 0.04440407 from iter_122).
    - `gen3_mean_fitness`: The calculated mean fitness of the new Gen-3 population.
    - `fitness_improvement_pct`: The percentage change from Gen-2 mean to Gen-3 mean.
    - `gen3_top_fitness`: The highest fitness score achieved in Gen-3.
    - `gen3_rules_beating_gen2_top`: The number of rules in Gen-3 with a fitness score greater than Gen-2's top score (0.23962495).

The final executor output should be the standard YAML block with `status`, `metrics`, etc. The `metrics` dictionary in the executor output should contain the keys listed in step 4.