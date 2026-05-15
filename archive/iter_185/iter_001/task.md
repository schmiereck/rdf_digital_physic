Using the `g10_rule_001` from `iter_179`, simulate a 'glancing' collision between two 3-bit L-tromino gliders in a 2D hexagonal grid.
1. Place two gliders on parallel East-bound trajectories.
2. Introduce a small lateral (North/South) offset of 2 cells between their starting positions, ensuring their edges will interact.
3. Set their starting positions so they will collide near the center of the grid.
4. Run the simulation for 500 steps.
5. Record the initial and final bit counts in the metrics.
6. Analyze the outcome: Do they pass through each other? Do they scatter? Do they annihilate or fuse?
7. Save an animation of the collision to `archive/iter_185/results/glancing_collision.gif`.