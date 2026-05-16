Use the validated `MarginalDynamicCollisionFitness` function to run a new evolutionary search for rules that produce genuine, dynamic, two-body collisions.

**Instructions for the Planner:**

1.  Create a new script `src/run_iter_189_evolution.py`.
2.  Integrate the `MarginalDynamicCollisionFitness` function from `src/run_iter_189_fitness_validation.py`.
3.  Set up an evolutionary search starting with a new random population of 100 rules.
4.  Use the standard 2D Hex configuration: 128x128 torus, two 3-bit L-tromino particles as the seed.
5.  Set the simulation steps to 400, with the midpoint check at step 200.
6.  Use a fitness margin of `1.0` for the `MarginalDynamicCollisionFitness` function.
7.  Run the evolution for up to 10 generations. The goal is to find a rule with a fitness of `1.0`.
8.  If a champion rule is found (fitness == 1.0), stop the evolution, save the rule to `archive/iter_189/results/champion_rule.json`, and generate a visualization of its collision dynamics as `archive/iter_189/results/collision.gif`.
9.  The final report should include the number of generations required, the fitness of the champion, and a description of the observed collision behavior. If no champion is found, report the best fitness achieved.