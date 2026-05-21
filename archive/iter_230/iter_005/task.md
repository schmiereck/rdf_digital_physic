Fix the typo in `src/run_dynamic_attraction.py` and run it.
Specifically:
1. In `seed_glider`, change `(cy + cz)` to `(cy + dr)`.
2. Run `python src/run_dynamic_attraction.py`.
3. Capture the stdout of the script and write it to `archive/iter_230/results/run_output.txt`.
Verify that the output demonstrates emergent attraction and saves `attraction_summary.json` successfully.