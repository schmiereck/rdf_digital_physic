The analysis of sub-task 188.1 revealed that the previous `CollisionFitness` function was flawed, as it was exploited by a rule that creates static still-lifes instead of moving gliders. The particles never collided, yet the end-state check was satisfied.

This sub-task is to design a new, more robust fitness function and re-run the evolutionary search to find a rule that produces genuine, dynamic, and conserving collisions.

**Instructions:**
1.  **Design `DynamicCollisionFitness`:** Implement a new fitness function that explicitly rewards the dynamics of a collision. It must verify four conditions to return a score of 1.0, otherwise it returns 0.0:
    a.  **Approach:** The distance between the two particles at a midpoint (e.g., step 50) must be less than the initial distance.
    b.  **Recession:** The distance between the particles at the end (e.g., step 100) must be greater than the midpoint distance.
    c.  **Bit Conservation:** `final_bit_count` must equal `initial_bit_count` (6).
    d.  **Object Conservation:** `final_object_count` must equal `initial_object_count` (2).
2.  **Validate the new Fitness Function:** As a sanity check, confirm that this new function correctly assigns a fitness of 0.0 to the static rule from `iter_187.2`.
3.  **Run Evolutionary Search:** Launch a new evolutionary search using `DynamicCollisionFitness`. Run for at least 10 generations with a population of 100 `C2-symmetric` rules. The simulation horizon for each evaluation should be 100 steps.
4.  **Report Results:**
    *   If a rule with fitness 1.0 is found, save it as `archive/iter_188/results/dynamic_champion_rule.json`.
    *   Generate an animation of this rule's collision behavior and save it as `archive/iter_188/results/dynamic_champion_collision.gif`.
    *   Report the generation in which the champion rule was found.