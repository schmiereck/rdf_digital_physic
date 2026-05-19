Based on the analysis in `archive/iter_216/results/fitness_analysis.md`, implement the new `SubLightFitness` function.

**Requirements:**

1.  **Modify `src/fitness_functions.py`:** Add a new class `SubLightFitness` to this file.
2.  **Implement Core Logic:** The new class must implement the features designed in the analysis:
    *   **Unwrapped Coordinates:** Track the center of mass using unwrapped coordinates to correctly calculate velocity across toroidal boundaries.
    *   **Period Detection:** Implement a mechanism to detect the period of a particle's internal state. A simple way is to store a history of the particle's bit-pattern (relative to its center of mass) and find the first time a pattern repeats.
    *   **Velocity Gate:** Add a hard check that returns a fitness of 0.0 if the average velocity is `>= 0.9c` or the detected period is `<= 1`.
    *   **Fitness Formula:** Combine the metrics into a final fitness score. A good starting point is `fitness = displacement * (1 - 1/period)`.

3.  **Ensure Integration:** Make sure the new class inherits from the same base class as the other fitness functions and is correctly importable by the evolution script. Do not modify the evolution script itself in this step.
4.  **Docstrings:** Add a clear docstring to the `SubLightFitness` class explaining its purpose, its formula, and why it's designed to avoid `v=1c` gliders.