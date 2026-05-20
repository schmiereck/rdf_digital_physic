Create and execute the main evolutionary search script `src/run_evolution_exp_221.py`.

Requirements:
1. Copy the structure of `src/run_evolution_exp_220_fixed.py`.
2. Modify it to support **warm-starting** from `archive/iter_215/results/final_population.json`.
   - If the warm-start file is found, load the 100 rules, extract their rule dictionaries under key `rule_dict`, convert them to chromosomes using `rule_dict_to_chromosome()`, and use them as Generation 0.
   - If the file is not found or has fewer than 100 rules, fall back to generating random C2 rules to fill the population.
3. Configure the fitness function to be `DisplacementConsistencyFitness` from `src/new_fitness.py` with:
   - `max_bit_threshold = 12` (to prevent breeders/growth exploits)
   - `max_velocity_threshold = 0.9` (to enforce sub-light speed)
   - `num_windows = 5`
   - `min_velocity = 0.05` (to reject stationary/frozen rules)
4. Run the evolution for **30 generations** with a population size of **100** and elite size of **10**.
5. Save all outputs under the directory `archive/iter_221/results/`:
   - `champion_rule.json` (champion metadata, dictionary, and parameters)
   - `evolution_summary.csv` (best_fitness and mean_fitness per generation, pandas-free)
   - `final_population.json` (the final population of 100 rules with their chromosomes and fitness scores)
   - `champion_vc_glider.gif` (GIF animation of the champion rule)
6. Ensure that the directories are created if they do not exist, and print progress updates after each generation. Do NOT use pandas.