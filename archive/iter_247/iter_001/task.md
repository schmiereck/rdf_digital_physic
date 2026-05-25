## Task: Phase 7.4 — Pair Production Experiment with O_h-Equivalence Filter

### CRITICAL: Read Pre-Registration First
Before writing ANY code, read `src/pre_registration.md` and adhere to ALL falsification criteria declared there. Then update it with the three mandates below.

### Manager's Three Mandates (MUST be added to pre-registration)

1. **O_h-Equivalence Filter**: Any candidate glider found in collision debris whose bit-count is 8 AND whose velocity vector matches any member of the LUT-08 O_h orbit (all 48 O_h rotations of the LUT-08 velocity vector) must be classified as "scattered/deflected LUT-08", NOT as a newly produced species. The LUT-08 velocity in Cartesian coordinates is approximately v ≈ [0.25, -0.5, 1.0] cells/tick (compute exact value from simulation). You must generate all 48 O_h-rotated velocity vectors using the transformation matrices from `src/rigorous_glider_audit.py::build_oh_transforms()`. A candidate glider matches an O_h orbit member if: (a) bit-count = 8, (b) |v_candidate - v_rotated| < 0.3 cells/tick for some O_h rotation, (c) period matches LUT-08 period (±1 step).

2. **300-Step Vacuum Isolation Test**: Any candidate pattern extracted from debris that passes the O_h filter (i.e. is NOT classified as LUT-08) must be isolated on a completely clean L=64 vacuum grid and simulated for 300 steps. It is REFUTED as a stable species if, during this 300-step run: (a) total bit count changes at any step, (b) average velocity shows monotonic drift > 10% over the run, or (c) periodic cycle breaks (shape autocorrelation drops below 0.5).

3. **Pre-Registration Compliance**: All execution must strictly follow the pre-registered protocol. No post-hoc parameter tuning.

### Experiment Protocol

Create `src/experiment_247_pair_production.py` (~200 lines max):

**Setup:**
- L=64 FCC toroidal grid
- Load LUT-08 from `archive/iter_224/results/glider_00_lut08_sub03.json`
- Use `src/engine_3d.py` for stream/collide
- Use `src/glider_charge_analysis.py::make_BT`, `reflect` for P-reflection
- Use `src/rigorous_glider_audit.py::build_oh_transforms` for O_h transforms

**Collision configurations (8 impact parameters):**
- Place two identical-chirality LUT-08 gliders (both original particle from JSON) on head-on collision course
- Particle A at origin oA = (20, 32, 20), moving toward Particle B
- Particle B at origin oB = (44, 32, 44), moving toward Particle A
- 5 original impact parameters: transverse offset dy = 0, ±1, ±2 (add to row coordinate of B)
- 3 extended impact parameters: dy = ±3, ±4 (for F4 robustness)

**Run each collision for 300 steps.**

**Debris Analysis (starting at step 60, post-collision settling):**
- Every 10 steps from t=60 to t=300, extract all bit positions
- Cluster bits using 6-connectivity (max distance R=4 between connected bits, with toroidal wrapping)
- Track each cluster's center-of-mass over 40-step windows
- For each cluster, compute:
  - bit_count: number of bits
  - velocity: average displacement per step over the tracking window
  - period: detect by autocorrelation of cluster shape (or just track CoM displacement pattern)
  - is_propagating: True if net displacement ≥ 2 cells over ≥ 2 tracking windows with <20% velocity variance
  - is_stationary: True if net displacement < 1 cell over all tracking windows

**O_h Orbit Matching:**
- Compute LUT-08's exact velocity by running a single LUT-08 for 80 steps and measuring CoM displacement per step
- Generate all 48 O_h-rotated velocity vectors using build_oh_transforms()
- For each propagating cluster with bit_count=8, check if its velocity matches any O_h-rotated LUT-08 velocity (within 0.3 cells/tick tolerance)
- Classify as "LUT-08_scattered" if match found, "NEW_CANDIDATE" otherwise

**Vacuum Control:**
- Run a single LUT-08 on L=64 for 300 steps
- Confirm no spontaneous debris gliders appear (only the one 8-bit cluster)

**300-Step Vacuum Isolation (for any NEW_CANDIDATE):**
- Extract the candidate pattern at some step after collision
- Place it on a clean L=64 grid at center (32,32,32)
- Run for 300 steps
- Check: bit count constant, velocity stable, periodic cycle maintained
- If any check fails: candidate is a transient, not a stable species

**Falsification Evaluation:**
After all runs, evaluate the four pre-registered falsification criteria:
- F1: No stable propagating patterns in debris across all 8 configs → REFUTED
- F2: All propagating patterns are LUT-08 (after O_h orbit check) → REFUTED
- F3: All stable debris objects are stationary → REFUTED
- F4: Pair production not robust to ±1 lattice-unit variation → REFUTED

**Output:**
- Print detailed results to stdout
- Save JSON results to `archive/iter_247/results/pair_production_results.json`
- The JSON must include: all collision configs with impact_param, debris_bit_count, n_stationary, n_propagating, propagating_details (bit_count, velocity, is_LUT08_orbit, O_h_match_if_any), vacuum_control_ok, F1_through_F4 evaluations, verdict (SUPPORTED/INCONCLUSIVE/REFUTED)

**Important Implementation Notes:**
- Use toroidal distance computation for clustering (wrap-around on L=64 grid)
- For CoM computation, use circular mean to handle toroidal wrapping (similar to compute_com_circular in rigorous_glider_audit.py)
- Keep the script under 250 lines
- DO NOT use any float values inside the physics engine (only in analysis/diagnostics)
- The CA rule (stream + collide with LUT) is strictly local, binary, O_h-symmetric, reversible, and bit-conserving

**Update Pre-Registration:**
After writing the script but BEFORE executing it, update `src/pre_registration.md` to include the three manager mandates (O_h-equivalence filter, 300-step stability test, pre-registration compliance) in sections 2 and 3.

Then execute the experiment and save results.