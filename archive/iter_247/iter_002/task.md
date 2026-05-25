## Task: Phase 7.4 — Pair Production Experiment (Corrected)

### CRITICAL CORRECTIONS FROM 247.1
The LUT-08 glider is **4-bit** (not 8-bit), with period 2 and grid velocity ≈ [0.5, 0.0, 1.0].
Same-chirality partner is found via `find_pC()` in `src/phase7_3_cpt_experiment.py`, NOT via `reflect()`.
The O_h orbit matching must compare against 4-bit clusters.

### Step 0: Update Pre-Registration
Update `src/pre_registration.md` to include:
1. **O_h-Equivalence Filter**: Any 4-bit propagating cluster whose velocity matches any of the 48 O_h-rotated LUT-08 velocities (within 0.3 cells/tick) AND whose period is 2 (±1 step) is classified as "LUT-08_scattered", NOT a new species.
2. **300-Step Vacuum Isolation Test**: Any candidate not matching LUT-08's orbit must survive 300 steps alone on a clean L=64 grid with constant bit count, stable velocity, and maintained periodicity.
3. Pre-registration compliance clause.

### Step 1: Write `src/experiment_247_pair_production.py`

This script must be ≤ 220 lines. Use ONLY existing infrastructure:
- `src/engine_3d.py` for `stream`, `collide`
- `src/glider_charge_analysis.py` for `make_BT`, `reflect`
- `src/rigorous_glider_audit.py` for `build_oh_transforms`, `seed_grid`, `compute_com_circular`, `grid_cells`, `is_translate`
- `src/phase7_3_cpt_experiment.py` pattern for `find_pC` (copy the logic)

**Protocol:**

A) **Load LUT-08 and find same-chirality partner pC**
- Load from `archive/iter_224/results/glider_00_lut08_sub03.json`
- Use `find_pC()` logic from iter_245: find the O_h rotation of pA that has the same chirality (velocity direction opposite, so head-on collision works)
- Confirm pC is stable solo for 80 steps

B) **Measure exact LUT-08 velocity**
- Run single LUT-08 for 80 steps, compute average velocity per step using compute_com_circular

C) **Generate O_h orbit velocities**
- Apply all 48 O_h transforms to the measured velocity vector

D) **Vacuum control**
- Single LUT-08 on L=64, 300 steps, confirm only one 4-bit cluster, stable

E) **Collision experiments (9 impact parameters)**
- L=64, origins: pA at (20, 32, 20), pC at (44, 32+dy, 44)
- dy = 0, ±1, ±2, ±3, ±4
- Each collision runs for 300 steps
- Save the full grid state every 10 steps from step 0 to step 300

F) **Debris analysis (starting at step 60)**
- At each saved step from step 60 to 300:
  - Extract all occupied cells via `grid_cells(grid)`
  - Cluster by spatial proximity: two cells are connected if toroidal Manhattan distance (sum of wrapped coordinate differences) ≤ 4
  - For each cluster, record: bit_count, set of (l,r,c,ch) cells

G) **Cluster tracking across time**
- Match clusters at consecutive analysis steps by overlap: a cluster at step t+10 matches the cluster at step t with the most cells in common (by position)
- Track: (cluster_id, list of (step, cells, com, bit_count))

H) **Classification of each tracked cluster**
- **Propagating**: net CoM displacement ≥ 2 cells over the tracking window, velocity variance < 20%
- **Stationary**: net CoM displacement < 1 cell over tracking window
- For propagating clusters: compute average velocity, period (using is_translate), bit_count

I) **O_h orbit matching for propagating clusters**
- If bit_count == 4 AND period == 2 (±1) AND velocity matches any O_h-rotated LUT-08 velocity within 0.3 cells/tick: → "LUT-08_scattered"
- Otherwise: → "NEW_CANDIDATE"

J) **300-step vacuum isolation for NEW_CANDIDATE**
- Extract the candidate pattern at the first step where it appears as a cluster
- Place on clean L=64 grid at center (32,32,32)
- Run 300 steps, check:
  - bit_count constant at every step
  - velocity drift < 10%
  - periodicity maintained (shape autocorrelation)
- If all pass: candidate is a genuine stable species
- If any fail: candidate is a transient, refuted

K) **Falsification evaluation**
- F1: No stable propagating patterns across all 9 configs → REFUTED
- F2: All propagating patterns are LUT-08 (after O_h filter) → REFUTED
- F3: All stable debris are stationary → REFUTED
- F4: Pair production (if any) not robust to ±1 lattice-unit variation → REFUTED

L) **Save results**
- JSON to `archive/iter_247/results/pair_production_results.json`
- Print detailed summary to stdout

### Step 2: Execute the experiment
Run `python3 src/experiment_247_pair_production.py` and capture output.

### Step 3: Write RESEARCH-RESULT-247.md
To `archive/iter_247/results/RESEARCH-RESULT-247.md`, following the mandated structure:
- Pre-Declared Hypothesis & Falsification
- Protocol
- Observations
- Verdict
- Construction-vs-Empirical Note
- Limitations

### Key Implementation Notes
- Use `grid_cells(grid)` to get all occupied (l,r,c,ch) tuples — this preserves channel info
- For clustering, use only spatial coordinates (l,r,c) with toroidal distance; group all channels at same position
- For CoM computation, use `compute_com_circular` which handles toroidal wrapping
- For period detection, use `is_translate` comparing cluster shapes at different time steps
- The `find_pC` logic: iterate over all 48 O_h transforms, apply each to pA, find the one whose step-1 displacement is closest to -dA (i.e. same chirality, opposite direction), with det(M)=1 (proper rotation)
- Keep the code CLEAN and under 220 lines