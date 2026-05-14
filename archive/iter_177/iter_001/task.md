Characterize the long-term stability of the new champion rule discovered in iter_176.3.
1. Load the rule from `archive/iter_176/results/gen_5/rule_019.json`.
2. Load the initial particle seed from `archive/iter_176/results/best_particle.json`.
3. Run a simulation for 2000 steps.
4. Record the step, center-of-mass x-coordinate, center-of-mass y-coordinate, and total bit count at each step.
5. Save the results to `archive/iter_177/results/long_run_metrics.csv`.
6. Analyze the CSV to determine if the velocity is constant (linear displacement) and if the bit count is stable. Report these findings in the experimenter_view.
Success Criterion: The final bit count at step 2000 is the same as the initial bit count, and the displacement plot is visibly linear.