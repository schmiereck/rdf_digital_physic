Create a 3D Cuboctahedron (FCC lattice) Lattice Gas Cellular Automaton (LGCA) simulation engine in `src/engine_3d.py`.
The engine must implement:
1. A 3D toroidal grid of shape `(L, H, W, 12)` representing the 12 velocity channels of the FCC lattice.
2. The 12 directions defined in the standard projection of FCC onto a stack of hexagonal layers:
   - Directions 0-5 are in-plane hexagonal directions.
   - Directions 6-8 point to layer l+1.
   - Directions 9-11 point to layer l-1.
   Use the precise coordinate shifts (dl, dr, dc) derived in our coordinate projection:
   - Channel 0: dl=0, dr=1, dc=0
   - Channel 1: dl=0, dr=-1, dc=0
   - Channel 2: dl=0, dr=0, dc=1
   - Channel 3: dl=0, dr=0, dc=-1
   - Channel 4: dl=0, dr=1, dc=-1
   - Channel 5: dl=0, dr=-1, dc=1
   - Channel 6: dl=1, dr=1, dc=1
   - Channel 7: dl=1, dr=1, dc=0
   - Channel 8: dl=1, dr=0, dc=1
   - Channel 9: dl=-1, dr=-1, dc=-1
   - Channel 10: dl=-1, dr=-1, dc=0
   - Channel 11: dl=-1, dr=0, dc=-1
3. A `stream` function that propagates the bits along their respective directions using `np.roll`.
4. A `collide` function that applies a 12-bit lookup table (LUT) of size 4096 to pack the bits, apply the LUT, and unpack them.
5. Verification functions to test:
   - Reversibility: verify that the stream and collide steps can be reversed.
   - Bit conservation: verify that any step preserves the exact total number of set bits.
6. A test script in `src/test_engine_3d.py` that runs these verifications and prints the result. Run the test script to verify correctness.