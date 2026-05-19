This is a retry of failed task 219.8.

**Goal:** Render the grid state to files for later analysis.

**Background:** The previous agent failed due to a simple `code_error`. The task itself is valid.

**Instructions:**
1.  Use the cleaned rule file: `archive/iter_219/results/g4_rule_083_cleaned.json`.
2.  Run `src/run_simulation.py` for 150 steps with the standard L-tromino seed.
3.  At the end of step 150, get the final `grid` object.
4.  Save the entire 128x128 grid in two formats to the `archive/iter_219/results/` directory:
    a.  As a NumPy array file: `grid_at_150.npy`. Use `numpy.save()`.
    b.  As a PNG image file: `grid_at_150.png`. Use a library like `matplotlib` or `Pillow` to create a high-contrast image of the grid.
5.  Do not attempt to find, count, or analyze any objects. Simply run the simulation and save the final state.
6.  Add the paths to the two created files to the `artifacts` list in your result.