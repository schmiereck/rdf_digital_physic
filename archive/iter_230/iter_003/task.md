Create and run a python script `src/run_dynamic_attraction.py` to simulate the multi-body glider deflection.
The script should:
1. Load the 3D glider configuration from `archive/iter_224/results/glider_00_lut08_sub03.json`. Use its `lut_seed = 8` and `particle` coordinates.
2. Initialize two simulations of size L=32:
   a. Vacuum Control: `alpha = 0.0` (or extremely high threshold, so no latching ever occurs).
   b. Dynamic Gravity: `alpha = 1.0`, `threshold = 3.0`, `exponent = 1.0`.
3. Seed both simulations with two gliders at:
   - Glider 1: centered at (16, 14, 16)
   - Glider 2: centered at (16, 18, 16)
4. Run both simulations for 80 steps.
5. At each step, track the centroids (using circular/unwrapped coordinates or coordinate averaging on the local glider window) of Glider 1 (Y in range [8, 15]) and Glider 2 (Y in range [17, 24]).
6. Measure:
   - Centroid trajectories Y1(t), Y2(t) for both runs.
   - Mutual separation distance d(t) = Y2(t) - Y1(t).
   - Net trajectory deflection for both gliders:
     Delta Y1(t) = Y1_dynamic(t) - Y1_vacuum(t)
     Delta Y2(t) = Y2_dynamic(t) - Y2_vacuum(t)
7. Save the results and a plot or summary JSON to `archive/iter_230/results/attraction_summary.json`.
8. Print a beautifully formatted table of the step-by-step trajectories, mutual distance, and trajectory deflection, verifying if emergent attraction (Y1 bending up, Y2 bending down) is observed. Ensure perfect bit conservation is maintained in both simulations.