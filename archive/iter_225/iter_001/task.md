Write a Python script `src/fcc_spacetime.py` that:
1. Implements the 2D+1 FCC spacetime projection along the (1,1,1) axis.
2. Mathematically defines the 12 nearest neighbors of the FCC lattice.
3. Computes the spatial coordinates (X, Y) and discrete time T = (x+y+z)/2 for each neighbor.
4. Verifies that the 6 neighbors with dT = 0 form a regular hexagon in the spatial plane (side length = sqrt(2)), and the 3 neighbors with dT = 1 form an equilateral triangle (side length = sqrt(2), distance from origin = sqrt(2/3)).
5. Establishes the speed of light as c = sqrt(2/3).
6. Simulates three distinct physical worldlines:
   - Stationary worldline (v = 0): cycling through the 3 future directions sequentially (1 -> 2 -> 3).
   - Moving massive worldline (v = 0.5c): cycling through 2 of the future directions (1 -> 2).
   - Massless worldline (v = c): always taking the same future direction (1 -> 1).
7. For each worldline, simulates N steps, tracks coordinate time T, spatial coordinates (X, Y), physical velocity v, proper time tau using the discrete Minkowski metric ds^2 = dT^2 - dX^2 / c^2, and the experimental gamma factor.
8. Verifies that the experimental gamma factor matches the continuous relativistic formula gamma = 1 / sqrt(1 - v^2/c^2) with perfect accuracy.
9. Saves a comprehensive markdown report and a JSON data file to `archive/iter_225/results/fcc_spacetime_report.json` and `archive/iter_225/results/fcc_spacetime_report.md`.