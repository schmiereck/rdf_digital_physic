
Create a new script `src/evaluate_late_displacement.py` to test a new fitness metric.

**Methodology:**
1.  The script must load the rule definition for `rule_021`, which was the champion from iter_153. The rule is the 22nd rule (index 21) in the file `archive/iter_153/results/elite_rules.json`.
2.  Initialize a 150x150 CA grid with a random soup of density 0.25, using the specific seed `21` for reproducibility (this is the same seed used in iter_154 and 155).
3.  Run the CA simulation for 2000 steps.
4.  Calculate the center of mass (CoM) of all live cells at step 1200.
5.  Calculate the center of mass (CoM) of all live cells at step 2000.
6.  The new fitness score is the Euclidean distance between the CoM at step 1200 and the CoM at step 2000.
7.  The script must output this score as `late_displacement_fitness` in the final YAML metrics.
8.  Also include the CoM coordinates at t=1200 and t=2000 in the metrics for verification.
