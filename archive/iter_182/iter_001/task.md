Isolate and characterize the 5-bit composite glider discovered in iter_181.3.

1.  **Load the Particle:** Load the final state from `archive/iter_181/results/glider_bit_collision_end.npy`. This file contains the 5-bit composite glider.
2.  **Setup:** Create a new, clean 256x256 hexagonal grid. Isolate the 5-bit particle from the loaded state (remove any other debris if present) and place it in the center of the new grid.
3.  **Simulate:** Run the simulation for 800 steps using the known glider rule (`g10_rule_001` from iter_179).
4.  **Analyze & Report:**
    - Measure the center of mass displacement and bit count at intervals of 100 steps.
    - Determine the particle's final velocity (cells/step) and its stability (is the bit count constant?).
    - Save the results to a CSV file: `archive/iter_182/results/composite_glider_properties.csv`.
    - Generate an animation of the simulation: `archive/iter_182/results/composite_glider.gif`.
5.  **Goal:** Determine if the 5-bit composite particle is a stable glider with a constant velocity.