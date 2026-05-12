
Create a new script `src/run_evolution_parity_gen3.py`. This script will breed and evaluate the third generation of parity-conserving rules.

**1. Identify Parent Rules:**
- The script must read the `results.csv` file from the previous generation, located at `archive/iter_139/results/results.csv`.
- Identify the 5 "elite" parent rules. These are the rules from Gen-2 that had a fitness score greater than the Gen-1 top score of 0.36059.

**2. Implement Breeding Process:**
- Create a new population of 100 "child" rules in `archive/iter_140/population/`.
- The breeding pool will consist of 20 copies of each of the 5 elite parent rules (total of 100 rules in the pool).
- For each of the 100 children to be generated:
    a. Select two parent rules at random from the breeding pool.
    b. Load their kernel pairs from the corresponding files in `archive/iter_139/population/`.
    c. Create a child rule by performing a one-point crossover on the parents' lists of 8 kernel pairs. The child will inherit some pairs from parent A and the rest from parent B.
    d. Apply a 10% mutation chance. If mutation occurs, replace one of the child's 8 kernel pairs with a new, randomly generated, valid, parity-conserving kernel pair.
    e. Save the resulting child rule as a new JSON file in `archive/iter_140/population/`.

**3. Evaluate the New Population:**
- Evaluate each of the 100 new rules using the established local fitness environment.
- This requires loading `src/ash_pattern.json` and `src/local_target_objects.json`.
- The fitness function is the "late displacement" (COM shift between steps 100 and 200) penalized by the quadratic bit ratio (`1 + (bit_ratio - 1)**2`).
- The simulation for each rule must run for 200 steps.

**4. Report Metrics:**
- After evaluating all 100 rules, create a summary CSV file at `archive/iter_140/results/results.csv` with columns: `rule_id, fitness, bit_ratio, displacement_100_200`.
- Create a final summary YAML file for the orchestrator at `archive/iter_140/results/summary.yaml` with the following keys:
    - `gen2_top_fitness`: 0.73077873 (for baseline comparison)
    - `gen3_top_fitness`: The highest fitness score achieved by any rule in the Gen-3 population.
    - `gen3_mean_fitness`: The average fitness score across all 100 rules in Gen-3.
    - `rules_beating_gen2_top`: The number of Gen-3 rules with a fitness score greater than `gen2_top_fitness`.
    - `viable_rules`: Count of rules with fitness > 0.01 AND bit_ratio < 3.0.
    - `chaotic_rules`: Count of rules with bit_ratio >= 3.0.
    - `dead_rules`: Count of rules with fitness <= 0.01.

The final YAML block for the orchestrator should be based on the contents of this `summary.yaml` file.
