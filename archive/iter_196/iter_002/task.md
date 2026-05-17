**Goal:** Evolve a rule in a 2-bit-per-cell hexagonal grid that produces a stable, v<c (sub-light speed) glider.

**Context:** The framework has been successfully generalized to support multi-bit cells (iter_196.1). We now leverage this to search for "massive" particles, which are hypothesized to arise from internal oscillations requiring this richer state space. This is a discovery-oriented task.

**High-Level Plan for the Planner:**
1.  **Implement `SublightFitness`:** Create a new fitness function in `src/fitness.py`. This function should be a modification of the robust `CheckpointFitness` (iter_179). It must reward displacement while simultaneously penalizing high velocities that approach v=1c. A possible formula is: `fitness = displacement * num_checkpoints_passed * (1.0 - velocity)`, where `velocity = displacement / total_steps`. This creates a fitness landscape that prefers slower, coherent motion over the v=1c gliders previously discovered.
2.  **Configure and Run Evolution:**
    *   Set up an evolutionary search using the newly generalized framework with `BITS_PER_CELL=2`.
    *   Use the new `SublightFitness` function.
    *   The search space for 2-bit rules is vast (a `2^14 = 16384` entry LUT). You may need to adjust evolutionary parameters (e.g., population size, mutation rate, number of generations) accordingly. Use the standard L-tromino seed particle.
3.  **Analyze and Validate:**
    *   After the search completes, identify the champion rule with the highest fitness.
    *   Rigorously validate the champion. Run a long simulation and measure its velocity to confirm it is stable and `0 < v < c`.
    *   Visualize the champion particle's dynamics by generating a GIF. This is crucial to ensure the high fitness score is not the result of a known exploit (e.g., "bloomers", "puffers", or measurement artifacts).

**Success Criterion:**
The phase is successful if you discover and validate at least one rule that produces a particle with a stable, non-zero bit-count that travels at a consistent average velocity significantly below `v=1c` for at least 1000 steps. The final `result.yaml` must include the champion rule, its measured velocity, and the path to the confirmation GIF.