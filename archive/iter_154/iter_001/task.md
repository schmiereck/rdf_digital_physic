
Create a script `src/visualize_rule.py` to visualize the dynamics of the champion rule from iter_153.

**Methodology:**

1.  The script must deterministically regenerate the Gen-3 population from iter_153. The evolutionary process is seeded and should be identical:
    *   Start with the random Gen-1 population from seed=150.
    *   Evolve Gen-2 using the top 10 elites from Gen-1 and breeding_seed=152.
    *   Evolve Gen-3 using the top 10 elites from Gen-2 and breeding_seed=153.
    *   The `src/evolve.py` script should contain the logic for this process.

2.  Select the champion rule from the generated Gen-3 population. This was rule_021, which had the highest fitness.

3.  Run a simulation for 1000 steps using this rule. The simulation must start from the *exact same initial conditions* as its fitness evaluation in iter_153. The convention is that rule `i` is evaluated with `random_seed=i`. Therefore, use `random_seed=21`.

4.  Generate an animated GIF of the simulation, showing the grid state. Save snapshots to create a smooth animation.

5.  Save the final animation to `archive/iter_154/results/rule_021_dynamics.gif`.

6.  In your `experimenter_view`, describe the qualitative dynamics. Is it a glider? A puffer? Explosive growth? Be specific.
