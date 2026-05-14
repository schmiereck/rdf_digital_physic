The experiment for iter_159 was not performed correctly. The task was to evaluate a new random population of 100 rules, but instead only a single old rule was tested.

Your task is to correctly perform the experiment that was intended for iter_159.

**Goal:** Find a "founder" rule for a new evolutionary run, using the composite fitness metric.

**Methodology:**
1.  Create a Python script `src/main.py`.
2.  In this script, generate a **new, random population of 100 C2-symmetric rules**.
3.  For each of the 100 rules:
    a.  Initialize a 128x128 grid with a 25% random density (using `seed=42` for reproducibility).
    b.  Run the simulation for 2000 steps.
    c.  Calculate the center of mass (CoM) at t=1200 and t=2000.
    d.  Calculate the final bit count at t=2000.
    e.  Calculate the fitness score using the composite metric: `fitness = displacement(CoM_1200, CoM_2000) / (1 + final_bit_count)`.
4.  After evaluating all 100 rules, save the entire population (rules + their fitness scores) to `archive/iter_166/results/population_gen1.json`.
5.  Identify the rule with the highest fitness score.
6.  For the **top-scoring rule only**, generate a visualization of its final grid state at t=2000 and save it to `archive/iter_166/results/champion_final_grid.png`.

**Final Output:**
Your final YAML block for the `run_agent` call should report the following metrics:
- `mean_fitness`: The mean fitness of the entire 100-rule population.
- `max_fitness`: The fitness score of the top-performing rule.
- `top_rule_id`: The ID of the top-performing rule (e.g., "rule_087").
- `top_rule_displacement`: The late displacement of the top rule.
- `top_rule_final_bits`: The final bit count of the top rule.

This will properly test the hypothesis and provide a founder for the next generation if successful.