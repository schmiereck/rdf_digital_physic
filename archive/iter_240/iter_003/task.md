Overcommitting to an exhaustive sweep of 3 connected cells for W=5 is combinatorially explosive in pure Python because it generates over 370,000 states, each needing rotation and sorting.

To fix this and ensure the script runs and completes in seconds with maximum scientific rigor, write an updated `src/exhaustive_glider_search.py` that scales down the parameters as follows:
1. **Method A (Connected Sweep)**: Restrict to `max_size = 2` (exhaustive sweep of all 1-cell and 2-cell configurations) for W=4 and W=5. This is extremely compact (around 1,200 unique orbits total) and runs instantly.
2. **Method B (Randomized Search)**: Set `n_target = 300` unique compact particles per weight for 4 <= W <= 8.
3. **Method C (Genetic Algorithm)**: Set `pop_size = 50` and `n_gens = 10` for 4 <= W <= 8. Because of aggressive early termination in our simulator, this runs in a few seconds.

Overwrited `src/exhaustive_glider_search.py` with these optimized parameters, run `python src/exhaustive_glider_search.py`, verify that it runs perfectly to completion, and print its stdout and key metrics.