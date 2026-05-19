
Create a new script `src/run_iter_217_sublight_search.py` that combines the warm-start population generation from `src/run_iter_215_warm_start.py` with the validated `SubLightFitness` function from `src/run_iter_216_diagnostics.py`.

The script should:
1.  Initialize the population using the same mix of 'active' rules and mutants as `iter_215`.
2.  Use the `SubLightFitness` function, ensuring the velocity gate (`vel < 0.9`) and period gate (`period > 1`) are strictly enforced.
3.  Run an evolutionary search for a maximum of 10 generations.
4.  If a `v<c` glider is found (fitness > 0), halt the search and save the following to `archive/iter_217/results/`:
    - `champion.json`: The rule and its fitness details.
    - `champion_vc_glider.gif`: An animation of the glider.
5.  If no glider is found after 10 generations, save the best-performing non-glider rule to `archive/iter_217/results/best_failure.json`.
6.  The script must output a final YAML block with the experiment's results.
