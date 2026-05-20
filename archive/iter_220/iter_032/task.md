Surgically modify `src/new_fitness.py` so that the window displacements are divided by the window duration (the number of steps in each window) to compute actual velocities in cells/step instead of raw displacement proxies:
1. In `DisplacementConsistencyFitness.__call__`, inside the window loop, find the number of steps in the current window:
   `window_steps = last_entry["step"] - first_entry["step"]`
   If `window_steps > 0`, divide the displacement magnitude by `window_steps` to get the velocity of that window. If `window_steps == 0`, velocity is 0.0.
2. Use these normalized velocities for calculating `mean_velocity_magnitude` and `std_dev_velocity_magnitudes`.
3. Ensure that the velocity gate (`max_velocity_threshold`) and the core fitness formula are applied to these true step velocities.
4. Verify that this correctly normalizes fitness values and handles the division correctly. Run a syntax and import check to ensure no errors.