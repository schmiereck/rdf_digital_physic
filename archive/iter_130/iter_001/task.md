**Goal:** Breed a second generation (Gen-2) of rules from the two viable medium-density rules discovered in iter_129, and evaluate their fitness to see if the evolutionary process yields improvement.

**Inputs:**
- The two viable medium-density rules from `archive/iter_129/population_medium/`. The script must identify these two rules by loading `archive/iter_129/results/medium_density_scores.csv` and finding the rules with the highest fitness scores.
- The canonical ash pattern from `src/ash_pattern.json`.

**Breeding Process:**
1. Create a new population of 100 C2-symmetric rules with 8 kernel pairs each.
2. For each new rule, create its 8 generator pairs by randomly selecting `k` pairs from the first elite rule and `8-k` pairs from the second elite rule, where `k` is a random integer from 0 to 8. This performs a uniform crossover of the rule's generator pairs.
3. Apply a 10% mutation rate: for each of the 8 pairs in a newly created rule, there is a 10% chance it will be replaced with a new, randomly generated valid pair (where `HammingWeight(A) != HammingWeight(B)`).
4. Save the new Gen-2 population to `archive/iter_130/population/`.

**Evaluation:**
- Evaluate all 100 new rules using the established late-displacement fitness metric: simulate for 200 steps on the ash pattern and calculate fitness based on the center-of-mass displacement between step 100 and step 200, penalizing any significant change in bit count.

**Reporting:**
- Save all fitness scores for the new generation to `archive/iter_130/results/gen2_reboot_scores.csv`.
- Create the final `archive/iter_130/result.yaml` file with the following summary metrics:
  - `gen1_top_fitness`: The top fitness from the previous generation (hardcoded to 0.02771506).
  - `gen2_top_fitness`: The best fitness score achieved by any rule in the new Gen-2 population.
  - `gen2_mean_fitness`: The mean fitness of the Gen-2 population.
  - `rules_beating_gen1_top`: The number of Gen-2 rules that achieved a fitness score higher than `gen1_top_fitness`.
  - `fitness_improvement_pct`: The percentage improvement of `gen2_top_fitness` over `gen1_top_fitness`.
