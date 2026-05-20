Implement and run the complete 72-orbit C2-symmetric evolutionary search in `src/run_evolution_exp_222.py`.

Key instructions:
1. Compute the C2-rotation orbit mapping for all 128 local neighborhood states (where bit 6 is center, bits 5..0 are East, South-East, South-West, West, North-West, North-East). Ensure it results in exactly 72 unique orbits.
2. Form the 72-orbit-based chromosome where chrom_72 is an array/list of length 72. Define `chromosome_72_to_rule_dict` and `rule_dict_to_chromosome_72` to convert between 72-orbit representation and standard rule_dict.
3. Load rules from `archive/iter_215/results/final_population.json`. Reconstruct their 128-state LUT, project/symmetrize them into 72-orbit chromosomes, and form the initial population of size 100. If there are fewer than 100 rules, pad the population by taking random warm-start chromosomes and mutating them (applying bit flips).
4. Implement standard Genetic Algorithm operations directly on the 72-orbit chromosomes:
   - Elitism: carry over the top 10 elites.
   - Selection: tournament selection (size 3) from the current population.
   - Crossover: uniform or single-point crossover with probability 0.5.
   - Mutation: independent bit-flip mutation with probability 0.02 per bit.
5. Evaluate fitness using:
   - Perfect per-step unwrapped CoM tracking (accumulating step-to-step unwrapped deltas rather than resetting the reference to raw CoM, to avoid backward jumps).
   - DisplacementConsistencyFitness(num_windows=5, max_bit_threshold=12, max_velocity_threshold=0.9, min_velocity=0.02) from `src/new_fitness.py`.
6. Use ProcessPoolExecutor to parallelize evaluations across workers. Define the worker at module level to make it pickleable.
7. Run the evolutionary search for 50 generations with population size 100, elite size 10.
8. Output the following to `archive/iter_222/results/`:
   - `champion_rule_perfect.json`: a JSON file containing the champion rule meta-data and rule dictionary.
   - `evolution_summary_perfect.csv`: a CSV logging generation, best_fitness, and mean_fitness.
   - `champion_vc_glider_perfect.gif`: a high-quality GIF of the champion glider moving in the hexagonal grid.
9. Perform a detailed 500-step characterization of the champion:
   - Track its active cells and unwrapped center-of-mass trajectory.
   - Verify it is a genuine, stable v<c glider (i.e. does not go extinct, does not grow without bound, and travels with a stable speed v < c).
   - Write a detailed analysis summary to `archive/iter_222/results/trajectory_analysis.txt` detailing its period, speed, displacement, and bit count over the 500 steps.