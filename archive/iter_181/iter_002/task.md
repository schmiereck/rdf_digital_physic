Now that the environment is stable, conduct a head-on collision experiment between two v=1c gliders.

1.  Modify the `src/run_simulation.py` script to support multiple initial particles.
2.  Load the champion rule `g10_rule_001` from `archive/iter_179/results/champion_rule.json`.
3.  On a 128x128 grid, place two gliders on a collision course along the same row:
    *   **Glider A (moves East):** The standard L-tromino, positioned near (32, 64).
    *   **Glider B (moves West):** A 180-degree rotated version of the L-tromino. You must determine the correct shape and position for this particle to ensure it propagates correctly towards Glider A. Place it near (96, 64).
    *   Ensure there is enough initial separation for them to travel before colliding near the center.
4.  Run the simulation for 500 steps to observe the collision and its aftermath.
5.  Analyze and describe the outcome in the `experimenter_view`. Key points to observe:
    *   Is the collision elastic (gliders emerge intact), inelastic (they merge or change), or do they annihilate?
    *   Is the total bit count conserved throughout the interaction?
6.  Save a visualization of the full interaction to `archive/iter_181/results/head_on_collision.gif`.
7.  Report the initial and final bit counts as metrics.