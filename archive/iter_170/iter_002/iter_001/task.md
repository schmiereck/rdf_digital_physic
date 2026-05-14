## Goal
This task is to create and evaluate a second generation (Gen-1) of cellular automata rules to test if the L-tromino particle motion is an evolvable trait.

## Instructions
1.  Create a new Python script `src/evolve.py`.
2.  The script must read the results of the previous generation from `archive/iter_170/results/gen_0_results.json`.
3.  Implement the following genetic algorithm components:
    *   **Tournament Selection:** Select parent rules from the Gen-0 population. The tournament size should be 3.
    *   **Uniform Crossover:** Combine pairs of parent rules with a crossover probability of 0.5 for each bit.
    *   **Bit-flip Mutation:** Mutate the offspring with a mutation probability of 0.01 for each bit.
4.  Generate a new population of 100 rules (Gen-1) by applying selection, crossover, and mutation.
5.  Evaluate the fitness of each rule in the new Gen-1 population using the *exact same simulation and fitness function* as in the previous iteration (170.1). You can reuse code from `src/evaluate_rules.py`. The key simulation parameters are:
    *   Seed: "L-tromino"
    *   Simulation steps: 200
    *   Fitness metric: Displacement of the center of mass.
6.  After evaluating all 100 rules, calculate the maximum, mean, and minimum fitness for the Gen-1 population.
7.  Save the complete results for the new generation into a file at `archive/iter_170/results/gen_1_results.json`. The JSON file should contain the summary statistics (`max_fitness`, `mean_fitness`, `min_fitness`) and the list of all individual rules and their corresponding fitness scores.
8.  Execute the `src/evolve.py` script.
9.  In your final YAML block, report the `max_fitness`, `mean_fitness`, and `min_fitness` of the Gen-1 population in the `metrics` field.
