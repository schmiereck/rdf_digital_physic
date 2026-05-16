**Goal:** Implement a new fitness function, `DynamicCollisionFitness`, validate it, and use it to run an evolutionary search to find a cellular automaton rule for a dynamic, conserving collision.

**1. Update Fitness Function Implementation**

Modify or create `src/fitness.py` to include a new class `DynamicCollisionFitness`. This class must evaluate a rule based on a simulation of two 3-bit "gliders" colliding.

*   **Initial State:** A 64x64 grid with two 3-bit objects.
    *   Object 1 at (30, 20), (31, 20), (30, 21).
    *   Object 2 at (33, 43), (34, 43), (33, 44).
*   **Simulation Horizon:** 100 steps.
*   **Fitness Logic:** The `evaluate` method should return 1.0 if and only if ALL four of the following conditions are met. Otherwise, it should return 0.0.
    1.  **Approach:** The distance between the centers of mass of the two objects at the simulation midpoint (step 50) must be *less than* the initial distance.
    2.  **Recession:** The distance between the centers of mass at the final step (step 100) must be *greater than* the midpoint distance.
    3.  **Bit Conservation:** The total number of 'on' cells in the final state must be exactly 6 (the same as the initial state).
    4.  **Object Conservation:** The number of distinct objects (connected components) in the final state must be exactly 2.

    You will likely need `scipy.ndimage.label` to count objects and `scipy.ndimage.center_of_mass` to find their positions.

**2. Create a New Execution Script: `src/run_dynamic_evolution.py`**

This script will orchestrate the validation and the new search.

*   **Part A: Validation:**
    *   Load the champion rule from `archive/iter_187/results/champion_rule.json`.
    *   Instantiate `DynamicCollisionFitness` and evaluate the loaded rule.
    *   Print the result. You must verify that the fitness score is 0.0. If it is not, report a failure in the validation step and stop.

*   **Part B: Evolutionary Search:**
    *   If validation is successful, configure and run a new evolutionary search.
    *   **Population:** 100 individuals.
    *   **Rule Type:** `C2-symmetric`.
    *   **Generations:** 10.
    *   **Fitness Function:** `DynamicCollisionFitness(horizon=100)`.

*   **Part C: Results and Reporting:**
    *   If a rule with fitness 1.0 is found (a "champion"):
        1.  Stop the search.
        2.  Save the champion rule to `archive/iter_188/results/dynamic_champion_rule.json`.
        3.  Generate a GIF animation of the champion rule's collision simulation (100 steps) and save it to `archive/iter_188/results/dynamic_champion_collision.gif`.
    *   If no champion is found after 10 generations, report this clearly.

**3. Execution and Output**

*   Run the `src/run_dynamic_evolution.py` script.
*   The script should create the output directory `archive/iter_188/results/` if it doesn't exist.
*   Your final output must be the standard YAML block reporting the outcome of the experiment.
    *   If a champion is found, `status` should be `ok`, and the `metrics` should include `champion_found: 1` and `champion_generation`. List the generated files in `artifacts`.
    *   If no champion is found, `status` should still be `ok`, but `metrics` should be `champion_found: 0`.