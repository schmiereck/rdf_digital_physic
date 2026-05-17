**Goal:** Characterize the collision dynamics of the champion elastic-collision rule under varying vertical offsets.

**Inputs:**
- The champion rule, which is the first rule in the list from `archive/iter_193/iter_002/results/final_population.json`.

**Steps:**
1.  Create a new script `src/characterize_offset_collisions.py`.
2.  Load the champion rule.
3.  Implement functionality to generate two-glider collision seeds where one glider is displaced vertically relative to the perfect head-on trajectory.
4.  Run simulations for 600 steps for the following vertical offsets: `y_offset = 1`, `y_offset = 2`, and `y_offset = 3`.
5.  For each simulation:
    a. Save the outcome as a GIF (e.g., `offset_1_collision.gif`) to `archive/iter_195/results/`.
    b. Analyze the collision's properties:
        i.  **Bit Conservation:** Record the initial and final bit counts.
        ii. **Outcome:** Classify the result (e.g., Elastic Scattering, Inelastic, Fusion, Chaotic).
        iii. **Scattering Angle:** If the gliders survive and separate, calculate the angle of their final velocity vectors relative to the initial horizontal axis.
6.  Generate a summary report `offset_report.json` in `archive/iter_195/results/` that details these findings for each offset value.
