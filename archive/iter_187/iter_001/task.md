The previous rule, g10_rule_001, produced stable gliders but had catastrophic collision dynamics. The next step is to evolve a new rule that specifically rewards elastic collisions.

Your task is to create the necessary software framework for this new evolutionary search.

1.  **Create a new fitness function `CollisionFitness` in `src/fitness_functions.py`**. If the file does not exist, create it.
    *   This class's `__init__` method should accept the CA rule.
    *   The `__call__` method must perform a simulation of a collision.
    *   **Initial State:** Create a 128x128 toroidal grid. Place two 3-bit 'L-tromino' particles on a head-on collision course. For example, place one at (48, 64) and the other, rotated 180 degrees, at (80, 64). They should move towards each other. The `initial_bit_count` is 6.
    *   **Simulation:** Run the CA for 100 steps. This should be enough time for the particles to collide and for the immediate aftermath to become clear.
    *   **Fitness Calculation:** The fitness score must reward bit conservation and object conservation. A simple and effective formula would be: `fitness = (initial_bit_count / final_bit_count) * (2 / final_object_count)`.
        *   `final_bit_count` is the total number of set bits on the grid after 100 steps.
        *   `final_object_count` is the number of distinct connected components (objects) on the grid after 100 steps. You can use a standard library like `scipy.ndimage.label`.
        *   Handle division by zero: if `final_bit_count` or `final_object_count` is zero, the fitness should be 0.
    *   **Ideal Score:** A perfect elastic collision (two 3-bit objects become two 3-bit objects) would yield a fitness of `(6/6) * (2/2) = 1.0`. Annihilation, fusion, or explosion will result in scores less than 1.0.

2.  **Create a new main script `src/run_evolution_elastic.py`**.
    *   This script should orchestrate the evolutionary search using the new `CollisionFitness`.
    *   Use the structure of previous evolutionary scripts (e.g., `src/run_iter_179_evolution.py`) as a template for the main loop: population initialization, generation loop, selection (top 10%), crossover, and mutation.
    *   **Configuration:** Population size 100, 10 generations.
    *   **Output:** The script should print the best fitness score of each generation. After the final generation, it must save the best rule found (its kernel definition) to `archive/iter_187/results/best_elastic_rule.json`.

Ensure the code is clean, commented, and ready for immediate execution by the next agent.