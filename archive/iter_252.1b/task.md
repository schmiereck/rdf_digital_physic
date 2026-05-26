Create src/analyze_hex_mechanism.py that extracts the cooperative survival mechanism of the 2D hex v=0.469c glider. This is a FOCUSED script — no analysis, just compute and save.

Read src/pre_registration.md first.

The script should:

1. Load champion_rule_perfect.json from archive/iter_222/results/
2. Convert rule_dict to LUT using evolution.rule_dict_to_lut()
3. Run the full glider for 200 steps from L-tromino seed [(63,63),(64,63),(64,64)] on 128x128 grid
4. Run each of the 3 seed bits individually for 200 steps
5. Compute OR-superposition mismatches at each step
6. For EACH mismatching step t, extract the set of neighborhood states where the full glider's grid differs from the OR superposition
7. Trace the glider pattern for 200 steps and detect the period by comparing canonical shapes
8. Save ALL results to archive/iter_252/results/hex_mechanism.json as a dict with these keys:
   - glider_speed (float)
   - glider_period (int or None)
   - full_glider_bit_counts (list of int, length 201)
   - single_bit_final_bits (list of 3 ints)
   - or_mismatch_count (int, out of 201)
   - binding_lut_entries (dict): mapping from neighborhood_state_int -> (lut_input, lut_output_center_bit, description) for each state where the full glider differs from OR superposition at step 1
   - full_rule_dict (dict): the loaded rule_dict as str->str mapping
   - period_detections (list): for each candidate period p, the number of matching steps

Use these imports:
```python
import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from evolution import rule_dict_to_lut, step_grid, LTROMINO_CELLS
```

The hex CA state encoding is:
state = center*64 + E*32 + SE*16 + SW*8 + W*4 + NW*2 + NE
The LUT maps state -> center bit of output (0 or 1). So lut[state] = output center bit.

step_grid from evolution.py computes neighborhood states vectorized and applies the LUT.

For OR-superposition comparison at step t: compute np.maximum of all single-bit grids at step t, compare with full glider grid at step t.

For binding LUT entries: at the first step where mismatch occurs, find cells where full_grid != or_grid, compute their neighborhood states in the full glider, and record those LUT entries.

Keep the script under 200 lines. Run it after creating it.