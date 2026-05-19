**Goal:** Extract the v<c glider structure. This is a re-attempt of a previously failed task (219.3), but with new information.

**Diagnosis:** The core simulator is fine (per 219.6), but the analysis code probably hung the last agent. Your task is to extract the glider structure using a simpler, more robust method.

**Instructions:**
1.  Use the cleaned rule file: `archive/iter_219/results/g4_rule_083_cleaned.json`.
2.  Run `src/run_simulation.py` for 150 steps with the standard L-tromino seed.
3.  At step 150, get the grid state.
4.  **Use a simple extraction logic:** Instead of complex motion tracking, find all contiguous objects on the grid. Assume the **largest** object by bit count is the glider. Discard all smaller objects as debris.
5.  Take the coordinates of this largest object and normalize them (so the top-left-most bit is at `[0,0]`).
6.  Save the normalized coordinates to `archive/iter_219/results/vc_glider_g4_rule_083_structure.json`.
7.  Report the `glider_bit_count` metric (the number of bits in the final structure).
8.  Report the `debris_object_count` metric (the number of other, smaller objects you discarded).