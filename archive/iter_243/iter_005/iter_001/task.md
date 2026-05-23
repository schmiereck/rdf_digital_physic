Write and execute a Python script `src/glider_annihilation_analysis.py` to analyze glider annihilation and CPT-symmetry reconstruction.

The script must implement the following self-contained protocol:

1. Load the LUT-08 glider rule from `archive/iter_224/results/glider_00_lut08_sub03.json`.
   The file contains "particle" (list of 4 coordinates [dl, dr, dc, ch]) and "lut" (4096-entry list).

2. Implement a highly optimized, self-contained 3D LGCA engine with:
   - `SHIFTS`: the 12 FCC vectors in the order specified in `src/engine_3d.py`:
     [(0,1,0), (0,-1,0), (0,0,1), (0,0,-1), (0,1,-1), (0,-1,1), (1,1,1), (1,1,0), (1,0,1), (-1,-1,-1), (-1,-1,0), (-1,0,-1)]
   - `pack(grid)` and `unpack(packed)` functions.
   - `stream(grid, reverse=False)` and `collide(grid, lut)` functions.
     Optimization tip: since the grid has at most 8 active bits, `np.any(grid[..., i])` check can skip rolls for empty channels!
   - `sim_step(grid, lut)` defined as `stream(collide(grid, lut))`.
   - `sim_step_reverse(grid, lut)` defined as `collide(stream(grid, reverse=True), invert_lut(lut))`.

3. Compute the velocity of the original glider pA in vacuum over 80 steps to establish its velocity vector v_A.
   - Seed a single glider with `particle` coordinates at center (16, 16, 16) of a L=32 toroidal grid.
   - Simulate for 80 steps.
   - Compute centroid at step 0 and step 80 using torus-unwrapped coordinate averaging relative to the first active bit.
   - Compute `v_A = (centroid(80) - centroid(0)) / 80`. (It should be close to [0.5, 0.0, 1.0]).

4. Identify stable antiparticle candidates pB:
   - Load the 48 O_h symmetry permutations using `get_oh_permutations()` from `src/search_3d_gliders.py`.
   - For each permutation g in 0..47:
     - Rotate the original particle coordinates to get a rotated candidate `pB_cand`:
       ```python
       # Rotate using g:
       perm = perms[g]
       S = np.array(SHIFTS, dtype=float)
       S_pinv = np.linalg.pinv(S)
       S_rot = np.zeros_like(S)
       for i in range(12):
           S_rot[i] = S[perm[i]]
       M_g = S_rot.T @ S_pinv.T
       
       rotated_part = []
       for (dl, dr, dc, ch) in particle:
           pos = np.array([dl, dr, dc], dtype=float)
           pos_rot = np.round(M_g @ pos).astype(int)
           ch_rot = perm[ch]
           rotated_part.append([int(pos_rot[0]), int(pos_rot[1]), int(pos_rot[2]), int(ch_rot)])
       ```
     - Simulate `pB_cand` in vacuum for 80 steps.
     - Verify stability: total bit count must be exactly 4 at every single step of the 80 steps.
     - Compute its velocity `v_B`.
     - If stable and `v_B` is exactly `-v_A` (within 1e-5), identify it as a stable antiparticle candidate.

5. Sweep over:
   - These stable antiparticle candidates pB.
   - Relative phase in {0, 1} (where phase 1 is obtained by simulating the original glider pA for 1 step, and extracting its relative unwrapped coordinates).
   - Alignments: place the original glider at oa = (6, 16, 6) and the antiparticle at ob = (26 + dl, 16 + dr, 26 + dc) with dl, dr, dc swept in [-4, 4].
   - If glider A and glider B overlap initially (some bits are at the same cell and channel), skip this alignment.

6. For each setup, simulate for 80 steps and check for "clean annihilation" at step 80:
   - Total bit count == 8.
   - Bounding box of size 10x10x10 centered at (16, 16, 16) is completely empty of any active bits.
     (i.e., no active bits in range [11, 20] on any axis).
   - All 8 bits are isolated (pairwise Manhattan distance on torus L=32 is >= 6).

7. If a clean annihilation is found, perform the CPT-symmetry reconstruction test:
   - Apply CPT to the state at step 80 (coordinates l,r,c become (-l)%L, (-r)%L, (-c)%L on torus L=32, channel remains unchanged).
   - Simulate for 80 steps forward under the forward rule.
   - Apply CPT again.
   - Verify that it perfectly matches the initial step 0 grid (to bit-level precision).

8. Write the results to:
   - `archive/iter_243/results/annihilation_summary.json` containing the list of successful annihilation setups and their details.
   - `archive/iter_243/results/CPT_annihilation_report.md` explaining the findings and validating CPT-symmetry reconstruction.

Execute the script with `python src/glider_annihilation_analysis.py` and print its complete stdout. Ensure everything runs successfully.