
Create a script `src/visualize_remnant.py` that analyzes the spatial distribution of objects in the stable remnant produced by `rule_011` from iter_131.

**1. Setup:**
   - Load the canonical ash pattern from `src/ash_pattern.json`.
   - Load the rule `archive/iter_131/population/rule_011.json`.
   - Initialize a 200x200 hexagonal grid with the ash pattern.

**2. Simulation and Object Identification:**
   - Simulate the grid for 200 steps to allow the remnant to form and stabilize.
   - At step 200, use a connected-components algorithm to identify all objects on the grid.

**3. Object Characterization:**
   - For each object, determine its type (still-life or oscillator period) and its bit-count. This can be done by simulating each object in isolation and hashing its state history to find its period.
   - For each object, calculate its center-of-mass (COM) coordinates.

**4. Output Generation:**
   - Create a text file at `archive/iter_134/results/remnant_map.txt`.
   - For each of the 37 objects, write a line in the format:
     `object_id, type, period, bit_count, com_q, com_r`
     - `type`: "still-life" or "oscillator"
     - `period`: 1 for still-lifes, >1 for oscillators.

**5. Analysis and Reporting:**
   - In the `experimenter_view` of your final YAML, analyze the `remnant_map.txt` file to answer the core research question: **Are the oscillators spatially clustered?**
   - Describe the overall distribution. For instance, are oscillators in the core with still-lifes on the periphery, or are they intermingled? Calculate the average distance between oscillators versus the average distance between all objects to support your conclusion.
