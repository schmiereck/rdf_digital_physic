Create a new Python script src/d4_spacetime.py that:
1. Implements the 3D+1 spacetime projection on the 4D FCC (D4) lattice.
2. Definess the 24 nearest neighbors (permutations of (+-1, +-1, 0, 0)) of the origin and verifies their classification into:
   - 12 spatial neighbors (dT = 0, sum of coordinates = 0)
   - 6 future temporal neighbors (dT = 1, sum of coordinates = 2)
   - 6 past temporal neighbors (dT = -1, sum of coordinates = -2)
3. Implements the spatial projection of (x, y, z, w) onto the 3D hyperplane perpendicular to (1, 1, 1, 1):
   - X = (x - y) / sqrt(2)
   - Y = (z - w) / sqrt(2)
   - Z = (x + y - z - w) / 2
4. Verifies mathematically and numerically that:
   - The 12 spatial neighbors form a perfect 3D cuboctahedron of radius sqrt(2).
   - The 6 future-directed neighbors have a spatial displacement of exactly 1.0, defining the speed of light c = 1.0.
   - All future-directed neighbors are perfectly light-like (proper time ds^2 = dT^2 - dX^2 = 0).
5. Simulates three worldlines for 300 steps:
   - Stationary (v=0): Cycle of [D1, D2] where D1 = (1,1,0,0) and D2 = (0,0,1,1)
   - Moving Massive (v=0.5c): Cycle of [D1, D1, D3, D4] where D3 = (1,0,1,0) and D4 = (0,1,0,1)
   - Massless (v=c): Cycle of [D1]
6. Computes proper time tau and Lorentz factor gamma at each step and asserts that the experimental gamma and theoretical gamma match with perfect precision (< 1e-12 error) for the massive worldlines.
7. Saves a detailed JSON report and a formatted Markdown report to archive/iter_226/results/d4_spacetime_report.json and archive/iter_226/results/d4_spacetime_report.md.
Execute the script and confirm that it runs successfully and generates all output files.