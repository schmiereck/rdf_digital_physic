This task is to re-run the v<c glider simulation with the **correct seed** discovered from `iter_218`. All previous runs in this phase used the wrong seed.

**Create a Python script `src/run_and_save_state_corrected.py` that:**
1.  **Load Rule:** Loads the rule from `archive/iter_218/results/champion_rule.json`.
2.  **Initialize Grid:** Creates a 256x256 numpy array for the grid.
3.  **Center the CORRECT Seed:** The seed from the discovery file is `[[0, 0], [0, 1], [1, 1]]`. Place this seed relative to the grid center (128, 128).
4.  **Simulate:** Runs the simulation for 300 steps.
5.  **Save Final Grid:** Saves the entire 256x256 grid to `archive/iter_219/results/final_grid_state_corrected.npy`.
6.  **Log Final Bit Count:** After the simulation, count the number of active cells and print it clearly to stdout. This is expected to be 10.