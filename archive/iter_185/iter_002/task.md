Using `g10_rule_001`, simulate a head-on collision between the original 3-bit L-tromino glider and the 5-bit composite glider (discovered in iter_181).
1. The 5-bit glider's structure was formed from a 3-bit glider fusing with a stationary bit. You must first identify and re-create this 5-bit particle.
2. Place the 3-bit glider (moving East) and the 5-bit glider (moving West) on a direct collision course in the center of a 128x128 grid.
3. Run the simulation for 500 steps, which should be sufficient to observe the collision and its aftermath.
4. Record the initial (3 + 5 = 8 bits) and final bit counts in the metrics.
5. Analyze the outcome (e.g., annihilation, fusion, elastic scatter, complex debris) and save an animation to `archive/iter_185/results/asymmetric_collision.gif`.