1. Write a Python script `src/run_evolution_exp_220_sublight_final.py` which:
- Implements `SubLightFitness` internally (using the unwrapped CoM tracking and period detection logic we discussed, rejecting rules with zero displacement, velocity >= 0.9, or period <= 1).
- Implements the C2 rule evolution loop (same as `run_evolution_exp_220.py` but evaluates with `SubLightFitness`).
- Runs for 20 generations, population size 100.
- Saves the results to `archive/iter_220/results/champion_rule.json`, `evolution_summary.csv`, and a GIF.
2. Run this script using `python src/run_evolution_exp_220_sublight_final.py`.
3. Print the output and verify that it ran successfully. Do NOT exit early.