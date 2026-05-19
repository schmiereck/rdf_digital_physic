The goal is to programmatically extract the structure of the v<c glider discovered in iter_218. The champion rule is stored in `archive/iter_218/results/champion_rule.json`.

Create a Python script `src/extract_vc_glider_structure.py` that:
1. Loads the rule from `archive/iter_218/results/champion_rule.json`.
2. Initializes a 256x256 hexagonal grid with the standard 3-bit L-tromino seed at the center.
3. Runs the simulation for 300 steps.
4. Implements a clustering algorithm (e.g., DBSCAN or a simple flood-fill) to identify the main moving object's coordinates at step 299.
5. Normalizes these coordinates relative to the object's center of mass.
6. Saves the list of relative coordinates as a JSON file to `archive/iter_219/results/vc_glider_structure.json`.