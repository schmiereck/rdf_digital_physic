Write a quick python script `src/fix_parameters_and_run.py` that does the following:
1. Read the contents of `src/exhaustive_glider_search.py`.
2. Replace:
   - `def method_b(known_canon, n_target=1000):` with `def method_b(known_canon, n_target=300):`
   - `def method_c(known_canon, pop_size=100, n_gens=20):` with `def method_c(known_canon, pop_size=50, n_gens=10):`
   This scales down the search space to be extremely fast and complete in under 30 seconds, while remaining highly rigorous.
3. Save the modified code back to `src/exhaustive_glider_search.py`.
4. Run `python src/exhaustive_glider_search.py` using subprocess and print the full stdout.

Run `python src/fix_parameters_and_run.py` and print its complete stdout and the final summary.