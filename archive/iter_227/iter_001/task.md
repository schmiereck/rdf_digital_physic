Create a Python script `src/d4_lensing.py` that implements the D4 lattice and uses Dijkstra's pathfinding algorithm to find Fermat geodesics (minimum-coordinate-time paths) of light rays in the projected 3D+1 spacetime.

Requirements:
1. Orthonormal projection from 4D FCC (D4) lattice to 3D spatial (X, Y, Z) coordinates:
   - X = (x - y) / sqrt(2)
   - Y = (z - w) / sqrt(2)
   - Z = (x + y - z - w) / 2
   And coordinate time:
   - T = (x + y + z + w) / 2

2. The 6 future-directed light-like vectors in D4:
   - (1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1), (0, 1, 1, 0), (0, 1, 0, 1), (0, 0, 1, 1)

3. Define a static gravitational potential well U(X, Y, Z) centered at the origin (0, 0, 0):
   - U(X, Y, Z) = A_grav * exp(- (X^2 + Y^2 + Z^2) / (2 * sigma^2))
   where sigma = 4.0 is the spatial width and A_grav is the potential amplitude.
   The coordinate time cost of a transition is:
   - cost(u, v) = 1.0 + U_mean
   where U_mean is the potential at the midpoint or at the destination node v. Let's use U_mean = U(X_v, Y_v, Z_v).

4. Dijkstra's pathfinding on D4:
   - Start node: (x_A, y_A, z_A, w_A) which projects to X_A = -15.0, Y_A = b (impact parameter), Z_A = 0.0.
     Let's calculate the corresponding starting 4D integer coordinates at T = 0 using the inverse projection:
     - x = (T + Z + X*sqrt(2)) / 2
     - y = (T + Z - X*sqrt(2)) / 2
     - z = (T - Z + Y*sqrt(2)) / 2
     - w = (T - Z - Y*sqrt(2)) / 2
     Since the start position must be on the integer grid, let's round these coordinates to the nearest integers that satisfy x + y + z + w = 0 (even sum).
   - Find the shortest path to any 4D node whose projected X coordinate is >= 15.0.
   - Constrain the search to a spatial bounding box to ensure high performance:
     - X in [-18, 18]
     - Y in [b - 8, b + 8]
     - Z in [-6, 6]

5. Implement a function to calculate:
   - The total coordinate travel time T_total.
   - The 3D trajectory (list of projected coordinates).
   - The deflection angle theta (in degrees) by comparing the initial tangent vector (from the first few steps) and the final tangent vector (from the last few steps).
   - The Shapiro time delay: Delta T = T_grav - T_vac.

6. Write a basic test in `src/d4_lensing.py` that runs the pathfinder for vacuum (A_grav = 0) and gravity (A_grav = 3.0) with impact parameter b = 3.0, and prints a summary of the results (coordinates, time, deflection, delay) to verify correctness.