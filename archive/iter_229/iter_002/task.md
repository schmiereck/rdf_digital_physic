Run the self-tests in `src/engine_d4_latching.py` by executing it as a script to verify that it is fully correct and passes all checks. 

Then, create and run a new script `src/run_latching_lensing_sweep.py` that:
1. Conducts a systematic parameter sweep over:
   - `latch_duration`: [5, 10, 15]
   - `mass_value`: [5.0, 10.0, 15.0]
   - `threshold`: [3.0, 5.0, 7.0]
2. For each combination, measures Shapiro Delay at different impact parameters b, and runs Dijkstra Fermat pathfinding to calculate the maximum deflection (light bending) and coordinate travel time.
3. Generates a beautifully-designed Markdown report summarizing the findings.
4. Saves the results to a JSON file `archive/iter_229/results/latching_lensing_sweep.json` and the Markdown report to `archive/iter_229/results/latching_lensing_report.md`.
5. Verifies that the entire pipeline is 100% correct and error-free. Print out the results.