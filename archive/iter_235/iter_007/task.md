Write and execute a Python script `src/test_bound_state_long.py`. This script must:
1. Load `ClosedLoopLatchingEngine` from `src/engine_d4_closed_loop_v2.py` and the LUT-08 glider.
2. Setup Permutation 10 (which is a 90-degree stacking rotation under the O_h group).
3. Run a long-term simulation (160 steps) of the active run (eta=2.0) and the Vacuum Control run (eta=0.0) under the baseline parameters: `alpha=2.0`, `threshold=0.045`, `gamma=0.90`, `sigma=2.5`, grid size L=32.
4. Track and print the mutual separation and total bit count of both runs at steps 0, 20, 40, 60, 80, 100, 120, 140, 160.
5. Verify if the active run remains stable and bit-conserving (exactly 8 bits) for the entire 160 steps, and keeps the gliders bound (separation remains < 4.0 cells), while the Vacuum Control run disperses completely.
6. Write the trajectory separation table and results to a text file: `archive/iter_235/results/bound_state_long_report.txt`.

Verify that the script executes successfully and output its printed results.
