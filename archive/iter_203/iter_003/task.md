The goal of this task is to test the effectiveness of the new `DisplacementOverBoundingBoxFitness` function.

You must run a new evolutionary search using this function.

**Methodology:**

1.  **Find and Adapt Script:** Locate the main evolutionary search script (e.g., `src/run_evolution.py` or similar).
2.  **Configure Fitness Function:** Modify the script to import `DisplacementOverBoundingBoxFitness` from `src/new_fitness.py` and use it as the fitness function for the search.
3.  **Run Experiment:** Execute a 15-generation evolutionary search with the following parameters:
    - Population size: 100
    - Particle seed: 3-bit L-tromino
4.  **Save Results:**
    - Save the best rule found as `champion_rule.json` in `archive/iter_203.3/results/`.
    - Save the generation-by-generation fitness data as `fitness_log.csv` in `archive/iter_203.3/results/`.

**Expected Outcome:**
A report on the evolutionary run. The key question to answer is: Does this new fitness function successfully avoid the "puffer" exploit and guide the search towards discovering rules that produce coherent, sustained motion? Or does it fall into a different local optimum?