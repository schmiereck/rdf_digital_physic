**Goal:** Develop a new, exploit-resistant fitness function for `v<c` glider discovery.

**Task:**
1.  Create a new Python file: `src/new_fitness.py`.
2.  In this file, implement a new fitness function class named `DisplacementConsistencyFitness`.
3.  This function should be designed to reward consistent, directional motion and penalize stationary or oscillating "drifters".
4.  **Implementation Logic:**
    a. The `__call__` method should take a simulation history (`sim_history`) as input.
    b. Divide the simulation into a number of windows (e.g., 4 or 5).
    c. For each window, calculate the displacement vector and the velocity (displacement / steps_in_window).
    d. Calculate the mean of these windowed velocity vectors.
    e. Calculate the standard deviation of the windowed velocity magnitudes.
    f. Implement the core fitness formula: `fitness = mean_velocity_magnitude / (1 + std_dev_velocity_magnitudes)`.
    g. Incorporate the "leaky" bit conservation logic from `LeakyCheckpointFitness`: multiply the final score by the `total_conservation_score`.
    h. The function should return the final fitness score.
5.  Add comments to the file explaining the logic and why it is resistant to the "drifter" exploit.
6.  The task is successful when `src/new_fitness.py` is created and contains the correctly implemented class. Do not write tests or validation scripts.