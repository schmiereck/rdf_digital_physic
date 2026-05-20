[CACHE_BUST_987123984576]
Create and run a python script `src/run_evolution_exp_220_sublight_final.py` which:
- Implements `SubLightFitness` internally (unwrapped CoM tracking, period detection, rejects rules with zero displacement, velocity >= 0.9, or period <= 1).
- Implements the C2 rule evolution loop (same as `run_evolution_exp_220.py` but evaluates with `SubLightFitness`).
- Runs for 20 generations, population size 100.
- Saves the results to `archive/iter_220/results/champion_rule.json`, `evolution_summary.csv`, and a GIF.
Run the script using `python src/run_evolution_exp_220_sublight_final.py`.
Output the evolution progress log and final results of the search.