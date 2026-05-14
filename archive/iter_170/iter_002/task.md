Sub-task 170.1 successfully identified a population of "founder" rules capable of moving an asymmetric L-tromino particle, with a `max_fitness` of 0.283 and a `mean_fitness` of 0.034.

This task is to determine if this motion is an evolvable trait. You will create and evaluate a second generation (Gen-1) of rules.

Your task is to:
1.  Read the results from `archive/iter_170/results/gen_0_results.json` to identify the elite rules from the first generation. Use tournament selection with a tournament size of 3 to select parents.
2.  Create a new population of 100 rules by applying crossover (uniform crossover with p=0.5) and mutation (bit-flip with p=0.01) to the selected parents.
3.  Evaluate this new Gen-1 population using the exact same simulation setup as in 170.1 (L-tromino seed, same fitness metric).
4.  The hypothesis is that the mean fitness of Gen-1 will be at least 50% higher than the Gen-0 mean fitness of 0.034.
5.  Save the results for the new generation to `archive/iter_170/results/gen_1_results.json`.