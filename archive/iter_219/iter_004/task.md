This task has one simple goal: run the v<c glider simulation and save the final grid state.

**Create a Python script `src/run_and_save_state.py` that performs ONLY the following actions:**
1.  **Load Rule:** Loads the rule from `archive/iter_218/results/champion_rule.json`.
2.  **Initialize Grid:** Creates a 256x256 numpy array for the grid.
3.  **Center the Seed:** Places the 3-bit L-tromino seed `((0,0), (1,0), (1,1))` relative to the grid center (128, 128).
4.  **Simulate:** Runs the simulation for exactly 300 steps.
5.  **Save Final Grid:** At the end of the simulation, it saves the entire 256x256 numpy grid array to a binary file at `archive/iter_219/results/final_grid_state.npy` using `numpy.save()`.

Do not perform any analysis, extraction, or JSON creation. Just run the simulation and save the raw final grid.