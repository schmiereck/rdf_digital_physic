## Task: Run Full 13-Channel Cooperative Trapping Search and Analysis

You are executing the experimental phase of iteration 251. The infrastructure is already built:
- src/fcc_engine_13ch.py: 13-channel engine (pack/unpack/stream/collide/verify for 13-bit states)
- src/cooperative_lut_13ch.py: Parametric LUT family with cooperative trapping (weight-1→antiparallel, weight-2 self-maps, weight-3+ random orbit pairing)
- 500 valid LUT variants generated, all passing bijection/bit-conservation/O_h symmetry audits

### CRITICAL MATHEMATICAL FINDING (from sub-goal 251.1)
Cross-orbit weight-2 mappings (C↔E, B↔D) are **mathematically impossible** under O_h symmetry because the stabilizer subgroups of orbits C and E (and B and D) are non-conjugate. This is a theorem — two transitive G-sets are isomorphic iff their stabilizers are conjugate. Therefore:
- ALL 500 LUT variants use weight-2 self-maps only
- Active channel mixing (F5) must occur through weight-3+ orbit pairings that involve the rest channel
- Update src/pre_registration.md Step 4 to reflect this — remove the C↔E requirement and note F5 compliance comes from weight-3+ dynamics

### Read Pre-Registration First
Read src/pre_registration.md and adhere to ALL pre-registered hypotheses and falsification criteria (F1–F5).

### Experimental Pipeline (execute sequentially)

#### Step 1: Update Pre-Registration
Fix Step 4 of src/pre_registration.md to remove the impossible C↔E requirement. Replace with:
"Weight-2 orbit mappings are self-maps only (cross-orbit C↔E and B↔D mappings are mathematically impossible under O_h due to non-conjugate stabilizer subgroups). F5 compliance must be achieved through weight-3+ orbit pairings where rest-channel states map to non-rest-channel states and vice versa."

#### Step 2: Positive Control (2D Hex)
Run the known 2D hex v=0.469c glider rule for 500 steps and confirm:
- Binding energy > 0 (single-bit decomposition kills all constituent bits)
- Cooperative survival active (weight-1→0)
This validates the search methodology. Use src/experiment_250_hex_decomposition.py as reference.

#### Step 3: Build Search Script (src/search_13ch.py)
Create a search script that:
1. Loads the 500 LUT variants from src/cooperative_lut_13ch.py (regenerate them using generate_all_lut_variants)
2. Defines 30 diverse seeds for the 13-channel system:
   - 5 seeds with 2 adjacent bits including 1 rest bit (e.g., cell (12,12,12) with ch0+ch12)
   - 5 seeds with 2 adjacent bits both prop (e.g., cell (12,12,12) with ch0+ch4)
   - 5 seeds with 3 adjacent bits including rest (e.g., ch0+ch4+ch12)
   - 5 seeds with 3 adjacent bits all prop (e.g., ch0+ch4+ch7)
   - 5 seeds with 2-3 bits at non-adjacent cells (separate cells with 1-2 bits each)
   - 5 seeds with 4-5 bits in asymmetric arrangements
3. For each (LUT, seed) pair, runs 300 steps on L=24 FCC toroidal grid
4. Tracks: unwrapped center-of-mass displacement, bit count stability, bounding extent, rest channel occupancy
5. Scores each run by: displacement_norm * bit_stability (where bit_stability = 1 if final_bits == initial_bits, 0 otherwise)
6. Records rest channel activity (how often ch12 is occupied vs empty across time steps)

#### Step 4: Run 12-Channel Control (F4 test)
Create and run src/search_12ch_control.py that:
1. Uses the SAME 12-channel O_h-equivariant LUTs (from src/non_additive_lut_v2.py's build_additive_lut or generate_symmetric_lut with Cartesian weight-1)
2. Tests the same prop-only seeds (seeds without ch12, adapted to 12 channels)
3. Uses the same scoring and tracking
4. This tests whether the rest channel specifically enables binding

Note: The 12-channel control uses the same weight-1 mechanism (Cartesian transposition) but no rest channel. If 13-channel finds gliders but 12-channel doesn't, the rest channel is the enabling factor (F4 not triggered).

#### Step 5: Parametric Search Execution
Run the search. For computational efficiency:
- Use numpy vectorized operations where possible
- Target: complete all 500 LUTs × 30 seeds × 300 steps within 10 minutes
- If this is too slow, reduce: use 100 LUT variants × 30 seeds × 300 steps (sample every 5th LUT variant)
- Write all results to archive/iter_251/results/search_results.json

#### Step 6: Candidate Analysis
For any (LUT, seed) pair that:
- Survives ≥200 steps (F1 not triggered for that pair)
- Has displacement_norm > 1.0 (net motion)
- Has bit_stability = 1 (bit conservation maintained)

Run extended analysis:
a) Single-bit decomposition test (T1): Remove each constituent bit individually. If removing any bit changes the propagation trajectory or speed, binding energy > 0.
b) O_h covariance test (T3): Run the same seed under all 48 O_h rotations of the grid. If the glider propagates consistently, it's O_h-covariant.
c) F5 active channel mixing: Check whether ch12 occupancy oscillates during propagation (not always 0 or always 1). Check whether the rest bit changes position (converted to prop and back).

#### Step 7: Synthesize Results
Write archive/iter_251/results/experiment_report.json with:
- total_runs: number of (LUT, seed) pairs tested
- candidates_surviving_200steps: count
- candidates_passing_T1: count  
- candidates_passing_T3: count
- candidates_passing_F5: count
- f1_triggered: bool (no multi-bit configuration survives ≥200 steps)
- f2_triggered: bool (all survivors fail single-bit decomposition)
- f3_triggered: bool (any discovered glider fails O_h covariance)
- f4_triggered: bool (12-channel control produces gliders at same rate)
- f5_triggered: bool (rest channel not dynamically active)
- verdict: string summarizing findings
- positive_control_passed: bool
- 12ch_control_glider_count: int
- best_candidate: dict or null

### Important Notes
- The LUT construction uses cooperative TRAPPING (not survival). Weight-1 states are NOT killed — they oscillate (prop → antiparallel → back). This is bit-conserving.
- For F5: even though weight-2 cross-orbit mapping is impossible, weight-3+ orbit pairings CAN involve the rest channel. Some LUTs will have weight-3 states with ch12 mapping to weight-3 states without ch12, and vice versa. Check for this.
- The 13-channel engine uses src/fcc_engine_13ch.py. The 12-channel engine uses src/engine_3d.py.
- The simulate_track function in src/search_3d_gliders.py can be adapted for 13 channels.
- Be careful: the 13-channel grid has shape (L,H,W,13), not (L,H,W,12).

### Success Criteria
- Positive control passes (2D hex glider confirmed genuine)
- ≥100 (LUT, seed) pairs tested on FCC-13
- 12-channel control executed
- All 5 falsification criteria evaluated
- Comprehensive experiment_report.json written
