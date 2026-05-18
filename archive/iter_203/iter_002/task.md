The goal is to create a new fitness function that is robust to the "puffer" exploit identified in `iter_203.1`.

Create a new Python file named `src/new_fitness.py`. Inside this file, define a class named `DisplacementOverBoundingBoxFitness`.

**Requirements:**

1.  **Inheritance:** The class must inherit from `BaseFitness` (you can find this in `src/fitness_functions.py`).
2.  **Bit Conservation:** The function must check for perfect bit conservation. If the initial and final bit counts do not match, the fitness must be `0.0`.
3.  **Core Logic:** The fitness value should be calculated as `metrics['cumulative_displacement'] / (1 + metrics['max_bounding_box_diagonal'])`.
    - The `+ 1` in the denominator is to prevent division-by-zero errors.
4.  **`__call__` method:** The logic should be implemented within the `__call__` method, which takes `initial_grid`, `final_grid`, and `metrics` as input and returns a float (the fitness value).

You only need to write the file. Do not run any experiments.