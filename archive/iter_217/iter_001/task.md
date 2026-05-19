**Goal:** Discover a stable, bit-conserving `v<c` (sub-light speed) glider using the new, validated `SubLightFitness` function.

**Strategy:** Re-run the successful 'warm-start' evolutionary strategy from `iter_215`, but replace the flawed fitness function with the new `SubLightFitness` from `iter_216.4`.

**Detailed Steps:**
1.  **Initial Population:** Start with the exact same 'warm-start' population used in `iter_215.1` (a mix of known 'active' rules and their mutants). This is critical to provide a good starting gradient for evolution.
2.  **Fitness Function:** Evaluate all individuals in the population using the new `SubLightFitness` function. This function must enforce the velocity gate (`vel < 0.9`) and the period gate (`period > 1`) to explicitly reject `v=1c` gliders and stationary oscillators.
3.  **Evolutionary Loop:** Run the evolutionary search for up to 10 generations.
4.  **Reporting:**
    *   If a `v<c` glider is found, report its rule, fitness score, average velocity, and period. Save an animation of its movement to `archive/iter_217/results/champion_vc_glider.gif`.
    *   If no `v<c` glider is found after 10 generations, analyze the fitness landscape. Report the highest-fitness individual and describe its (failed) behavior. Explain why the search may have failed.
5.  **Reference:** The code for the new fitness function is located in `src/run_iter_216_diagnostics.py` (from iter_216.4). The 'warm-start' population logic is in `src/run_iter_215_warm_start.py`.