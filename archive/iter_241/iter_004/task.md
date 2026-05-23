Write and execute a streamlined, highly optimized Python script `src/fcc_glider_search.py` that implements the entire Phase 7.1 Glider Taxonomy search and O_h orbit checking.

Key requirements:
1. Create `src/fcc_glider_search.py` to run Phase 7.1 Glider Taxonomy.
2. Load the reference glider `LUT-08` from `archive/iter_224/results/glider_00_lut08_sub03.json`.
3. Build the O_h coordinate and channel transforms exactly as verified in `src/rigorous_glider_audit.py` (using `build_oh_transforms` with matrix B mapping).
4. Simulate `LUT-08` for 40 steps, extract its active bit set (unwrapped and translated so that the lexicographical minimum is at (0, 0, 0)) at each step, and rotate each of these 40 shapes under all 48 O_h symmetries. Store all unique resulting shapes in a set `LUT08_ORBIT_SHAPES` to represent the reference glider's full orbit (across all phases and rotations).
5. Search for stable, propagating gliders:
   - Method A: Systematic connected sweep for W in {4, 5} on 1 and 2 cells.
   - Method B: Randomized compact search for W in {4..8} (100 unique compact contiguous random particles per W).
   - Method C: Genetic Algorithm for W in {4..8} (population 40, 6 generations).
6. For any stable propagating glider found (displacement >= 4.0 over 80 steps):
   - Translate it to be canonical, and check if its canonical shape is in `LUT08_ORBIT_SHAPES`. If yes, classify it as `LUT-08` and discard.
   - If no, run an extended stability verification up to 1000 steps (no bit count change, and max_extent <= 6 on every step).
   - If it survives 1000 steps, check if its velocity is strictly sub-light (v_coord < sqrt(2)).
   - Verify O_h covariance: rotate the glider seed under a selected O_h rotation (e.g. g=10 or g=21) and verify that it propagates in the rotated direction with identical stability and speed.
7. Save the summary to `archive/iter_241/results/search_summary.json` and write `archive/iter_241/results/exhaustive_search_report.md` detailing the methods, candidates, and results.
8. If no new gliders are found, document this robust null result using the disciplined scientific language mandated by the Research Manager (e.g. "is consistent with the unique isolation of the LUT-08 glider within the scanned configuration space").

Write the script, execute it, verify it runs error-free, and save the artifacts in `archive/iter_241/results/`.