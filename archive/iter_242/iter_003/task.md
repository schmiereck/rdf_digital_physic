Write a Python script `src/glider_collision_charge_analysis.py` to systematically explore 10 distinct collision configurations of two LUT-08 gliders on the 3D FCC grid under the native LUT-08 rule, and evaluate the conservation of chirality and sub-lattice charges across these interactions.

Keep the script under 110 lines of clean, self-contained Python.
The script should:
1. Reconstruct `BT` and `BT_inv` projection matrices.
2. Load the canonical LUT-08 glider and its LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
3. Set up 10 distinct initial configurations of two gliders launched towards each other.
   Since the glider has a known velocity vector, we can place them facing each other by rotating one of them by 180 degrees using an O_h transformation (or using known channel mappings) and offsetting their starting positions (e.g., Y and Z offsets) and initial steps (relative phase) to create a variety of collisions:
   - Head-on, off-center, and glancing collisions.
4. Run each collision simulation for 100 steps on a 32^3 grid.
5. At each step \(t\), monitor:
   - Total bit count \(N(t)\).
   - Total sub-lattice occupancy vector \(\mathbf{Q}(t) = (Q_0, Q_1, Q_2, Q_3)\).
   - Group active cells into spatial clusters using a simple BFS (Manhattan distance <= 2).
   - For each cluster: if its bit count is 4, check if it is a stable propagating glider (original or reflected) and compute its chirality.
6. Analyze the outcomes:
   - Determine if any of the 10 collisions are elastic (yielding exactly two stable gliders in the final state).
   - Compute the sum of incoming chiralities vs. outgoing chiralities.
   - Analyze if the sub-lattice occupancy vector \(\mathbf{Q}(t)\) behaves independently or is mixed during chaotic interactions.
7. Print a summary table of the 10 runs, detailing: initial offsets, collision outcome (Annihilation, Inelastic Debris, Elastic, etc.), incoming vs outgoing total bit counts, and incoming vs outgoing total chiralities.
8. Evaluate the pre-registered falsification criteria against these empirical observations.
Write and run this script, and display its output.