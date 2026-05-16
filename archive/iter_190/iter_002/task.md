Run an evolutionary search for 10 generations using the new `StagedCollisionFitness` function implemented in sub-task 190.1.

**Goal:** Determine if the new staged fitness landscape allows for evolutionary progress, measured by an increase in population fitness over time.

**Framework:** Use the existing evolutionary search script (e.g., `src/evolution.py`).

**Configuration:**
- **Fitness Function:** `StagedCollisionFitness`.
- **Generations:** 10.
- **Population Size:** 100.
- **Elite Fraction:** 0.1.
- **Particle Seed:** Use the standard two L-tromino setup defined in the `StagedCollisionFitness` implementation.
- **Grid Size:** 128x128 torus.

**Success Criterion:**
The experiment will be considered a success if the evolutionary search finds a champion rule with a fitness score of 1.0 or 2.0. A secondary success criterion is observing a clear positive trend in the mean fitness of the population across the 10 generations.

**Outputs:**
- Log the fitness statistics (mean, max, std) for each generation.
- Save the final population, especially the champion rule(s), to the results directory.
- Generate a plot showing the max and mean fitness per generation.
- If a champion with fitness >= 1.0 is found, generate a GIF visualizing its dynamics.