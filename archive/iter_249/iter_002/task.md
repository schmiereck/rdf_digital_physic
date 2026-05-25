# Phase 249 Sub-Goal B: Systematic Collision Search with Non-Additive LUTs

## CRITICAL CONTEXT
Read `src/pre_registration.md` first for the pre-registered hypothesis and falsification criteria.

In iter_248, we proved that ALL 3D FCC gliders under O_h-symmetric additive LUTs are non-interacting composites of single-bit period-2 particles. The root cause: the LUT maps weight-2 states as the independent superposition of weight-1 transpositions. Bits from different velocity cycles never interact.

Sub-goal 249.1 built `src/lut_construction_nonadditive.py` and `src/coherence_testing.py`, but the LUT construction needs improvement. Your task: reconstruct verified non-additive LUTs, then run the full collision search with coherence testing.

## Part 1: Reconstruct Non-Additive LUT Variants (Fix + Verify)

The existing `src/lut_construction_nonadditive.py` has issues:
- The "binding" variant maps states to themselves (identity), which is questionable
- The modifications aren't well-documented
- The orbit analysis is incomplete

### What you MUST do:

**Step 1.1:** Load LUT-08 from `archive/iter_224/results/glider_00_lut08_sub03.json`.

**Step 1.2:** Analyze the weight-2 orbit structure. Use `src/search_3d_gliders.py` functions (get_oh_permutations, precompute_perm_action, compute_orbits) to:
- Identify all weight-2 states (Hamming weight = 2, 66 states)
- Group them into O_h orbits
- For each orbit, determine: which channel pairs it represents, what the LUT-08 output is, and what velocity cycles the output bits belong to

**Step 1.3:** Document the orbit structure. Print or save a table showing:
- Orbit ID, orbit size, representative state (channel pair), LUT-08 output (channel pair), and velocity cycle membership of output channels

**Step 1.4:** Construct non-additive variants using orbit remapping. The key insight: within a Hamming-weight group, the generate_symmetric_lut() algorithm randomly pairs source orbits with destination orbits. To make a non-additive LUT, we need to CHANGE which destination orbit a source orbit maps to.

The correct approach:
1. Use generate_symmetric_lut() with different seeds to get the orbit-to-orbit pairing
2. OR: manually identify which weight-2 orbit pairs map to which in LUT-08, then swap the pairings

For each non-additive variant, the modification must be:
- An orbit-to-orbit remapping (not individual state overrides)
- Verified to preserve bijectivity (the destination orbits must not be double-booked)
- Verified to preserve bit conservation
- Verified to preserve O_h symmetry

**Step 1.5:** Construct at least 3 variants:

**Variant 1 (EXCHANGE):** For two weight-2 source orbits that map to different destination orbits, swap their destination orbit assignments. This creates cross-cycle interaction.

**Variant 2 (CYCLE-REDIRECT):** For a weight-2 source orbit whose LUT-08 output sends the two bits to two different velocity cycles, remap it so the output sends both bits into the same velocity cycle (or at least closer together in velocity space). This may not be possible for all orbits — document which ones can and can't be redirected.

**Variant 3 (SCATTERING):** For weight-2 source orbits, redirect their outputs to a "slow" velocity cycle (e.g., the stationary cycle {8,11} or the {9,10} cycle). This creates dissipation at collision sites.

**IMPORTANT:** If a particular modification cannot be made consistent with O_h symmetry, bit conservation, and bijectivity, document it as a negative finding. Do NOT force invalid modifications.

**Step 1.6:** For each variant, run `verify_lut()` from `src/search_3d_gliders.py` to confirm bijection, bit conservation, and O_h symmetry. Print the full verification results.

**Step 1.7:** Also verify each variant's weight-1 cycles are the same as LUT-08 (6 period-2 cycles). If the weight-1 cycles changed, the variant is invalid — weight-1 interactions should be preserved.

**Step 1.8:** Save each verified LUT as `src/nonadditive_lut_<name>.npy` and save metadata as `src/nonadditive_lut_metadata.json` documenting:
- Which orbit pairs were remapped
- Original destination orbit → new destination orbit
- Physical reasoning for each modification
- Verification results

## Part 2: Systematic Collision Search

**Step 2.1:** For each non-additive LUT variant (and LUT-08 as control), set up two-bit collision initial conditions.

