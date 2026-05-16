
Create a new script `src/run_iter_189_evolution.py` to conduct an evolutionary search for rules that produce dynamic, two-body collisions.

**Requirements:**

1.  **Integrate Fitness Function:**
    *   Copy the `MarginalDynamicCollisionFitness` class and any necessary helper functions from `src/fitness/iter_189_fitness_validation.py` into the new script.

2.  **Evolutionary Setup:**
    *   Start with a new, randomly generated population of 100 rules.
    *   Use the `ca_config_2d_hex_128_torus_2_particles_3_bit_ltromino` configuration for the CA simulation.
    *   Set the simulation `steps` to 400.
    *   The `MarginalDynamicCollisionFitness` function should be configured with `midpoint=200` and `margin=1.0`.

3.  **Execution Loop:**
    *   Run the evolutionary algorithm for a maximum of 10 generations.
    *   In each generation, evaluate the fitness of all rules in the population.
    *   The primary goal is to find a "champion" rule with a fitness of exactly `1.0`.

4.  **Champion Handling:**
    *   If a champion rule (fitness == 1.0) is discovered, the evolution should stop immediately.
    *   Save the champion rule's JSON data to `archive/iter_189/results/champion_rule.json`.
    *   Generate a GIF visualization of the champion rule's simulation, showing the collision dynamics. Save this animation as `archive/iter_189/results/collision.gif`.

5.  **Reporting:**
    *   The script's final YAML output should report:
        *   `status`: `ok` if a champion is found, `experiment_failed` otherwise.
        *   `metrics`:
            *   `champion_found`: `true` or `false`.
            *   `generations_ran`: The number of generations completed before stopping.
            *   `best_fitness`: The fitness of the champion rule, or the best fitness found if no champion emerged.
        *   `artifacts`: A list of the created files (`champion_rule.json`, `collision.gif`).
        *   `experimenter_view`: A brief qualitative description of the outcome (e.g., "Champion rule found in generation 5. The visualization shows a clean two-body collision and reaction."). If no champion is found, describe the best behavior observed.

This is a self-contained task. The script should perform the setup, execution, and reporting as described.
