Task: Build and execute 13-channel search and 12-channel control search (Steps 3, 4, and 5).

First, create `src/search_13ch.py`:
1. Use `fcc_engine_13ch.py` for the simulation.
2. Load/generate the 500 LUT variants from `src/cooperative_lut_13ch.py` (call `generate_all_lut_variants(max_variants=500, w3plus_seeds=2, verbose=False)`).
3. To fit nicely within runtime constraints, sample every 5th LUT (totaling 100 LUT variants).
4. Define exactly 30 seeds on an L=24 FCC toroidal grid:
   - 5 seeds with 2 adjacent bits including 1 rest bit (e.g., cell (12,12,12) with ch0+ch12)
   - 5 seeds with 2 adjacent bits both prop (e.g., cell (12,12,12) with ch0+ch4)
   - 5 seeds with 3 adjacent bits including rest (e.g., ch0+ch4+ch12)
   - 5 seeds with 3 adjacent bits all prop (e.g., ch0+ch4+ch7)
   - 5 seeds with 2-3 bits at non-adjacent cells (separate cells with 1-2 bits each)
   - 5 seeds with 4-5 bits in asymmetric arrangements
5. For each (LUT, seed) pair, run 300 steps.
6. Track: unwrapped center-of-mass displacement, bit count stability, bounding extent, rest channel occupancy.
7. Score each run by: displacement_norm * bit_stability (bit_stability = 1 if final_bits == initial_bits, 0 otherwise).
8. Record rest channel activity (how often ch12 is occupied vs empty).
9. Save results to `archive/iter_251/results/search_results.json`.

Second, create `src/search_12ch_control.py`:
1. Use `src/engine_3d.py` for the 12-channel simulation.
2. Generate 100 12-channel O_h-equivariant LUTs using `build_randomized_w3plus_lut(w2_cfg, seed)` from `src/non_additive_lut_v2.py` (where w2_cfg = i % 128, seed = i // 128).
3. Adapt the SAME 30 seeds to 12 channels:
   - For propagation-only seeds, keep them identical.
   - For seeds with ch12, map ch12 to an unused propagation channel at the same cell (to maintain the exact same bit counts and spatial configuration).
4. For each (LUT, seed) pair, run 300 steps.
5. Score and track similarly.
6. Save control results to `archive/iter_251/results/control_results.json`.

Execute both scripts. Ensure there are no performance bottlenecks or syntax errors. Provide a high-level summary of the run, counts of successful/non-zero score runs, and any discovered propagating structures.