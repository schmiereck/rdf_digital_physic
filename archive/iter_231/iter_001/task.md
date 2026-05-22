Create a script `src/moving_mass_shapiro.py` that implements a 3D+1 D4 Spacetime LGCA with a moving mass packet.
The grid size should be 32x32x32 with periodic boundary conditions.
The mass center should move as Y(t) = Y0 + v_y * t (e.g., Y0 = 10, v_y = 0.2, and Z = 16, X = 16).
The mass is a localized density packet with value 10.0 at the center, and 5.0 at its 6 nearest neighbors.
The local density is computed by summing the bits (temporal + latched) and the moving mass, then smoothing over the 6 nearest neighbors as in `engine_d4_latching.py`.
If local density >= threshold (e.g., threshold = 5.0), a latching delay of latch_duration (e.g., 10 steps) is applied.
Run experiments launching a single temporal bit (light pulse) in channel 4 (propagating along +X direction, shift is (1,0,0)) from X=0, Y=16, Z=16 at different launch times t_launch from 0 to 30.
Measure the travel time of the light pulse to reach X=31.
Show that the coordinate delay (Shapiro delay) peaks when the mass is in perfect synchronization with the light pulse's arrival at X=16.
Write the results table and physical analysis to `archive/iter_231/results/moving_mass_shapiro.json` and a markdown report `archive/iter_231/results/moving_mass_shapiro_report.md`.
Verify bit-conservation of the temporal and latched bits in the presence of the moving mass.
Run the script to verify it works perfectly and passes all assertions.