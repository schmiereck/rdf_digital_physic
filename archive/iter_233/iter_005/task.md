Create a Python script `src/analyze_sweep.py` that parses `archive/iter_233/results/closed_loop_attraction.json`. It must find:
1. The total number of configurations in `"all_results"`.
2. The number of configurations that are `"stable"` (i.e. stable == true).
3. The maximum `"mutual_attraction"` value achieved among all configurations.
4. The configurations (parameters and results) that achieved the maximum `"mutual_attraction"`.
5. How many configurations have `"mutual_attraction"` > 0.0, and what their parameters are.
Run this script and print the summary. Write the summary to `archive/iter_233/results/sweep_analysis.txt` too.