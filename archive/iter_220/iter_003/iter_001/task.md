
Create and run a Python script `src/probe_evolution.py` to conduct a 5-generation evolutionary search probe.

**Script Requirements (`src/probe_evolution.py`):**

1.  **Import necessary modules:** `evoflux.evoflux`, `evoflux.fitness`, `evoflux.rules`, `evoflux.seeds`, `numpy`, `pandas`, `json`, `os`.
2.  **Configuration:**
    *   Population size: 100
    *   Grid size: 128x128
    *   Simulation steps (horizon): 500
    *   Generations: 5
    *   Symmetry: C2
    *   Seed: 3-bit L-tromino (`seeds.ltromino_3bit()`)
    *   Fitness function: `DisplacementConsistencyFitness`
    *   Output directory: `archive/iter_220/results/`
3.  **Logic:**
    *   Create the output directory if it doesn't exist.
    *   Initialize an `EvolutionaryOptimizer` with the specified configuration.
    *   Create a random initial population of C2-symmetric rules.
    *   Run the evolution for 5 generations.
    *   Keep track of fitness statistics (mean, max, min, std) for each generation.
4.  **Outputs:**
    *   Save the best rule found (the "champion") to `archive/iter_220/results/champion_rule.json`.
    *   Save the per-generation fitness statistics to `archive/iter_220/results/fitness_log.csv`. The CSV should have columns: `generation`, `mean_fitness`, `max_fitness`, `min_fitness`, `std_fitness`.
5.  **Reporting:**
    *   After the run, print the fitness log to stdout.
    *   Calculate if the primary success criterion was met: `mean_fitness_gen5 >= 2 * mean_fitness_gen1`.
    *   Print a clear statement indicating whether the criterion was met.

**Execution:**

1.  Run the script: `python src/probe_evolution.py`
2.  After the script finishes, create the final YAML block summarizing the outcome.

**Final YAML block for the executor:**
```yaml
status: ok
artifacts:
  - archive/iter_220/results/champion_rule.json
  - archive/iter_220/results/fitness_log.csv
metrics:
  generations_run: 5
  initial_mean_fitness: <mean_fitness_of_gen_1>
  final_mean_fitness: <mean_fitness_of_gen_5>
  fitness_improvement_factor: <final_mean_fitness / initial_mean_fitness>
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "Probe experiment to validate DisplacementConsistencyFitness landscape."
```
