Write and execute a python script `src/rigorous_glider_audit.py` that performs a complete and correct O_h orbit filtering and 200-step stability verification of all 163 gliders in `archive/iter_240/results/new_glider_*.json`.

Here are the strict guidelines:
1. Since `rigorous_glider_audit.py` lives in `src/`, it can import `SHIFTS`, `stream`, `collide` directly from `engine_3d` using:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.resolve()))
   from engine_3d import SHIFTS, stream, collide, pack, unpack
   from search_3d_gliders import get_oh_permutations
   ```
   Do not import `from src.engine_3d` because that will cause ModuleNotFoundError.
2. Load all 163 JSON files from `archive/iter_240/results/new_glider_*.json`.
3. Load the reference LUT-08 glider from `archive/iter_224/results/glider_00_lut08_sub03.json`.
4. Implement the 48-element O_h coordinate and channel symmetry orbit filtering. For each permutation `perm` of the 48 permutations returned by `get_oh_permutations()`:
   - S is the 12x3 matrix of `SHIFTS` (floats).
   - S_rot is S permuted by `perm` (row i of S_rot is S[perm[i]]).
   - Compute M_g = S_rot.T @ np.linalg.pinv(S).T.
   - For a particle (list of (l, r, c, ch) tuples), its transformed coordinates are `M_g @ np.array([l, r, c])` rounded to nearest integer, and its transformed channel is `perm[ch]`.
   - The transformed particle is translationally canonicalized (i.e. shifted so the lex-min coordinate is at (0, 0, 0) and sorted).
   - The canonical representative of a particle under the full 48-element O_h group is the lex-minimum sorted tuple of (l, r, c, ch) over all 48 transformations.
5. Group all 163 gliders + the reference glider into equivalence classes based on this full O_h canonical representative.
6. For each unique equivalence class:
   - Run the representative particle for 200 steps (on an L=32 grid in vacuum using `stream` and `collide` from `engine_3d` with the LUT-08 LUT loaded from `archive/iter_224/results/glider_00_lut08_sub03.json`).
   - Audit stability on EVERY single step:
     - Check bit conservation: is sum of bits == initial bits?
     - Check bounding extent: is bounding_extent <= 6?
     - If both hold for all 200 steps, mark the glider as "STABLE".
     - Calculate the exact period P (the first step t > 0 where the canonical shape of the particle matches the initial canonical shape).
     - Calculate the coordinate speed v_coord = ||cumulative_displacement|| / 200.
     - Calculate the normalized speed v/c = v_coord / sqrt(2), where c_max = sqrt(2).
7. Generate a clean, audited JSON summary at `archive/iter_240/results/audited_glider_taxonomy.json` and a detailed markdown report at `archive/iter_240/results/audited_glider_taxonomy_report.md`.
8. Print the full execution output, showing how many unique classes were found, how many are stable for 200 steps, which ones are equivalent to LUT-08, and their normalized velocities (v/c). Verify that there are no coordinate rounding errors or index out of bound issues.