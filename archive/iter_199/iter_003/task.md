Develop and validate a new, exploit-resistant fitness function for discovering `v<c` gliders.

1.  **Implement New Fitness Function:**
    *   Create a new Python file: `src/fitness_v2.py`.
    *   In this file, define a new class `SparseGliderFitness`. This function should build upon the principles of `CheckpointFitness` (measuring displacement and bit-conservation at multiple time points).
    *   Add a **sparsity penalty/bonus**. At each checkpoint, calculate the particle's bounding box. The sparsity score should be high for compact particles and low for diffuse, grid-filling patterns. A good metric would be `bit_count / (bounding_box_area)`.
    *   The final fitness should combine the net displacement and the average sparsity score, while still being zero if bit conservation fails at any checkpoint.

2.  **Validate Against Known Exploit:**
    *   The sub-planner in `iter_197.2` produced a champion rule and an initial seed that exploited the old fitness function, resulting in a grid-filling pattern.
    *   Create a script `src/validate_fitness.py` that loads this known "bad" rule and seed.
    *   Run a short simulation (e.g., 200 steps) of this exploit pattern.
    *   Evaluate the final state using the new `SparseGliderFitness` function.

3.  **Report:**
    *   The primary success metric is the fitness score assigned to the known exploit pattern. A score near zero confirms the new function successfully rejects the exploit.
    *   In the `experimenter_view`, clearly state the score the new function gives to the exploit pattern and confirm that the sparsity term is working as intended.
    *   Place the new `SparseGliderFitness` implementation in `src/fitness_v2.py` and the validation script in `src/validate_fitness.py`. These files should be listed in the artifacts.