The current `MarginalDynamicCollisionFitness` is too strict, creating a flat fitness landscape. Your task is to implement a new, continuous fitness function named `GradedCollisionFitness` in a new file `src/fitness_g190.py`. This function will be used in a new evolutionary search script.

**Design Rationale (Incorporate into code comments):**
The goal is to reward partial progress. The fitness will be a product of a hard constraint (conservation) and a sum of desired behaviors (movement and interaction), rewarding rules that get *closer* to the goal.

**`GradedCollisionFitness` Implementation Details:**

The function should take the initial and final state of a simulation (particle coordinates, bit counts) and return a float score.

1.  **Calculate Key Metrics:**
    *   `initial_dist`: Distance between the two particles' centers of mass at step 0.
    *   `mid_dist`: Distance at the simulation's midpoint (e.g., step 200 of 400).
    *   `final_dist`: Distance at the final step.
    *   `total_displacement`: Sum of the distances traveled by each particle's center of mass from start to finish.
    *   `initial_bits`, `final_bits`.

2.  **Calculate Component Scores:**
    *   **`conservation_score`:** `min(initial_bits, final_bits) / max(initial_bits, final_bits)` if `initial_bits > 0` else `0`. This is 1.0 for perfect conservation and degrades gracefully.
    *   **`approach_score`:** `max(0, initial_dist - mid_dist)`. This rewards particles getting closer in the first half of the simulation.
    *   **`recede_score`:** `max(0, final_dist - mid_dist)`. This rewards particles moving apart in the second half.
    *   **`interaction_score`:** `approach_score + recede_score`. This rewards the 'V-shaped' distance profile of a collision.

3.  **Final Fitness Formula:**
    *   `fitness = conservation_score * (interaction_score + total_displacement)`
    *   This formula uses conservation as a primary multiplier. If conservation fails, the fitness is penalized proportionally. It then rewards both the correct interaction pattern and general movement.

**Deliverables:**
1.  A new file `src/fitness_g190.py` containing the `GradedCollisionFitness` function.
2.  A new script `src/run_g190_evolution.py` that is set up to run an evolutionary search using this new fitness function. You do not need to run the evolution, just prepare the script.
3.  Ensure the new script correctly identifies the two largest objects in the grid as the particles for distance calculation.
