Using `g10_rule_001`, investigate if the 192-bit static 'ash' (from iter_181) can be perturbed by a glider collision.
1. Stage 1: Generate the 192-bit static 'ash' by simulating a head-on collision of two 3-bit gliders and letting the result stabilize.
2. Stage 2: Introduce a new, single 3-bit L-tromino glider on a trajectory to collide with the center of the stabilized ash.
3. Run the simulation for 500 steps *after* the glider-ash collision.
4. Record the initial bit count of the ash (~192 bits) and the final bit count of the entire system in the metrics.
5. Analyze the outcome: Is the ash inert? Does it get 'eaten' or destroyed? Does it catalyze a new reaction? Save an animation of the Stage 2 interaction to `archive/iter_185/results/glider_ash_interaction.gif`.