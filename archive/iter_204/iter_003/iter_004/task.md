
Your task is to run a full evolutionary search for a `v<c` glider using the `src/run_vc_search.py` script.

### 1. Configure the search
Open `src/run_vc_search.py` and ensure the main execution block is configured with the following parameters:
- **Fitness Function**: `NetDisplacementFitness`
- **Population Size**: 100
- **Generations**: 20
- **Seed**: 3-bit L-tromino (ensure the `tromino_l_3bit` seed is used).

### 2. Run the experiment
Execute the configured script: `python src/run_vc_search.py`. The script is expected to run the evolutionary algorithm and print fitness statistics for each generation.

### 3. Save the results
- **Fitness Log**: The script should already be saving a fitness log. Ensure it is written to `archive/iter_204.3/results/fitness_log.csv`. This file should contain columns for `generation` and `max_fitness`.
- **Champion Rule**: Identify the rule with the highest fitness at the end of the run. Save its JSON representation to `archive/iter_204.3/results/champion_rule.json`.

### 4. Report
Your final YAML report must include:
- `status`: `ok` if the run completes, `experiment_failed` otherwise.
- `artifacts`: A list of the files you created (e.g., `['archive/iter_204.3/results/fitness_log.csv', 'archive/iter_204.3/results/champion_rule.json']`).
- `metrics`: Report the `max_fitness` achieved.
- `experimenter_view`: A summary of the search outcome. Address these questions:
    - Was a stable `v<c` glider found?
    - What was the maximum fitness, and in which generation was it achieved?
    - Did the fitness curve plateau, suggesting convergence, or is more evolution needed?
- `log_excerpt`: The last 20 lines of the script's standard output, showing the fitness progression in the final generations.
