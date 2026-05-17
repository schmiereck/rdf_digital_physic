
## Task: Run Evolutionary Search for Massive Glider

The necessary components (`MassiveGliderFitness`, experiment config) are now in `src`. Your task is to run the evolutionary search defined in `src/experiments/exp_198_2_massive_glider.py`.

### 1. Create the evolution script `src/evolve.py`

Create a script that performs the following:
-   Imports necessary libraries (`deap`, `numpy`, `random`, etc.).
-   Loads the `EXPERIMENT_CONFIG` from `src/experiments/exp_198_2_massive_glider.py`.
-   Sets up the DEAP evolutionary algorithm (Toolbox, creators, etc.).
-   The rule representation should be a list of integers for the "survive" and "birth" conditions. The `B3/S23` space from the config implies the "birth" part is fixed at `B3`. The evolution should search for the "survive" `S` rules. The chromosome can be a list of 9 booleans (for S0-S8).
-   The fitness function is already defined in the config.
-   The script should run for the number of generations specified in the config.
-   It should save the champion rule, the hall of fame, and a log of the evolution statistics (e.g., min/max/avg fitness per generation) to the results directory.

### 2. Execute the script

Run the `evolve.py` script.

### 3. Save the results

Ensure all results are saved to `archive/iter_198.2/results/`. The key artifacts to save are:
-   `champion.txt`: The best rule string found (e.g., "B3/S1234").
-   `hall_of_fame.json`: A list of the top rules and their fitness scores.
-   `evolution_log.csv`: A CSV file with statistics for each generation.
-   A plot of the fitness over generations (`fitness_plot.png`).

### Final Output YAML

The final YAML from the executor should look like this upon successful completion:

```yaml
status: ok
artifacts:
  - "archive/iter_198.2/results/champion.txt"
  - "archive/iter_198.2/results/hall_of_fame.json"
  - "archive/iter_198.2/results/evolution_log.csv"
  - "archive/iter_198.2/results/fitness_plot.png"
metrics:
  champion_fitness: <fitness_score_of_champion>
  num_generations: 10
log_excerpt: |
  Gen 0: Max fitness = 0.0012, Avg fitness = 0.0001
  ...
  Gen 9: Max fitness = 0.056, Avg fitness = 0.034
  Champion rule B3/S... found with fitness 0.056
experimenter_view: |
  The evolutionary search completed successfully over 10 generations. The fitness showed a clear upward trend, indicating that the search was effectively exploring the rule space. The champion rule has been saved for validation.
notes: "Evolution run complete. Next step is validation of the champion rule."
```
Make sure the output path for artifacts is `archive/iter_198.2/results/` as the current parent context is `198.2`.