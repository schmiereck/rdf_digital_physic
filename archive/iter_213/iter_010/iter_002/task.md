The previous step (213.10.1) completed an evolutionary search and found a champion rule, saved in `archive/iter_213.10/results/champion_rule.json`. The initial analysis suggests this champion might be a slow drifter rather than a true glider. This task is to perform a rigorous characterization of this champion rule.

**Task:**

1.  **Create a characterization script:** Write a Python script `src/characterize_rule.py`.
2.  **Load the rule:** The script must load the JSON rule from `archive/iter_213.10/results/champion_rule.json`.
3.  **Run a long simulation:** Simulate the rule for 1000 steps starting from a minimal 3-bit seed pattern (as this seems to be what the search optimized for).
4.  **Analyze and Measure:**
    *   Track the center of mass (CoM) at each step.
    *   Calculate the net displacement and average velocity (in cells/step) over the 1000 steps.
    *   Record the bit count at each step to check for stability (growth/decay).
5.  **Visualize:** Generate a GIF of the full 1000-step simulation, saved to `archive/iter_213.10/results/long_run.gif`.
6.  **Report Metrics:** Output the final calculated velocity, total displacement, and a judgment on its stability in the final YAML block.

**Command to run:**
```bash
python src/characterize_rule.py \
  --rule_file=archive/iter_213.10/results/champion_rule.json \
  --steps=1000 \
  --output_gif=archive/iter_213.10/results/long_run.gif
```
This will provide the definitive evidence to classify the champion's behavior.