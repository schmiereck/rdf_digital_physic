
We are debugging a persistent failure. The task is now to break the problem down. Your goal is to create and validate only the fitness function.

**Task 1: Create the Fitness Function File**

Create a new file at `src/fitness.py`. Inside this file, implement a Python class or function named `RobustGliderFitness`. This function must encapsulate the complex logic we have designed.

The `__call__` method or function signature should accept a `rule_string` as input and return a float `fitness_score`.

The logic for the fitness score must be as follows:
1.  **Initialization:**
    *   Use the 3-bit L-Tromino seed: `[[0, 1], [1, 1], [1, 0]]`.
    *   The initial bit count is 3.
    *   The simulation runs for 400 steps.
2.  **Bit Conservation Check:**
    *   Check the bit count at steps 100, 200, 300, and 400.
    *   If the bit count at *any* of these checkpoints is not equal to 3, immediately return a fitness score of `0.0`.
3.  **Displacement Calculation:**
    *   Calculate the center of mass at the start (step 0).
    *   Calculate the center of mass at steps 397, 398, 399, and 400.
    *   The final center of mass is the average of these four positions.
    *   The net displacement is the Euclidean distance between the start and final center of mass.
4.  **Compactness Penalty:**
    *   Calculate the area of the bounding box of the particle at the final step (400).
    *   The final fitness score is `NetDisplacement / (1.0 + BoundingBoxArea)`.

**Task 2: Create a Validation Script**

Create a second file at `src/test_fitness.py`. This script will test the `RobustGliderFitness` function.

1.  **Import:** Import the `RobustGliderFitness` function from `src/fitness.py`.
2.  **Test Case 1: Stationary Oscillator:**
    *   Define a rule string known to produce a stationary pattern (e.g., the original Game of Life rule `B3/S23` might work, or a simple rule that does nothing).
    *   Calculate the fitness for this rule.
    *   Assert that the fitness score is less than `0.1`, as its net displacement should be near zero.
3.  **Test Case 2: Puffer/Unstable Rule:**
    *   Define a rule string that is known to be unstable and change bit count. A simple rule like `B1/S1` will likely cause the L-Tromino to decay.
    *   Calculate the fitness for this rule.
    *   Assert that the fitness score is exactly `0.0` due to the bit conservation check.

**Task 3: Execute Validation**

Run the test script using `python src/test_fitness.py`. The command must succeed.

Your final output should report on the success of the tests.
