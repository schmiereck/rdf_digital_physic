# Task – iter_024

**Hypothesis:** arrowhead-glider: A hand-crafted, reversible, bit-conserving CA rule can make a 3-bit 'arrowhead' particle propagate as a stable, non-trivial glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_024/results/` (relative to the project root).

## Task

Use the simulator at `src/simulate_hex.py` but ensure it uses the **standard CA update model**, not the symmetric swap scheduler. The new state of each cell is the central bit of the rule's output for its old neighborhood.

**1. Implement a Hand-Crafted Rule:**
The rule will be a permutation of the 128 neighborhood states, designed to move a specific 3-bit particle. Most of the 128 states will map to themselves (identity). You only need to define the specific mappings to achieve the desired motion and their inverses to ensure reversibility.

**2. Define Particle and Motion:**
- The particle is a 3-bit "arrowhead" pointing East: It consists of a cell `c` and its `b4` (West) and `b5` (South-West) neighbors being '1'.
- The target motion is a one-cell translation to the East in one time step. The original 3-bit pattern should be perfectly recreated at the new location. This means the bit at `c`'s `b5` must turn OFF, and a new bit at `c`'s `b1` (East) must turn ON.

**3. Construct the Permutation Mappings (The Core Task):**
- **Identify active neighborhoods:** Determine the 7-bit neighborhood states for the four "active" cells: the one turning ON (`c`'s `b1`), the one turning OFF (`c`'s `b5`), and the two that move (`c`, `c`'s `b4`).
- **Define the permutation:** Create a rule mapping (e.g., a Python dictionary) that transforms the "before" neighborhood of each active cell into a corresponding "after" neighborhood. Crucially:
  - The mapping for the cell turning OFF must result in a center bit of '0'.
  - The mapping for the cell turning ON must result in a center bit of '1'.
  - The mappings must be bit-conserving: `hamming(input_neighborhood) == hamming(output_neighborhood)`.
  - The mappings must be reversible: if `rule[A] = B`, you must also define `rule[B] = A`.

**4. Simulation Setup:**
- Run for 50 steps on a 50x50 grid with periodic boundaries.
- Initial condition: Place a single 3-bit arrowhead particle near the center of the grid.

**5. Outputs:**
- Create `archive/iter_024/result.yaml` with the following keys:
  - `behavior_class`: `GLIDER` if successful, otherwise `DECAY`, `OSCILLATOR`, or `CHAOTIC`.
  - `is_stable`: `true` if the 3-bit pattern is preserved during motion.
  - `is_bit_conserving`: `true` if the total number of '1's on the grid remains 3.
  - `glider_velocity_hex`: A tuple `(avg_dq_per_step, avg_dr_per_step)` representing the measured velocity.


## Success Criteria

- The `behavior_class` in `result.yaml` is `GLIDER`.
- The `is_stable` flag is `true`.
- The `is_bit_conserving` flag is `true` and the final bit count is 3.
- The measured velocity is approximately (1.0, 0.0) in axial coordinates.

## Required Output

You MUST end your final response with a ```yaml``` code block in this exact schema (the orchestrator reads it to determine success):

```yaml
status: ok  # or experiment_failed or code_error
artifacts:
  - path/to/created/file  # relative to the project root
metrics:
  key: value  # any numeric results
log_excerpt: |  # last ~20 lines of relevant output
  ...
experimenter_view: |  # your qualitative observations
  ...
notes: brief technical remark
```
