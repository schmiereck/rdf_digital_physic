Please create and execute the Python script `src/d4_lensing_sweep.py`.

The script must:
1. Import from `src.d4_lensing` (or `d4_lensing` if `src` is in path):
   - `run_lensing_simulation`
   - `get_potential`
   - `project_to_3d_and_time`
   (You can append `src` to `sys.path` to ensure robust imports).

2. Perform a systematic sweep over:
   - Impact parameters b in [2.0, 4.0, 6.0]
   - Potential amplitudes A_grav in [1.0, 3.0, 5.0]
   With default sigma = 4.0.

3. For each pair of (b, A_grav):
   - Run `run_lensing_simulation(b=b, A_grav=A_grav, sigma=4.0)`.
   - Extract the vacuum and gravity travel times, 3D trajectories, and deflection angles.
   - Calculate Shapiro delay (T_grav - T_vac) and net deflection angle (theta_grav - theta_vac).

4. Save the results to a JSON report:
   `archive/iter_227/results/lensing_sweep_report.json`
   Ensure the JSON contains metadata, sweep parameters, and detailed results including:
   - b, A_grav, sigma
   - Vacuum and gravity step counts, travel times, deflection angles
   - Shapiro delay and net deflection angle
   - The X and Y coordinates of the 3D trajectories (for both vacuum and gravity) so that they are fully preserved.

5. Save a detailed Markdown report:
   `archive/iter_227/results/lensing_sweep_report.md`
   The report should contain:
   - Title and brief description of the D4 gravitational lensing simulation using Dijkstra pathfinding on Fermi geodesics.
   - A clean Markdown table summarizing the sweep results (b, A_grav, vacuum/gravity travel times, Shapiro delay, vacuum/gravity deflection angles, and net deflection angle).
   - An in-depth physical interpretation and discussion of the trends (e.g., how the delay and deflection depend on b and A_grav, and why the potential acts as a diverging lens in coordinate coordinates due to Fermat's principle of least coordinate time).

6. Generate a 2D matplotlib plot showing the paths in the X-Y plane:
   `archive/iter_227/results/d4_lensing_paths.png`
   The plot should:
   - Have subplots (e.g. a 1x3 row or similar, one subplot for each A_grav amplitude in [1.0, 3.0, 5.0]) to keep it clean and readable.
   - In each subplot, display the background gravitational potential U_grid centered at (0,0) as a colored reference shade (e.g., using contourf or imshow with a colormap like 'YlOrRd' and appropriate extent/alpha, and maybe contour lines).
   - Plot the trajectories for each impact parameter b in [2.0, 4.0, 6.0]. Use solid lines for gravity paths and dashed/dotted lines for vacuum paths. Use a consistent color for each impact parameter (e.g., b=2.0 is blue, b=4.0 is green, b=6.0 is magenta).
   - Add a red circle/marker at (0,0) to denote the center of the potential well.
   - Set proper labels, titles, grid, and legend.

7. Ensure the output directory `archive/iter_227/results/` is created (use os.makedirs) before writing any output.

8. After generating the files, execute the script and verify that all three files are non-empty and correctly formatted.

Please do not use mock data. Ensure proper execution in this Windows environment. Use robust error-handling.