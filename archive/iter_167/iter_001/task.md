## Goal
Implement the 'glider nursery' strategy. Evolve a population of C2-rules to propagate a pre-defined particle.

## Background
The previous "emerge from chaos" strategy has failed. We are pivoting to a new strategy where we provide a simple particle and evolve rules to make it move.

## Requirements
1.  **Modify `src/evolution.py` (or the main evolutionary script):**
    *   Create a new initialization function, `initialize_nursery(grid, particle_shape)`. Instead of filling the grid with random noise, it should place a single, small, pre-defined particle at the center of an empty grid.
    *   For this experiment, the particle should be a 4-bit, 2x2 square.
2.  **Implement a new Fitness Function:**
    *   The function should be named `evaluate_nursery_fitness`.
    *   It should take the final grid state and the initial particle's bit count as input.
    *   **Metric:** `displacement / (1.0 + abs(final_bit_count - initial_bit_count))`
        *   `displacement`: The displacement of the center of mass of all bits on the grid between the start (step 0) and the end (step 200).
        *   `initial_bit_count`: The bit count of the seed particle (which is 4).
        *   `final_bit_count`: The total number of `1`s on the grid at the end of the simulation.
3.  **Run the Experiment:**
    *   Generate a new random population of 100 C2-symmetric rules (using a new random seed).
    *   Evaluate this population for **one generation** using the new initialization and fitness functions.
    *   Use a 128x128 grid and run for 200 steps.
4.  **Reporting:**
    *   Log the mean and max fitness of the population.
    *   Identify the rule with the highest fitness.
    *   For the top rule, report its displacement, initial bits, and final bits.
    *   Write all results to `archive/iter_167/results/summary.json`.

## Executor Output YAML
The final YAML block in your response should include:
- `status`: ok | experiment_failed | code_error
- `artifacts`: ['results/summary.json']
- `metrics`:
    - `mean_fitness`: ...
    - `max_fitness`: ...
    - `top_rule_id`: ...
    - `top_rule_displacement`: ...
    - `top_rule_final_bits`: ...
    - `initial_bits`: 4
- `experimenter_view`: A qualitative description of the results. Did any rules successfully propagate the particle? Did most destroy it?
- `notes`: Any technical remarks.
