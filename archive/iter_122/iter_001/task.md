Create a new script, `src/run_ash_evolution_gen2.py`, to breed and evaluate a second generation of "ash-animating" rules.

**1. Identify Gen-1 Elites:**
- Load the fitness results from `archive/iter_121/results/fitness_scores.csv`.
- Identify the 11 rules that beat the inert baseline fitness of 0.052432. These are the "elites".
- Also, calculate and store the mean fitness for the entire Gen-1 population.

**2. Breed Gen-2 Population:**
- Create a new population of 100 rules for "Gen-2".
- **Elitism:** Carry over the top 2 rules from the Gen-1 elites directly into the new population.
- **Breeding:** Generate the remaining 98 rules by:
  a. Randomly selecting two parent rules from the pool of 11 elites.
  b. Creating a child's kernel set by taking a random half of the non-identity kernel pairs from each parent (crossover). Ensure the child rule has 8 kernel pairs.
  c. Applying a mutation with a 10% probability. A mutation consists of replacing one kernel pair with a new, randomly generated valid C2-symmetric pair.
- Save the 100 new Gen-2 rules to `archive/iter_122/population/`.

**3. Evaluate Gen-2 Population:**
- For each of the 100 new Gen-2 rules, calculate its fitness using the established ash-based metric:
  a. Load the canonical ash pattern from `src/ash_pattern.json`.
  b. Simulate for 400 steps.
  c. Calculate `fitness = displacement / (1 + abs(final_bits - 325) + abs(final_objects - 72))`.
- Save the results for the new generation to `archive/iter_122/results/fitness_scores.csv`.

**4. Report & Compare:**
- After evaluating all 100 rules, calculate the mean fitness for the new Gen-2 population.
- Create `archive/iter_122/result.yaml` with the following keys:
  - `gen1_mean_fitness`: The mean fitness calculated in Step 1.
  - `gen2_mean_fitness`: The mean fitness for the new generation.
  - `fitness_improvement_pct`: The percentage change from Gen-1 to Gen-2.
  - `gen2_rules_beating_gen1_top`: The number of rules in Gen-2 with a fitness higher than the best rule from Gen-1 (0.09386).
  - `gen2_top_fitness`: The single highest fitness score in the Gen-2 population.