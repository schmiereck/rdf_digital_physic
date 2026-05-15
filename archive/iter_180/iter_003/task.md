Characterize the head-on collision of two v=1c gliders using the champion rule `g10_rule_001` from `iter_179`.

**This is a retry of a task that failed due to resource limits. Be efficient.**

1.  Copy the script from `src/run_iter_179_evolution.py` to `src/run_iter_180_collision.py`.
2.  In the new script, remove all the evolutionary algorithm code (population, fitness, generations).
3.  Keep the simulation and visualization logic.
4.  Set up a 256x256 toroidal grid.
5.  Place two 3-bit L-tromino seeds on a direct collision course:
    *   Seed 1: Start at `(100, 128)`, oriented to move East.
    *   Seed 2: Start at `(155, 128)`, rotated 180 degrees to move West.
6.  Run the simulation for 100 steps.
7.  Save the resulting animation to `archive/iter_180/results/head_on_collision.gif`.
8.  Report the qualitative outcome (e.g., elastic, annihilation, fusion) and the final bit count (initial is 6).