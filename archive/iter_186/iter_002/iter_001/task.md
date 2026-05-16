Create a Python script `src/evolve_elastic.py` to conduct an evolutionary search for a rule that produces elastic collisions.

**Requirements:**

1.  **Fitness Function:** Use the `CollisionFitness` function from `src/fitness_functions.py`.
2.  **Population:** Start with a fresh, random population of 100 C2-symmetric rules.
3.  **Generations:** Run the evolution for 10 generations.
4.  **Selection:** In each generation, select the top 10% of rules as the elite for the next generation.
5.  **Breeding:** Breed the next generation through crossover and mutation of the elite rules.
6.  **Logging:** Log the maximum and average fitness for each generation to `archive/iter_186/results/fitness_log.csv`.
7.  **Champion Rule:** If a rule with fitness 1.0 is found, stop the search and save its truth table to `archive/iter_186/results/champion_rule.json`. If no rule reaches 1.0, save the best rule found.
8.  **Execution:** The script should be runnable from the command line and perform the full evolutionary search.

After creating the script, execute it.

Report the final champion rule's ID and its fitness score in the final result.

The final YAML block should look like this:
```yaml
status: ok
artifacts:
  - "archive/iter_186/results/champion_rule.json"
  - "archive/iter_186/results/fitness_log.csv"
metrics:
  champion_fitness: <fitness_of_best_rule>
  champion_id: "<id_of_best_rule>"
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "..."
```