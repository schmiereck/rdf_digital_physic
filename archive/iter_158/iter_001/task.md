Modify the evolutionary search script `src/evolve.py` to run a new, independent 'Generation 1' search using a different random seed for the initial population.

**Context:** The previous attempt (iter_157) to breed a Gen-2 from a Gen-1 population failed because the initial parents had very low fitness and their advantage was not heritable. This experiment tests whether a different random starting point can yield a more promising initial population.

**Requirements:**
1.  In `src/evolve.py`, locate the main execution block.
2.  Instantiate the `EvolutionarySearch` class.
3.  Call the `run_generation` method to execute a single 'Generation 1' search.
4.  **Crucially, use a different seed for generating the initial population.** The previous run effectively used the default seed. Use a new seed, for example, `population_seed=43`.
5.  Ensure the simulation parameters are identical to iter_157 for a fair comparison:
    *   `num_steps=2000`
    *   `fitness_fn_name='late_displacement'`
    *   `population_size=100`
    *   Initial soup seed remains `42` with density `0.25`.
6.  Save the resulting population to `archive/iter_158/results/population_gen1.json`.
7.  The final YAML output from the script should include:
    *   `gen1_mean_fitness`
    *   `gen1_max_fitness`
    *   `num_viable_rules` (count of rules with fitness > 0.2)
    *   `best_rule_id`

This is a search task. I expect it to find a few viable rules, but it might take a while.