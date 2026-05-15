The evolutionary search in 179.3 discovered a new champion rule with an exceptionally high fitness score of 56.0. This task is to visually verify that this rule produces a stable, moving glider.

**Instructions:**
1.  Load the final population from `archive/iter_179/results/final_population.json`.
2.  Identify the champion rule by re-evaluating all rules in the population with the `CheckpointFitness` metric and selecting the one with the highest score.
3.  Run a simulation with this champion rule for 500 steps.
    - Grid size: 128x128 (torus)
    - Seed: 'L-tromino'
4.  Generate an animation of the simulation. The animation should clearly show the particle's movement.
5.  Save the animation to `archive/iter_179/results/champion_glider.gif`.
6.  As a metric, calculate the net displacement of the particle between step 100 and step 500 and report it as `net_displacement`.
