The primary open question is to understand the dynamics of the champion rule discovered in iter_187.2, which appeared to produce a perfect elastic collision based on final bit/object counts. This sub-task is to visualize the head-on collision to determine its qualitative nature.

**Instructions:**
1. Load the champion rule from `archive/iter_187/results/champion_rule.json`.
2. Recreate the exact initial setup from iter_187.2: a 128x128 grid with two 3-bit L-tromino particles placed for a head-on collision.
3. Run the simulation for 400 steps.
4. Generate an animation of the full simulation and save it to `archive/iter_188/results/head_on_collision.gif`.
5. In your `experimenter_view`, describe the observed dynamics. Is it true scattering with an angle change? Do the particles pass through each other? Do they become stationary? This qualitative description is the main result.