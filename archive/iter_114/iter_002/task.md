Create a Python script `src/extract_glider_structure.py` to programmatically find and save the structure of the glider discovered in iter_110. **Please print progress updates to stdout after each major step (soup simulation done, object detection done, starting analysis loop, glider found).**

**1. Re-run the Discovery Simulation:**
   - Load the C2-symmetric "cooling" rule from `archive/iter_105/population/rule_023.json`.
   - Initialize a 150x150 hexagonal grid with 25% random noise, using the same random seed as iter_105 (seed=42).
   - Simulate the "primordial soup" for 1000 steps to generate the "ash" field of objects.

**2. Identify and Isolate the Glider:**
   - Use a connected-components algorithm to identify all distinct objects in the final grid state.
   - For each object, simulate it in isolation for an additional 200 steps to determine its properties (period, bit_count, displacement).
   - Identify the object that matches the known glider properties: 6 bits, period 4, and non-zero displacement. There may be multiple copies.

**3. Extract and Save the Structure:**
   - Once a glider is identified, record the relative coordinates (dq, dr) of its 6 constituent cells for each of the 4 phases of its cycle. The coordinates for each phase should be normalized by subtracting the center of mass for that phase.
   - Save this structural data to a JSON file at `archive/iter_114/results/glider_structure.json`.
   - The JSON output should be a dictionary with keys: "period", "bit_count", and "phases". The "phases" value should be a list of 4 lists, where each inner list contains the 6 coordinate tuples for that phase. Example: `{"period": 4, "bit_count": 6, "phases": [[(q,r), ...], [...], [...], [...]]}`

**4. Final Report:**
   - Create the standard `result.yaml` file in `archive/iter_114/`.
   - The YAML should report `status: ok` if the glider is found and its structure is saved.
   - Include a metric `gliders_found` with the count of gliders identified.
   - The `experimenter_view` should confirm that the `glider_structure.json` file was created and contains the four phases of the 6-bit object.