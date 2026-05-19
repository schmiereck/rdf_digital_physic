This is the third attempt to extract the v<c glider's structure. Agents 219.1 and 219.2 failed to complete this task correctly. **It is critical to get the initial conditions right.**

Create a Python script `src/extract_vc_glider_structure.py` that:
1.  **Load Rule:** Loads the rule from `archive/iter_218/results/champion_rule.json`.
2.  **Initialize Grid:** Creates a 256x256 numpy array for the grid.
3.  **Center the Seed:** Places the 3-bit L-tromino seed `((0,0), (1,0), (1,1))` relative to the grid center. For a 256x256 grid, the center is (128, 128). The absolute coordinates should be `(128, 128)`, `(129, 128)`, and `(129, 129)`.
4.  **Simulate:** Runs the simulation for 300 steps.
5.  **Extract & Normalize:** At step 300, finds all active cells, calculates their center of mass, and computes the relative coordinates of the 10-bit glider.
6.  **Save Structure:** Saves the list of relative coordinates to `archive/iter_219/results/vc_glider_structure.json`, overwriting the incorrect file from agent 219.2. The JSON key must be "structure".