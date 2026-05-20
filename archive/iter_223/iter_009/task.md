Create and run a python script src/simulator_3d_fcc.py to implement and validate the 3D FCC (face-centered cubic / cuboctahedron) cellular automaton simulator.
The script should:
1. Implement step_grid_fcc(grid, lut) using 3D numpy array rolling as discussed, mapping the 12 nearest spatial neighbors of the FCC lattice.
2. Initialize a grid of size 64x64x64 with a single active even cell at (32, 32, 32) (note: 32+32+32 = 96 is even).
3. Verify that after running the CA with various rules (e.g., birth if exactly 2 or 3 neighbors are active), only cells on the even-sublattice (where x+y+z is even) ever become active.
4. Verify that the 12 neighbor directions correctly represent the cuboctahedral coordinates.
5. Save a verification report to archive/iter_223/results/fcc_3d_verification.json.
6. Print a summary of the math and results of the verification.