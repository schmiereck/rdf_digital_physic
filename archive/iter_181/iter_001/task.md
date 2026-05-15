First, verify that the execution environment is stable and that the v=1c glider from iter_179 is reproducible.

1.  Load the champion rule `g10_rule_001` from `archive/iter_179/results/champion_rule.json`.
2.  Use the `src/run_iter_179_evolution.py` script as a reference for the simulation setup.
3.  Create a new script `src/run_simulation.py`.
4.  In this new script, initialize a 128x128 hexagonal grid with the 3-bit 'L-tromino' seed at a starting position (e.g., center).
5.  Run the simulation for 400 steps using the loaded rule.
6.  Verify that the glider propagates perfectly, i.e., it moves 400 cells in 400 steps with its bit count remaining at 3.
7.  Save a visualization of the trajectory to `archive/iter_181/results/reproducibility_check.gif`.
8.  Log the final displacement and bit count.

The primary goal is to confirm the environment is working before attempting new, more complex collision experiments. If this simple, known-good simulation fails, it indicates the technical issues from phase 180 persist.