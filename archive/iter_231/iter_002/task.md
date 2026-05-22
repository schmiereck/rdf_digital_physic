Create a script `src/moving_mass_deflection.py` that implements 4D time-dependent Dijkstra Fermat pathfinding over a 3D+1 spacetime lattice with a moving mass source.
The grid size should be 32x32x32 with periodic boundary conditions.
At any step t, the moving mass is centered at (16, Y(t), 16) where Y(t) = Y0 + v_y * t. Set Y0 = 10.0, v_y = 0.2.
Implement the local density smoothing and latching logic as in `moving_mass_shapiro.py` with threshold = 5.0 and latch_duration = 10.
In the 4D Dijkstra pathfinder:
- State represents (x, y, z, t) where t is the accumulated coordinate cost.
- Transitions from (x, y, z, t) are to the 6 spatial neighbors (x', y', z') with periodic wrapping in Y and Z, and x' restricted to [0, L-1].
- The time step transition is t' = t + cost, where cost = 1 + latch_duration if the neighbor (x', y', z') is in a latching region at time t, and 1 otherwise.
- To favor straight lines, add a tiny tie-breaker: cost += 1e-6 * ((y' - y_start)^2 + (z' - z_start)^2).
- Find the shortest path from start_node = (0, 16, 16, 0) to X = 31.
Run three comparative experiments:
1. Vacuum (Mass = 0) -> Deflection should be 0.
2. Static Mass at Y=16 (v_y = 0) -> Deflection should be symmetric.
3. Moving Mass starting at Y0=10 with v_y=0.2 -> Deflection should adapt to the shifting gravity well.
For each case, measure:
- Path length (excess coordinate steps)
- Maximum spatial deflection in Y and Z
- Coordinates of the path
Write the results JSON to `archive/iter_231/results/moving_mass_deflection.json` and a markdown report to `archive/iter_231/results/moving_mass_deflection_report.md`.
Run the script to verify it runs perfectly and write the terminal output to `archive/iter_231/results/deflection_output.txt`.