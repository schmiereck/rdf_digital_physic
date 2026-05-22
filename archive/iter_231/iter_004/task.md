Create the script `src/moving_mass_deflection.py` that implements 4D time-dependent Dijkstra Fermat pathfinding over a 3D+1 D4 spacetime lattice with a moving mass source.
The script should:
1. Implement the projection and inverse projection functions for the D4 lattice (identical to `src/d4_lensing.py`).
2. Implement a dynamic gravitational potential well centered at `(0, Y_mass(t), 0)` where `Y_mass(t) = Y0 + v_y * t`. Solve the implicit arrival time equation `t_v = curr_cost + 1.0 + U_v(t_v)` using fixed-point iteration.
3. Run a sweep of impact parameters `b` from -4.0 to +4.0 in steps of 1.0. For each `b`, find the shortest Fermat path for both vacuum (A_grav=0.0) and strong gravity (A_grav=5.0, v_y=0.2, Y0=0.0, sigma=4.0).
4. Compute the travel times, Shapiro delay, and deflection angles, then write a complete report to `archive/iter_231/results/moving_mass_deflection_report.md` and a JSON file to `archive/iter_231/results/moving_mass_deflection.json`.
5. Execute the script and verify that it completes successfully without errors.