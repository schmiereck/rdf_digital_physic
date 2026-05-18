## Goal

Configure and run an evolutionary search using `src/main_v2.py` to find a sub-light-speed glider.

## Configuration

You MUST use the `CumulativeDisplacementFitness` function. Ensure the following parameters are set for the evolutionary run, modifying `src/main_v2.py` if necessary:

*   **Fitness Function:** `CumulativeDisplacementFitness`
*   **Seed Particle:** 3-bit L-Tromino
*   **Grid Size:** 128x128 (Torus)
*   **Population Size:** 100 rules
*   **Elite Proportion:** 10% (0.1)
*   **Number of Generations:** 15

## Execution

1.  Run the evolutionary search by executing the `src/main_v2.py` script.
2.  The script should identify the champion rule (the one with the highest fitness) from the final generation.
3.  Save the champion rule's JSON representation to `archive/iter_202.2.1/results/champion_rule.json`.
4.  Write a summary of the run to `archive/iter_202.2.1/results/evolution_summary.txt`. The summary must include the final fitness score of the champion rule and the total number of generations completed.

## Final Report

Your final YAML report must include:
*   `status`: `ok` if the evolution completes successfully, otherwise `experiment_failed`.
*   `artifacts`: A list containing the paths to the champion rule and the summary text file.
*   `metrics`: A dictionary containing the final fitness score of the champion rule, e.g., `{'final_fitness': 123.45}`.
*   `experimenter_view`: A qualitative summary of the evolutionary process, noting if fitness appeared to be increasing and if the run was stable.
```