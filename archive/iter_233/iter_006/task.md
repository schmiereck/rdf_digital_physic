Analyze the results in `archive/iter_233/results/closed_loop_attraction.json` and write a Python script `src/analyze_two_body_sweep.py` that parses the file to:
1. Find the best configuration in terms of maximum mutual deflection.
2. Verify if any config achieved mutual attraction (i.e. the separation between the gliders decreased over time compared to the vacuum run, meaning deflection > 0.0).
3. If the results look correct, write a clean plot/table of the best trajectory (centroids of Glider 1 and Glider 2, and their separation over steps) and save it.
4. Let's also check if there are other parameters we should sweep, or if the current optimal parameters are indeed the best.
Execute this script and print its full output.