Conduct a collision experiment between the v=1c glider and a single stationary bit.

1.  Use the `src/run_simulation.py` script.
2.  Load the champion rule `g10_rule_001` from `archive/iter_179/results/champion_rule.json`.
3.  On a 128x128 grid, set up the initial state:
    *   **Glider:** The standard 3-bit L-tromino, positioned to start near (32, 64) and move East.
    *   **Target:** A single stationary '1' bit placed directly in the glider's path at (64, 64).
4.  Run the simulation for 500 steps.
5.  Analyze and describe the outcome. Key questions:
    *   Does the glider survive the collision?
    *   Is the target bit destroyed, or does it affect the glider?
    *   Does this interaction conserve the bit count (initial count = 4)?
    *   Does it trigger explosive growth like the head-on collision?
6.  Save a visualization to `archive/iter_181/results/glider_bit_collision.gif`.
7.  Report the initial and final bit counts as metrics.