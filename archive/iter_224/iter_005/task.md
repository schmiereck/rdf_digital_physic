Create and run `src/simulate_time_dilation.py`.

The script must:
1. Load glider 2 from `archive/iter_224/results/glider_02_lut21_sub01.json` (the z-axis traveling glider).
2. Set up a simulation space using `src/engine_3d.py`. We can represent the space as a 3D NumPy array of shape (32, 16, 16, 12).
3. Initialize the glider in the grid at initial coordinates: l=0, r=8, c=8 (which is the center of r, c). Place the glider's active channels as defined in the json file:
   For each (dl, dr, dc, ch) in the "particle" list, set `grid[(l + dl) % 32, (r + dr) % 16, (c + dc) % 16, ch] = 1`.
4. Run the simulation for 30 steps:
   - Control Simulation (Vacuum): No gravitational potential.
   - Gravitational Well Simulation: Define a static "gravitational well" potential U along the z-axis (axis 0, layer index):
     U(l) = A * exp(- (l - 16)**2 / (2 * sigma**2))
     where A = 2.0 (amplitude) and sigma = 3.0 (width).
     Since it's a torus, let's calculate the shortest distance on a circle of size 32:
     dist_l = min(abs(l - 16), 32 - abs(l - 16))
     U(l) = A * exp(- dist_l**2 / (2 * sigma**2))
     The update latency of cell (l, r, c) is:
     latency(l) = 1.0 + U(l)
5. For each step t in 1 to 30:
   - Perform the stream and collide step on the grids.
   - For both simulations, calculate the unwrapped z-coordinate (l_unwrapped) of the center of mass.
     Since the glider travels in the negative z-direction (it goes from l=0, to 31, 30, 29, etc. because cumulative_displacement is negative, or let's verify which direction it goes and unwrap it properly. Note that if it moves in negative z, its coordinate l decreases. To unwrap it properly, we can track the change in l from step to step, and if the change crosses the boundary, e.g. from 0 to 31, we subtract 32 from the unwrapped coordinate).
   - Track proper physical time T:
     - Vacuum: T_vac = t
     - Gravitational Well: T_grav = sum_{step=1 to t} latency(int(round(l_com_grav_wrapped)))
6. Print a table comparing:
   - Step t
   - Wrapped and unwrapped coordinate l for both Vacuum and Gravity.
   - Proper physical time T_vac and T_grav.
   - The coordinate velocities of both gliders (unwrapped_l_change / step, and unwrapped_l_change / T).
7. Save a report to `archive/iter_224/results/time_dilation_report.json`.
8. Execute the script using Python and output the printed results.