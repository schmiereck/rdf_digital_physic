Create a new fitness function `StableMassFitness` in a new file `src/fitness_v_c.py` to guide the search for `v<c` gliders. This new function must fix the "grid-filling" exploit seen in `iter_197.2`.

**Requirements:**

1.  **File:** Create a new file `src/fitness_v_c.py`.
2.  **Class `StableMassFitness`:** Implement a class that inherits from a base fitness class (you may need to create a simple one or assume one exists).
3.  **Core Logic:** The fitness calculation must robustly identify compact, moving objects with a constant bit count and sub-light speed.
    - **Perfect Conservation:** The function must first check for perfect bit conservation. If `final_bit_count != initial_bit_count`, the fitness must be `0.0`.
    - **Center of Mass (CoM) Velocity:** Calculate the CoM at several checkpoints (e.g., at steps 200, 400, 600, 800). Calculate the displacement vectors between checkpoints.
    - **Velocity Stability:** The primary score should be based on the consistency of these displacement vectors. A low standard deviation in the vectors' components indicates constant velocity. A particle that stops or changes speed should get a low score.
    - **Dispersion Penalty (CRITICAL):** This is the key to defeating the grid-filling exploit. Calculate the standard deviation of all 'on' cell coordinates relative to the CoM at the final step. A compact particle will have a low standard deviation, while a dispersed, grid-filling pattern will have a very high one.
    - **Final Fitness Formula:** Combine these elements. A suggested formula is: `(mean_displacement_magnitude) / (1.0 + velocity_std_dev + final_dispersion)`. This rewards movement while heavily penalizing instability and non-compactness. A stationary object (zero displacement) should have a fitness of 0.

**Deliverable:**
The file `src/fitness_v_c.py` containing the `StableMassFitness` class, ready to be imported and used in an evolutionary search script.