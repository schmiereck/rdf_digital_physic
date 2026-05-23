Write and run a script `src/test_original_stability.py` to audit all 175 newly discovered candidate gliders in their ORIGINAL, unrotated orientations under the LUT-08 rule.
The script must:
1. Load the LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Load all 175 `new_glider_*.json` files.
3. For each file, simulate the glider in its exact original, unrotated configuration on an L=32 grid for 200 steps.
4. Check if it maintains perfect bit-conservation and bounding extent <= 6 at every step.
5. Print how many of the 175 candidates are genuinely stable.
6. Group the genuinely stable candidates into unique equivalence classes under only the *valid* subgroup of O_h that preserves the LUT (i.e. those symmetries under which the LUT is invariant, or if the LUT is not fully symmetric, let's find the valid symmetries or just group them under the full O_h but simulate them in their stable orientations and report on their properties!).
7. Save the list of genuinely stable original gliders and print the summary.