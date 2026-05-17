Goal: Run an evolutionary search to find a rule that produces a v<c glider using the new fitness function and particle.

1.  **Modify the main evolution script `src/evolve.py`:**
    *   Import `MassiveGliderFitness` and `T_TROMINO_PARTICLE` from the newly created `src/massive_glider_fitness.py`.
    *   Locate the main execution block (e.g., `if __name__ == "__main__"`) and reconfigure the `Evolution` class instance.
    *   Set the `fitness_fn` parameter to an instance of `MassiveGliderFitness`.
    *   Set the `particle_shape` parameter to `T_TROMINO_PARTICLE`.
    *   Configure the search parameters:
        *   `generations`: 50
        *   `population_size`: 100
    *   Ensure the script is configured to save the champion rule at the end of the run.

2.  **Execute the search:**
    *   Run the modified `src/evolve.py`. This will start the multi-generational search.

3.  **Process and save the results:**
    *   After the search completes, identify the champion rule (the one with the highest fitness).
    *   Save the champion rule's dictionary to a JSON file at `archive/iter_197.2/results/champion_rule.json`.
    *   **Crucially, validate and characterize the champion:**
        *   Run a longer simulation of the champion rule with the `T_TROMINO_PARTICLE`.
        *   Calculate and report its final fitness score and, most importantly, its measured velocity vector `(vx, vy)` and speed.
        *   Generate a visualization of the glider. A GIF animation saved to `archive/iter_197.2/results/champion_glider.gif` would be ideal. If creating a GIF is too complex, save a sequence of frames (e.g., `frame_000.png`, `frame_001.png`, etc.) in a directory `archive/iter_197.2/results/frames/`.

4.  **Final YAML block:**
    *   The `metrics` field must include the champion's `fitness_score`, `velocity_x`, `velocity_y`, and `speed`.
    *   The `artifacts` field should list the saved rule file and the visualization (GIF or frame directory).
    *   The `experimenter_view` should describe the outcome of the search and the characteristics of the discovered glider.