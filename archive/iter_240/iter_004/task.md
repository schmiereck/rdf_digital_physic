Please write the complete, optimized code for `src/exhaustive_glider_search.py` with the following parameters:
- Method A cell shape size: `max_size = 2` (exhaustive sweep of all 1-cell and 2-cell shapes for W=4 and W=5).
- Method B target number: `n_target = 300` for 4 <= W <= 8.
- Method C GA parameters: `pop_size = 50` and `n_gens = 10` for 4 <= W <= 8.

The script must:
1. Load the LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Compute unique representative orbits under lattice rotations and translations, and compare with the KNOWN LUT-08 representative.
3. Track and evaluate candidates for stability and propagation (L=20, T=80, extent <= 6, displacement >= 4.0).
4. Run all three methods (Systematic Connected Sweep, Massive Randomized Search, and Genetic Algorithm).
5. Group all discovered gliders, deduplicate them by canonical orbit, check if any are in an O_h orbit disjoint from LUT-08 under both 4-sym and abstract 48-O_h channel permutations.
6. Save a scientific report to `archive/iter_240/results/exhaustive_search_report.md`.
7. Save JSON artifacts for any new gliders, and save a summary of the search to `archive/iter_240/results/search_summary.json`.

Please write this script to `src/exhaustive_glider_search.py` and run it using `python src/exhaustive_glider_search.py`. Verify it runs perfectly to completion in seconds and print its stdout and key metrics.