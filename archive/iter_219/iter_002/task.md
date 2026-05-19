Agent 219.1 confirmed the v<c glider is stable. This task is to programmatically extract its structure.

Create a new Python script `src/extract_vc_glider_structure.py` that re-uses the simulation logic from 219.1.

**Script Requirements:**
1.  **Load Rule:** Load the rule from `archive/iter_218/results/champion_rule.json`.
2.  **Initialize Grid:** Use a 256x256 hexagonal grid with the standard 3-bit L-tromino seed.
3.  **Simulate:** Run the simulation for exactly 300 steps to get the glider into a stable state.
4.  **Extract Coordinates:** At the final step (300), get the coordinates of all active cells (`np.where(grid > 0)`).
5.  **Normalize Coordinates:** Calculate the center of mass of the active cells. Subtract the center of mass from each coordinate to get a list of relative coordinate pairs.
6.  **Save Structure:** Save the list of relative coordinates to a JSON file at `archive/iter_219/results/vc_glider_structure.json`. The JSON should contain a single key "structure" with the list of `[row, col]` pairs.