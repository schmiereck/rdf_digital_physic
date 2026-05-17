The planner in `200.1` discovered a promising champion rule for `v<c` motion. Your task is to characterize this rule to determine if it produces a true, stable glider.

**Methodology:**

1.  **Load Rule:** Load the champion rule from `archive/iter_200/results/champion_v_lt_c_rule.json`.
2.  **Long Simulation:** Run a 2000-step simulation on a 256x256 grid using this rule and the standard 3-bit L-tromino seed.
3.  **Analysis:**
    *   Track the center-of-mass (CoM) coordinates at every step.
    *   Track the bit count at every step.
    *   Analyze the CoM trajectory to calculate the average velocity as a fraction of `c`. The velocity is the displacement over the last 1000 steps (from step 1000 to 2000) to ignore initial transients.
    *   Analyze the sequence of glider shapes (relative bit positions) to find the period of its internal oscillation. The period is the number of steps after which the shape repeats.
4.  **Output:**
    *   Create a JSON file `archive/iter_200/results/glider_properties.json`. It must contain the following keys:
        *   `velocity_vc`: The calculated average velocity (float).
        *   `period`: The detected period (integer).
        *   `is_stable`: A boolean indicating if the bit count remained perfectly constant throughout the 2000 steps.
    *   Generate a plot of the X and Y coordinates of the CoM versus time and save it to `archive/iter_200/results/trajectory.png` to visualize the motion.