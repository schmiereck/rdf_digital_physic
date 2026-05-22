Write and execute a Python script `src/test_oh_covariance.py`. This script must:
1. Load the LUT-08 glider config from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Generate the 48 permutations `perms` and compute the 3x3 matrices `M_g` for all 48 permutations using the pseudo-inverse method verified in `src/check_oh_transform.py`.
3. Select 5 distinct permutations representing different spatial orientations (e.g., g=0 (identity), g=5, g=10, g=21, g=29).
4. For each selected permutation g:
   - Rotate the two gliders' relative positions and velocity channels. For g=0, they are at (16, 13, 16) and (16, 18, 16). For other g, their initial centroids should be rotated using `M_g` and rounded to integers, and their channels mapped using `perms[g]`.
   - Run a 160-step simulation using `ClosedLoopLatchingEngine` from `src/engine_d4_closed_loop_v2.py` with the baseline parameters: `alpha=2.0`, `threshold=0.045`, `gamma=0.90`, `eta=2.0`, `sigma=2.5`, grid size L=32.
   - Run a corresponding Vacuum Control run with `eta=0.0`.
   - Track their mutual separation over time.
   - Verify if bit conservation is perfectly preserved (exactly 8 bits) and if the gliders remain stable.
   - Compute the net mutual deflection at step 160 (initial separation minus final separation).
5. Output the results of all 5 runs (active vs vacuum control, final bit conservation, and mutual deflection) to a summary report at `archive/iter_235/results/oh_covariance_report.txt`.

Verify that the script executes successfully and output its printed results.
