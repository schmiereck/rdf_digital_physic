## Goal

Your goal is to discover a stable, `v<c` (sub-light speed) glider in a 2D hexagonal lattice by running an evolutionary search. You will use the `SparseGliderFitness` function.

### Methodology

1.  **Create a new experiment script:** `src/run_v_less_than_c_search.py`. This script will orchestrate the entire experiment.
2.  **Implement the Evolutionary Search:**
    *   The script should set up and run an evolutionary algorithm.
    *   **Configuration:**
        *   **Seed Particle:** 3-bit L-Tromino.
        *   **Grid:** 128x128 torus (hexagonal).
        *   **Population:** 100 C2-symmetric rules.
        *   **Elitism:** 10% (top 10 rules carry over to the next generation).
        *   **Fitness Function:** Import and use `SparseGliderFitness` from `src/fitness_v2.py`.
    *   **Execution:** Run the evolution for **15 generations**. In each generation:
        *   Evaluate the fitness of every rule in the population.
        *   Log the fitness of the best rule in that generation.
        *   Create the next generation by applying mutation to the top 10 elite rules.
3.  **Analyze and Save Champion Rule:**
    *   After the evolutionary run is complete, identify the single best rule (the 'champion') from all generations.
    *   Save this champion rule to `archive/iter_200.1/results/champion_v_lt_c_rule.json`.
4.  **Generate Outputs:**
    *   **Animation:** Generate an animation of the champion rule acting on the L-tromino seed for 500 steps. Save it as `archive/iter_200.1/results/champion_v_lt_c_glider.gif`.
    *   **Summary:** Write a summary of the evolutionary run (generation number and best fitness for that generation) to `archive/iter_200.1/results/evolution_summary.csv`. The CSV should have headers: `generation,best_fitness`.
5.  **Execution:**
    *   Run the script using `python src/run_v_less_than_c_search.py`.
    *   The primary metric to report should be the `champion_fitness`.

### Final YAML Output

Please conclude your work by providing the following YAML block in your response.

```yaml
status: ok
artifacts:
  - "archive/iter_200.1/results/champion_v_lt_c_rule.json"
  - "archive/iter_200.1/results/champion_v_lt_c_glider.gif"
  - "archive/iter_200.1/results/evolution_summary.csv"
metrics:
  champion_fitness: <fitness_of_the_best_rule>
  generations_run: 15
log_excerpt: |
  <Last 20 lines of output from the evolutionary run>
experimenter_view: |
  <Your qualitative observations about the run. Did the fitness improve steadily? Were there any interesting behaviors observed? Did you find a stable glider?>
notes: "Executed evolutionary search for a v<c glider."
```