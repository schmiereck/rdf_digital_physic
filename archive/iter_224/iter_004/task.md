Create a script `src/simulate_time_dilation.py` that demonstrates gravitational time dilation using the CPU-throttling / local-latency analogy on our 3D Cuboctahedron CA grid.

Requirements:
1. Load a discovered stable 3D glider and its corresponding LUT from `archive/iter_224/results/glider_02_lut21_sub01.json` (the z-axis traveling glider).
2. Set up a periodic 3D simulation space of shape (32, 16, 16, 12).
3. Initialize the glider at the center of the grid, moving along the z-axis (axis 0, layer index).
4. Run two parallel simulations:
   - Control Simulation (Vacuum): No gravitational potential. Local latency at each cell is exactly 1.0.
   - Gravitational Well Simulation: Define a static "gravitational well" centered at l = 16 (in the middle of the z-axis) with a Gaussian profile along the z-axis:
     U(l, r, c) = A * exp(- (l - 16)^2 / (2 * sigma^2))
     where A = 2.0 (amplitude) and sigma = 3.0 (width).
     The local update latency (computational load) of cell (l, r, c) is defined as:
     latency(l, r, c) = 1.0 + U(l, r, c)
5. For both simulations, run for 30 steps. At each step, record:
   - The glider's center of mass coordinate along the z-axis (layer index, unwrapped to handle periodic boundaries).
   - The elapsed physical time T:
     - For Vacuum: T_vac(t) = t
     - For Gravitational Well: T_grav(t) = sum_{step=1 to t} (average latency of the cells occupied by the glider at that step)
6. Calculate and print:
   - The coordinate velocity of the glider in vacuum: v_vac = dz / dT_vac.
   - The coordinate velocity of the glider in the gravitational well: v_grav = dz / dT_grav.
   - The total delay (time dilation factor) experienced by the glider as it traverses the gravitational well.
7. Save a report of the simulation data (trajectories, latencies, and velocities) to `archive/iter_224/results/time_dilation_report.json`. Print the summary of results. Run the script to verify correctness.