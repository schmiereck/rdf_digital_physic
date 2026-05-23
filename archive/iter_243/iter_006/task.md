Write and run a Python script `src/test_antiparticle_direct.py` that:
1. Loads the LUT and the original particle pA from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Computes the Cartesian coordinates of the 4 bits of pA using `make_BT()` and `BT_inv`.
3. Tests the following coordinate transformations:
   - Spatial inversion: cart -> -cart.
   - y-axis 180-deg rotation: cart -> [-cart[0], cart[1], -cart[2]].
   - x-axis 180-deg rotation: cart -> [cart[0], -cart[1], -cart[2]].
   - z-axis 180-deg rotation: cart -> [-cart[0], -cart[1], cart[2]].
4. For each transformation:
   - Map the Cartesian positions back to grid coordinates.
   - For the channels, map the original channel velocity vector V_cart under the transformation, and find the closest channel in the FCC neighborhood.
   - Verify if this new rotated particle is stable in vacuum over 80 steps.
   - Compute its velocity v_B over 80 steps.
   - If v_B is exactly -v_A, print the candidate.
Run this script and output the results.