Create a new Python script `src/explore_two_body_attraction_v2.py` that implements a refined and extended Two-Body Cavendish parameter sweep.
The script must:
1. Load the stable 4-bit glider (LUT-08) from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Configure a toroidal grid with size L=32, steps=160.
3. Seed two gliders separated by 5 cells in Y (e.g., CY1 = 13, CY2 = 18, and CX = 16, CZ = 16).
4. Perform a systematic grid sweep over the following parameter space:
   - alpha: [1.5, 2.0, 2.5, 3.0, 3.5]
   - threshold: [0.3, 0.5, 0.7, 0.9]
   - gamma: [0.01, 0.02, 0.03, 0.05, 0.08]
   - kappa: [0.05, 0.08, 0.12, 0.16]
   - eta: [1.0, 1.5, 2.0, 2.5, 3.0]
   Total combinations = 2000.
5. In each simulation run, verify exact bit conservation (always 8 total bits) and correct glider partition (4 bits per glider). If stable, calculate the mutual deflection at step 160 (deflection = 5.0 - final_separation).
6. Find the best parameter set that maximizes mutual deflection at step 160.
7. Run a long-term validation on this best parameter set for 240 steps and check if the attraction persists and increases over time (e.g. comparing step 160 separation vs step 240 separation).
8. Save all results to `archive/iter_233/results/closed_loop_attraction_v2.json`, and print a beautiful summary table showing the centroids, separations, and deflections over time for the best config (and comparing it against the vacuum eta=0.0 baseline).
Run this script and print the entire stdout.