The LUT-08 weight-1 cycles and their velocities (from iter_248 fundamental_spectrum.json):
- Cycle {0,3}: v = (0, 0.5, -0.5) grid units/step
- Cycle {1,2}: v = (0, -0.5, 0.5) grid units/step
- Cycle {4,7}: v = (0.5, 1.0, -0.5) grid units/step
- Cycle {5,6}: v = (0.5, 0.0, 1.0) grid units/step
- Cycle {8,11}: v = (0, 0, 0) — stationary oscillator
- Cycle {9,10}: v = (-1, -1, -0.5) grid units/step

Select O_h-distinct collision geometries:
- Two particles from DIFFERENT velocity cycles on collision courses
- At least 6 initial configurations per LUT variant (different cycle pairs, different impact parameters)
- Place on L=64 grid with collision center at (32, 32, 32)
- Space particles so they will collide at the center within ~20 steps

**Step 2.2:** For each collision, run the simulation for 250 steps.

**Step 2.3:** Track the collision outcome:
- Does a coherent multi-bit structure survive?
- Track: bit count, center of mass, bounding extent per step
- Identify any structure that survives ≥50 steps with bounded extent and constant bit count

**Step 2.4:** For any candidate surviving ≥50 steps, apply the three-test coherence protocol from `src/coherence_testing.py`:
- Test A (decomposition): Run each bit independently
- Test B (collision interaction): Check multi-bit cell count
- Test C (bit-removal): Remove one bit and check stability

**Step 2.5:** For any candidate that passes the coherence protocol (i.e., is a genuine glider), run O_h rotation test: rotate initial conditions through all 48 O_h elements and verify the glider exists in rotated form.

**Step 2.6:** Compare against LUT-08 control. Run the same collision configurations on LUT-08 and confirm that no genuine gliders emerge (reproducing the iter_248 null result).

## Part 3: Report Results

Save results to `archive/iter_249/results/` directory:
- `collision_results.json` — all collision outcomes
- `coherence_results.json` — results of three-test protocol for any candidates
- `orbit_analysis.json` — weight-2 orbit structure
- `lut_verification.json` — verification results for all LUT variants
- `experiment_report.md` — human-readable summary

## Key Files to Read
- `src/pre_registration.md` — hypothesis and falsification criteria
- `src/engine_3d.py` — 3D FCC LGCA engine
- `src/search_3d_gliders.py` — LUT generation, O_h permutations, verify_lut()
- `src/coherence_testing.py` — three-test protocol (already built)
- `src/lut_construction_nonadditive.py` — existing LUT construction (may need fixing)
- `src/experiment_248_fundamental_spectrum.py` — weight-1 cycle analysis, sparse simulation
- `archive/iter_224/results/glider_00_lut08_sub03.json` — LUT-08 reference
- `archive/iter_248/results/fundamental_spectrum.json` — fundamental spectrum data

## Key Code Patterns (from existing code)

The sparse simulation approach from experiment_248_fundamental_spectrum.py:
```python
def stream_bits(bits, L):
    return [((l + SHIFTS[ch][0]) % L, (r + SHIFTS[ch][1]) % L, (c + SHIFTS[ch][2]) % L, ch) for (l, r, c, ch) in bits]

def collide_bits(bits, lut):
    cell_map = {}
    for (l, r, c, ch) in bits:
        cell_map[(l, r, c)] = cell_map.get((l, r, c), 0) | (1 << ch)
    new_bits = []
    for (l, r, c), packed in cell_map.items():
        new_packed = lut[packed]
        for ch in range(12):
            if (new_packed >> ch) & 1:
                new_bits.append((l, r, c, ch))
    return new_bits
```

This is much faster than full grid simulation for small particle counts.

## Success Criteria
1. At least 3 non-additive LUT variants constructed and verified (bijection + bit conservation + O_h symmetry + weight-1 preservation)
2. Orbit structure documented
3. Collision search completed across all LUT variants (≥6 configurations each)
4. Three-test coherence protocol applied to any survivors
5. LUT-08 control confirms null result
6. All results saved with proper documentation

## Falsification Protocol
Per the pre-registration, the hypothesis is REFUTED if ANY of:
- F1: No two-bit bound state survives ≥200 steps under any non-additive LUT variant
- F2: Any survivor passes the decomposition test (non-interacting composite)
- F3: Any survivor exists only along one lattice axis (lattice artifact)
- F4: Non-additive LUTs violate reversibility or bit conservation
