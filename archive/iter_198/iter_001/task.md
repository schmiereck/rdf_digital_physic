Diagnose the failure mechanism of the 60-degree collision for the champion rule from iter_193. The previous attempt in iter_197.1 timed out.

1.  **Load the Rule:** Use the champion rule from `archive/iter_193/iter_002/results/champion_rule.json`.
2.  **Set up the Simulation:** Create the same 60-degree collision scenario as in iter_197.1. Use a 256x256 grid.
3.  **Instrument and Run:** Run the simulation for a maximum of 800 steps. At each step, log the following metrics to a CSV file (`archive/iter_198/results/collision_log.csv`):
    *   `step`
    *   `bit_count`
    *   `num_components` (number of distinct objects/connected components)
    *   `sim_time_ms` (wall-clock time for that single step)
4.  **Visualize:** Save the final grid state as a PNG image (`archive/iter_198/results/final_state.png`).
5.  **Analyze:** In your `experimenter_view`, explicitly state the cause of the failure. Is it exponential `bit_count` growth (chaotic explosion), or is `sim_time_ms` increasing dramatically while `bit_count` remains stable (computationally expensive pattern)? This distinction is critical.