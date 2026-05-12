
Create a new script, `src/evolve_reboot_gen3.py`, to breed and evaluate a third generation of rules.

**1. Load Gen-2 Elites:**
- Load the fitness scores for the Gen-2 population from `archive/iter_130/results/reboot_gen2_scores.csv`.
- Identify the top 5 elite rules from Gen-2 based on their fitness scores.

**2. Breed Gen-3 Population:**
- Create a new population of 100 Gen-3 rules.
- For each new rule, select two parents at random from the pool of 5 elites.
- Create the child rule using crossover: take 4 random kernel pairs from the first parent and 4 from the second parent.
- Apply a 10% mutation rate: for 10 of the 100 new rules, replace one of its 8 kernel pairs with a completely new, valid, random C2-symmetric pair.
- Save the new population to `archive/iter_131/population/`.

**3. Evaluate Gen-3 Population:**
- For each of the 100 new rules, evaluate its fitness using the established "late-displacement" metric on the canonical `src/ash_pattern.json`.
  - Simulate for 200 steps.
  - Calculate displacement of the center of mass between step 100 and step 200.
  - Final fitness is `displacement / (1 + final_bit_count / initial_bit_count)`.
  - Assign a fitness of 0 to any rule that is chaotic (final bit count > 1000) or dead (final bit count < 20).
- Save the results to `archive/iter_131/results/reboot_gen3_scores.csv` with columns `rule_id,fitness,final_bits,final_objects,displacement_100_200`.

**4. Report Summary:**
- Create `archive/iter_131/result.yaml` with the following key metrics:
  - `gen2_top_fitness`: The top score from iter_130 (for comparison).
  - `gen3_top_fitness`: The top score from this new generation.
  - `fitness_improvement_pct`: The percentage improvement of Gen-3 top over Gen-2 top.
  - `rules_beating_gen2_top`: The number of Gen-3 rules that surpassed the Gen-2 champion.
  - `viable_rules`: The count of non-chaotic, non-dead rules in Gen-3.
  - `chaotic_rules`: The count of chaotic rules in Gen-3.
  - `gen3_mean_fitness`: The mean fitness of the viable rules in Gen-3.
