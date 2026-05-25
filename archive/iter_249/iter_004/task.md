# Phase 249: Execute Hex Coherence Test + Construct Intra-Orbit Non-Additive LUTs + Run Collision Search

## OVERVIEW
This is a combined execution task with three parts. Read `src/pre_registration.md` first.

## PART 1: Execute 2D Hex Glider Coherence Test (30 minutes budget)

The script `src/hex_coherence_test.py` was already created. Fix any import/path issues and run it.

### Known Issues to Fix:
- The script imports `from evolution import ...` but this module is in `src/evolution.py`. Make sure the import path works.
- The champion rule path should be `archive/iter_222/results/champion_rule_perfect.json`
- The `make_ltromino_grid` function from evolution.py creates a grid; you may need to just use seed_cells directly.
- The script uses `step_grid(grid, lut)` from evolution.py for the CA step.
- The `rule_dict_to_lut` function converts a rule_dict (mapping 7-bit neighborhood → center bit) to a LUT array.

### What the test does:
1. Load the champion rule from iter_222
2. Run the full glider (3-cell L-tromino seed) for 200 steps
3. Run each of the 3 seed bits independently for 200 steps
4. Compare: does full glider trajectory match XOR superposition of individual bit trajectories?
5. If NOT → genuine glider (bits interact). If YES → non-interacting composite.

### Expected outcome:
The hex CA is a standard binary synchronous CA where each cell is 0 or 1. The glider starts at 3 bits and grows to ~4 bits during propagation. If single bits don't produce the same behavior when run independently, the glider is genuine. This is very likely since the CA is non-linear.

### Save results to:
- `archive/iter_249/results/hex_coherence_result.json`

## PART 2: Construct Non-Additive LUT Variants via Intra-Orbit Remapping (30 minutes budget)

From sub-agent 249.2, we learned that:
- Inter-orbit remapping (EXCHANGE) is IMPOSSIBLE because weight-2 orbits have disjoint stabilizers
- INTRA-orbit remapping IS possible: within each orbit, the representative can be remapped to different valid targets
- LUT-08 has 4 weight-2 orbits with sizes [12, 6, 24, 24]
- Orbit 6 (size 24, rep=17): valid targets = [17, 34, 68, 136] — LUT-08 maps to 17
- Orbit 8 (size 24, rep=20): valid targets = [20, 40, 65, 130] — LUT-08 maps to 65
- There are 4×2×4×4 = 128 possible intra-orbit remapping combinations

### Your task:

**Step 2.1:** Write a script `src/experiment_249_collision_search.py` that:

a) Loads LUT-08 from `archive/iter_224/results/glider_00_lut08_sub03.json`

b) Uses `src/search_3d_gliders.py` functions to compute orbits, stabilizers, and the weight-2 orbit structure

c) Determines the current LUT-08 mapping for each weight-2 orbit representative (which target does LUT-08 currently map each rep to?)

d) Generates non-additive LUT variants by changing the target of one or more orbit representatives to a different valid target within the same orbit.

e) Selects AT LEAST 5 representative remapping combinations that test different physics:
   - Variant A: Remap orbit-6 rep from 17→34 (changes one weight-2 orbit mapping)
   - Variant B: Remap orbit-6 rep from 17→68 (different target in same orbit)
   - Variant C: Remap orbit-8 rep from 65→20 (changes the other main orbit)
   - Variant D: Remap both orbit-6 and orbit-8 simultaneously
   - Variant E: Remap orbit-6 rep to 136 (explore all 4 options for largest orbit)

f) For each variant, construct the full 4096-entry LUT by:
   - Starting from LUT-08
   - For the modified orbit, changing the mapping of the representative and all its O_h transforms
   - Specifically: if we remap rep→new_target, then for all g in O_h: lut[action[g, rep]] = action[g, new_target]
   - CRITICAL: This must preserve bijectivity! Check that the new mapping doesn't create duplicates.

g) Verify each variant: bijection, bit conservation, O_h symmetry, weight-1 cycles preserved.

**IMPORTANT CONSTRUCTION DETAIL:** When you change lut[s] = d_new (where s was previously mapped to d_old), you must also change the INVERSE mapping. The state that was previously mapped TO d_old now has no preimage, and the state that was previously mapped FROM d_old now has two preimages. To maintain bijectivity, you need to do an ORBIT SWAP within the weight-2 group: swap the mapping of two orbits so that the preimage/image relationship is preserved.

The safest approach: use generate_symmetric_lut() with a FIXED seed that produces a different orbit pairing, then keep all weight-1 mappings the same. Actually, the cleanest way is:

1. Extract the orbit-to-orbit pairing from LUT-08 (which weight-2 orbit maps to which weight-2 orbit)
2. SWAP two orbit pairs to create a new pairing
3. Rebuild the LUT from the new pairing using the equivariant construction

