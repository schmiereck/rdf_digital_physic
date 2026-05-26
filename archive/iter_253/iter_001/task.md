Build a complete 3D synchronous Cellular Automaton engine on the Face-Centered Cubic (FCC) lattice. Write to src/synchronous_ca_fcc.py. This is Step 1 of the pre-registered experiment in src/pre_registration.md — read it first.

## Architecture

### FCC Lattice
- The FCC lattice has 12 nearest neighbors per site (the cuboctahedron vertices).
- In the coordinate system from engine_3d.py, the 12 neighbor offsets are:
  (±1,±1,0), (±1,0,±1), (0,±1,±1) — these are the 6 face-center pairs.
- Specifically, the 12 offsets (dl, dr, dc) are:
  (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
  (0, 1, -1), (0, -1, 1), (1, 1, 1), (1, 1, 0),
  (1, 0, 1), (-1, -1, -1), (-1, -1, 0), (-1, 0, -1)
  (Use SHIFTS from src/engine_3d.py as reference — they are the same offsets.)
- Grid: 3D numpy array of shape (L, L, L) with dtype uint8 (0 or 1 per cell).
- Toroidal (periodic) boundaries via np.roll.

### Totalistic B/S Rule (Life-like on FCC)
- The rule is defined by two sets: B (birth) and S (survival), each a subset of {0, 1, ..., 12}.
- Update rule: new_cell = 1 if (cell==0 and neighbor_count in B) or (cell==1 and neighbor_count in S), else 0.
- neighbor_count = number of live neighbors among the 12 cuboctahedron neighbors.
- This is O_h-equivariant BY CONSTRUCTION because the rule depends only on the count, not on which specific neighbors are alive.
- Represent a rule as (B_set, S_set) where both are frozensets of ints.

### Core Functions to Implement

1. `fcc_neighbor_offsets() -> list[tuple]` — returns the 12 neighbor offsets
2. `step_ca(grid: ndarray, B: set, S: set) -> ndarray` — one synchronous update step:
   - Compute neighbor_count at each cell using np.roll for each of 12 offsets, summing.
   - Apply B/S rule: new = where((grid==0) & (count in B), 1, where((grid==1) & (count in S), 1, 0))
   - Use vectorized numpy operations for speed.
3. `simulate(grid, B, S, steps) -> dict` — run simulation, return history of:
   - bit_count at each step
   - unwrapped center-of-mass (3D, using trigonometric unwrapping on torus)
   - bounding_box_size (max extent in any dimension, accounting for toroidal wrapping)
   - survival time (first step where bit_count == 0, or max steps)
   - net_displacement (from unwrapped COM)
   - grid snapshots at intervals
4. `trig_com(grid, L) -> tuple[float,float,float]` — compute center-of-mass on torus using trigonometric method (like com_bits in experiment_248_axis_aligned_search.py)
5. `unwrap_com(prev, raw, L) -> tuple[float,float,float]` — unwrap COM to avoid toroidal jumps
6. `bounding_extent(grid, L) -> int` — compute bounding box size (max over all dimensions of wrapped extent, using the minimum-wrapping approach)
7. `format_rule(B, S) -> str` — format as "B{...}/S{...}" string
8. `lambda_param(B, S) -> float` — compute Langton's lambda for the 13-neighbor system

### Positive Control Validation
After building the engine, run a validation function `validate_engine()` that:
1. **All-die rule** (B={}, S={}): Single bit at center → should die in 1 step. Assert bit_count==0 after step 1.
2. **All-live rule** (B={0,...,12}, S={0,...,12}): Single bit → should expand. Assert bit_count > 1 after step 1.
3. **Still-life rule** (B={}, S={12}): Single bit → should die (neighbor_count=0, not in S). 13-bit full block → should survive (neighbor_count=12, in S). Test both.
4. **Cooperative survival rule** (B={3}, S={2,3}): With S not containing 0 or 1, isolated bits should die. Test with 1 bit → should die. Test with 3 adjacent bits → should see non-trivial dynamics.

Print PASS/FAIL for each validation.

### Performance Target
The engine must be able to simulate a 40×40×40 grid for 500 steps in under 2 minutes on CPU. Use vectorized numpy throughout — no Python loops over cells.

### Important Constraints
- NO floating point in the CA rule itself. The B/S rule operates purely on integer neighbor counts.
- Floating point is allowed only for COM tracking and diagnostics.
- Grid cells are strictly 0 or 1 (uint8).

Write the complete file to src/synchronous_ca_fcc.py. Run the validation and report results.