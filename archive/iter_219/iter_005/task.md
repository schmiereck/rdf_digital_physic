Agent 219.4 created the file `archive/iter_219/results/final_grid_state.npy`. Your task is to load this file, analyze its contents, and extract the object's structure. This will resolve a discrepancy from previous steps.

**Create a Python script `src/extract_from_state.py` that:**
1.  **Load Grid State:** Loads the 256x256 numpy array from `archive/iter_219/results/final_grid_state.npy` using `numpy.load()`.
2.  **Count Bits:** Counts the number of non-zero cells in the array. **Log this number clearly to stdout**, as it is a critical piece of information.
3.  **Extract & Normalize:** If the bit count is greater than 0, find the coordinates of all active cells, calculate their center of mass, and compute the relative coordinates of the object.
4.  **Save Structure:** Saves the list of relative coordinates to `archive/iter_219/results/vc_glider_structure.json`. The JSON key must be "structure".