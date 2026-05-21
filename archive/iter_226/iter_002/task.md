Create a python script src/plot_d4_trajectories.py that:
1. Loads the simulation data from archive/iter_226/results/d4_spacetime_report.json.
2. Extracts the 3D spatial coordinates (X, Y, Z) for the first 50 steps of the three worldlines: Stationary, Moving Massive, and Massless.
3. Generates a 3D line plot using matplotlib (3D projection) showing the three trajectories. Label each trajectory with its velocity (e.g., v=0, v=0.5c, v=c) and draw markers on the points to highlight the discrete lattice steps (making the Zitterbewegung zig-zag path of Stationary and Moving Massive paths clearly visible).
4. Configures clean axis labels, titles, and a legend.
5. Saves the generated figure as archive/iter_226/results/d4_trajectories.png.
6. Runs the script and makes sure d4_trajectories.png is created.
7. Return a simple message confirm success.