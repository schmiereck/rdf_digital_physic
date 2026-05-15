Characterize the head-on collision of two v=1c gliders using the champion rule `g10_rule_001` from `iter_179`.
1. Create a new script `src/run_iter_180_collision.py` based on the visualization code from `iter_179`.
2. Set up a 256x256 toroidal grid.
3. Place two 3-bit L-tromino seeds on a direct collision course:
   - Seed 1: Start at `(100, 128)`, oriented to move East (velocity `(1, 0)`).
   - Seed 2: Start at `(155, 128)`, rotated 180 degrees to move West (velocity `(-1, 0)`).
4. Run the simulation for 100 steps to observe the collision and its aftermath.
5. Save the result as a GIF animation to `archive/iter_180/results/head_on_collision.gif`.
6. Report the qualitative outcome (e.g., elastic, annihilation, fusion, chaos) and the final bit count compared to the initial bit count (6).