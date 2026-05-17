Goal: Create a new fitness function and particle definition for discovering v<c gliders.

1.  **Create a new file:** `src/massive_glider_fitness.py`.

2.  **Define the seed particle:**
    *   Inside this new file, define a 4-bit asymmetric particle. A T-tromino is a good choice. It should be represented in a format compatible with the existing simulation code (likely a list of coordinate offsets).
    *   Name the particle `T_TROMINO_PARTICLE`.

3.  **Implement the `MassiveGliderFitness` class:**
    *   Create a class named `MassiveGliderFitness`. It should be designed to work with the existing evolutionary framework. You may need to inspect other fitness function files in `src/` to understand the required interface (e.g., `__init__`, `evaluate`).
    *   The core logic of the `evaluate` method should be as follows:
        a. Initialize a simulation with the provided rule and the `T_TROMINO_PARTICLE`.
        b. Run the simulation for a set number of steps (e.g., 200) to let the pattern stabilize.
        c. **Measure velocity:** Calculate the center of mass at two points in time (e.g., step 200 and step 300). The velocity vector `v` is `(pos_300 - pos_200) / 100`.
        d. **Filter velocities:**
           *   If `v` is zero (the object is stationary or oscillating), return a fitness of 0.
           *   If the magnitude of `v` is close to 1 in any cardinal or diagonal direction (i.e., it's a standard `v=c` glider), return a fitness of 0. We are exclusively looking for `0 < |v| < 1`.
        e. **Verify constant velocity:** Continue the simulation for a longer duration (e.g., up to 1000 steps). At regular intervals (e.g., every 100 steps), predict the expected position using the measured velocity `v` and compare it to the actual center of mass.
        f. **Calculate fitness:** The fitness score should be proportional to how long the particle maintains its constant, non-integer velocity. For example, the score could be the number of successful checkpoint validations. Add a bonus for complexity (larger population size) to encourage "massive" gliders.
    *   Ensure the file is well-commented, especially the logic for velocity calculation and fitness evaluation.

4.  **Final Output:**
    *   The primary output should be the file `src/massive_glider_fitness.py`.
    *   No simulation needs to be run in this step. The goal is purely code implementation.
    *   The executor's final YAML block should report `status: ok` if the file is created successfully.