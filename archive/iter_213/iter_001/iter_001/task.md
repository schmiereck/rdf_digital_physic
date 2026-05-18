
Create a new Python script at `src/run_robust_vc_search.py`. This script will perform an evolutionary search for a `v<c` glider.

The script must implement a new, robust fitness function that combines the following four principles:

1.  **Net Displacement (Primary Metric):** The core fitness value must be the Euclidean distance between the particle's center of mass at the start and the end of the simulation.
2.  **Strict Bit Conservation (Constraint):** The fitness function must check the particle's bit count at multiple checkpoints (e.g., steps 100, 200, 300, 400). If the bit count at any checkpoint does not match the initial bit count of the seed particle (3 bits for the L-Tromino), the fitness for that rule must be immediately returned as `0.0`.
3.  **Phase-Sampling (Anti-Oscillator Constraint):** To defeat periodic oscillators, the final position for the displacement calculation must be the average of the center of mass over the last 4 steps of the simulation (e.g., steps 397, 398, 399, 400).
4.  **Compactness (Penalty):** The final fitness score should be penalized by the size of the particle's bounding box. The formula should be `Fitness = NetDisplacement / (1 + BoundingBoxArea)`.

**Evolutionary Algorithm Details:**

*   **Seed Particle:** Use the 3-bit L-Tromino, defined as `[[0, 1], [1, 1], [1, 0]]`.
*   **Population Size:** 100.
*   **Generations:** Run for a minimum of 10 generations. The script should be able to run for more, e.g., 20. Make this a command-line argument.
*   **Simulation Steps:** 400 steps for each fitness evaluation.
*   **Mutation Rate:** 0.05.
*   **Tournament Size:** 5.

**Output:**

*   The script must save the best rule found to `archive/iter_213.1/results/champion_rule.json`.
*   It must log the progress (generation, best fitness, mean fitness) to `archive/iter_213.1/results/evolution_log.csv`.
*   It should also save the final population to `archive/iter_213.1/results/final_population.json`.

**Dependencies:**

Assume `automata-lib` is installed and provides the necessary components (`Grid`, `Automaton`, `rules`, `seeds`). If you need to implement helper functions (e.g., for center of mass, bounding box), do so within the script.

The script should be executable from the command line, e.g., `python src/run_robust_vc_search.py --generations 15`.
Make sure to create the output directory `archive/iter_213.1/results/` before writing files.

Final YAML block must be correct.
