Design and execute the 3D physical Cavendish unit test to observe emergent gravitational attraction of a sub-light-speed glider on a physical cellular automaton grid.

Write a python script `src/run_cavendish_test.py` that does the following:
1. Load the 3D glider configuration from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Configure a 32x32x32 toroidal grid simulation using `DynamicLatchingEngine` from `src/engine_d4_dynamic.py`.
3. Test two configurations:
   - Vacuum Control: `alpha = 0.0`, `threshold = 100.0`.
   - Gravity: `alpha = 3.0`, `threshold = 2.5`, `exponent = 1.0`.
     Place a permanent heavy mass at the center `(16, 16, 16)`. To give the gravity field an extended range, initialize the engine's `permanent_mass` as a Gaussian potential:
     `permanent_mass[x, y, z] = mass_value * exp(-((x-16)**2 + (y-16)**2 + (z-16)**2) / (2 * sigma**2))`
     Test `mass_value = 25.0`, `sigma = 2.5`.
4. Run simulations for 80 steps, launching a single glider from `cx = 0`, `cz = 16` and test two starting Y positions:
   - Case A: `y_start = 12` (below the mass). If attracted, the glider's Y centroid should deflect UPWARDS (`Y_dyn > Y_vac`).
   - Case B: `y_start = 20` (above the mass). If attracted, the glider's Y centroid should deflect DOWNWARDS (`Y_dyn < Y_vac`).
5. At each step, measure the glider's Y centroid:
   `active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)`
   `Y_centroid = mean(y coordinates of active cells)` (using unwrapped circular coordinate averaging or direct mean since the glider is the only object on the grid).
6. Verify that perfect bit conservation is maintained at every single step!
7. Perform a systematic sweep over `mass_value` (e.g. 15.0, 25.0, 35.0) and `y_start` (12, 20) to find the parameter region where:
   - The glider is structurally stable and does not break up.
   - Significant lateral deflection in Y is observed.
8. Save a comprehensive summary JSON to `archive/iter_232/results/cavendish_summary.json` containing the parameters, trajectories, deflections, and bit-conservation logs.
9. Print a beautifully formatted table of the trajectories and print a clear success/failure statement based on whether the glider was attracted towards the mass.