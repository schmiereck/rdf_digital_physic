
**Goal:** Configure and run a multi-generational evolutionary search to find a rule supporting a stable, bit-conserving, sub-light speed glider.

**Instructions:**

1.  **Create a new Python script:** `src/run_evolution_exp_220.py`.

2.  **Implement the script:**
    *   The script should import necessary components from the `src` directory (e.g., `Evolution`, `DisplacementConsistencyFitness`, particle seeds).
    *   Configure the evolutionary search with the following parameters:
        *   **Fitness Function:** `DisplacementConsistencyFitness`
        *   **Seed Particle:** Use the 3-bit L-Tromino particle.
        *   **Population Size:** 100
        *   **Number of Generations:** 20
    *   The script must run the evolutionary search.
    *   Throughout the run, it should track the best rule (champion) found across all generations.

3.  **Define Outputs:**
    *   After the evolution is complete, the script must save the champion rule's definition to `archive/iter_220/results/champion_rule.json`.
    *   The script must also save a summary of the evolutionary process (best and mean fitness per generation) to `archive/iter_220/results/evolution_summary.csv`.

4.  **Execute the script:**
    *   After creating the script, execute it using `python src/run_evolution_exp_220.py`.

5.  **Final YAML Report:**
    *   The YAML report should include the paths to the two output files in the `artifacts` list.
    *   The `metrics` should report the final fitness of the champion rule.
    *   The `experimenter_view` should briefly analyze the run, noting if fitness plateaued.
    ```yaml
    status: ok
    artifacts:
      - "archive/iter_220/results/champion_rule.json"
      - "archive/iter_220/results/evolution_summary.csv"
    metrics:
      champion_fitness: <final fitness of the best rule>
    log_excerpt: |
      ... (last 20 lines of stdout from the python script)
    experimenter_view: |
      ... (brief analysis of the run)
    notes: "Evolutionary search completed as configured."
    ```
