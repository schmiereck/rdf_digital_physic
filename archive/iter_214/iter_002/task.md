Validate the new `LateWindowDisplacementFitness` function from `src/fitness_v_lessthan_c.py`.
1. Load the champion rule that caused the 'transient drift' exploit. This rule is located at `archive/iter_213/iter_213.10/results/champion.json`.
2. Load the standard 3-bit L-Tromino seed.
3. Run a simulation for 1000 steps using this rule and seed.
4. Evaluate the simulation using the `LateWindowDisplacementFitness` function.
5. The success criterion is a final fitness score of exactly 0.0. The script should fail if the fitness is not 0.0.
6. Write the calculated fitness and a success message to `archive/iter_214/results/validation.txt`.