This is guaranteed to be bijective because it's the same construction algorithm with a different random pairing.

OR, even simpler: generate several LUTs using generate_symmetric_lut(seed=X) for different seeds, and verify that each has the same weight-1 cycles as LUT-08. If the weight-1 cycles differ, that LUT won't help us compare.

Actually, the SIMPLEST correct approach: 
1. Use generate_symmetric_lut() with different seeds to create LUTs
2. Filter for ones that have the SAME weight-1 permutation structure as LUT-08 (same 6 period-2 transposition pairs)
3. These will differ only in their weight-2+ mappings
4. Any differences in collision dynamics between these LUTs are due to different weight-2 interactions

Try seeds 0-100 and find at least 5 LUTs with the same weight-1 structure as LUT-08.

## PART 3: Run Collision Search (30 minutes budget)

**Step 3.1:** For each LUT variant (including LUT-08 as control), set up two-bit collision configurations:

The LUT-08 weight-1 cycles and their velocities:
- Cycle {0,3}: v = (0, 0.5, -0.5) grid units/step
- Cycle {1,2}: v = (0, -0.5, 0.5) grid units/step  
- Cycle {4,7}: v = (0.5, 1.0, -0.5) grid units/step
- Cycle {5,6}: v = (0.5, 0.0, 1.0) grid units/step
- Cycle {8,11}: v = (0, 0, 0) — stationary oscillator
- Cycle {9,10}: v = (-1, -1, -0.5) grid units/step

Use sparse simulation (stream_bits + collide_bits from experiment_248_fundamental_spectrum.py) for speed.

Set up collisions between two particles from DIFFERENT velocity cycles:
- Collision 1: bit from cycle {0,3} + bit from cycle {5,6} 
- Collision 2: bit from cycle {0,3} + bit from cycle {4,7}
- Collision 3: bit from cycle {5,6} + bit from cycle {9,10}
- Collision 4: bit from cycle {0,3} + bit from cycle {1,2}
- Collision 5: bit from cycle {4,7} + bit from cycle {8,11} (stationary target)
- Collision 6: bit from cycle {5,6} + bit from cycle {8,11} (stationary target)

For each collision, place the two particles at positions where they will co-locate at the same cell within ~10-20 steps. Use L=64 grid.

**Step 3.2:** Run each collision for 250 steps. Track:
- Bit count per step
- Center of mass per step  
- Bounding extent per step
- Whether the two bits ever share a cell

**Step 3.3:** Identify candidates that survive ≥50 steps with:
- Constant bit count (2 bits)
- Bounded extent
- Moving center of mass

**Step 3.4:** For any candidates, apply the three-test coherence protocol from `src/coherence_testing.py`:
- Test A: decomposition test
- Test B: collision interaction test (multi-bit cell count)
- Test C: bit-removal test

**Step 3.5:** For LUT-08 control: confirm that no genuine gliders emerge (reproducing iter_248 null result).

**Step 3.6:** Save all results to `archive/iter_249/results/collision_results.json` and `archive/iter_249/results/experiment_report.md`.

## Falsification Assessment
After all experiments, evaluate the pre-registered falsification criteria:

The hypothesis is REFUTED if ANY of (F1 OR F2 OR F3 OR F4):
- F1: No two-bit bound state survives ≥200 steps under any non-additive LUT variant
- F2: Any survivor passes the decomposition test (non-interacting composite)  
- F3: Any survivor exists only along one lattice axis (lattice artifact)
- F4: Non-additive LUTs violate reversibility or bit conservation

## Key Files
- `src/pre_registration.md` — hypothesis and criteria
- `src/engine_3d.py` — 3D FCC engine (SHIFTS, stream, collide, pack, unpack)
- `src/search_3d_gliders.py` — generate_symmetric_lut(), get_oh_permutations(), precompute_perm_action(), compute_orbits(), verify_lut(), seed_grid(), compute_com_circular(), bounding_extent()
- `src/coherence_testing.py` — three-test protocol
- `src/experiment_248_fundamental_spectrum.py` — weight-1 cycle analysis, sparse simulation helpers (stream_bits, collide_bits, weight1_cycles)
- `src/evolution.py` — 2D hex CA (rule_dict_to_lut, step_grid)
- `src/hex_coherence_test.py` — hex coherence test (may need fixing)
- `archive/iter_224/results/glider_00_lut08_sub03.json` — LUT-08 reference
- `archive/iter_222/results/champion_rule_perfect.json` — hex champion rule

## Output Requirements
1. `archive/iter_249/results/hex_coherence_result.json` — hex glider verdict
2. `archive/iter_249/results/lut_variants.json` — metadata for all LUT variants tested
3. `archive/iter_249/results/collision_results.json` — all collision outcomes
4. `archive/iter_249/results/experiment_report.md` — human-readable summary with falsification assessment
