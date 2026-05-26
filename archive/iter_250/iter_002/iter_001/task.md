Execute the three-stage construction, search, and verification plan for O_h-symmetric non-additive LUTs on the 3D FCC lattice with the cooperative propulsion weight-1 sub-table.

### Goal
Determine whether any bijective, bit-conserving, O_h-symmetric non-additive single-cell LUT can support a genuine multi-bit bound glider under the "Cooperative Propulsion" design principle, or establish a definitive null result.

### Stage 1: Construct the 48 O_h permutations, actions, orbits, and stabilizers
Build `src/non_additive_lut_v2.py`. Use the orbit infrastructure of `src/search_3d_gliders.py` (or write your own matching it) to:
1. Build the 48 permutations of channel indices from the O_h point group.
2. Compute orbits of the 4096 states under O_h, and their stabilizers.
3. Group orbits by signature `(w, sz, stab_set)`.
4. Define the target weight-1 sub-table as the antipodal transposition mapping:
   ch0<->ch1, ch2<->ch3, ch4<->ch5, ch6<->ch9, ch7<->ch10, ch8<->ch11.
   Confirm this is O_h-symmetric.
5. For weight-2 orbits (O_0, O_1, O_2, O_3):
   - Find all valid targets with matching stabilizers for their representatives.
   - Show that there are exactly 256 unique O_h-symmetric weight-2 sub-tables.
6. Generate 40 distinct O_h-symmetric non-additive LUT variants using equivariant orbit matching for weight-2+, pinning the weight-1 sub-table to the antipodal transposition.
7. Construct the ADDITIVE control LUT where weight-1 is the transposition and weight-2+ is the additive extension of weight-1.
8. Verify all LUTs: bijectivity, bit conservation, O_h symmetry, and calculate their non-additivity measure.
9. Save the control LUT and all 40 variants (e.g., in `src/non_additive_luts.npz` or as json/numpy files).

### Stage 2: Systematic Seed Search
Build `src/experiment_250_nonadditive_search.py`.
1. Implement a high-speed sparse simulator (using coordinates and channels, similar to `src/experiment_248_fundamental_spectrum.py`) to run seeds for 200 steps on an L=32 FCC grid.
2. To optimize speed, abort simulations early if bit count grows (e.g. exceeds 10) or drops.
3. **Exhaustive Weight-2 Sweep**: Sweep ALL 256 unique O_h-symmetric weight-2 sub-tables across ALL 66 weight-2 seeds (2 bits in the same cell, all channel pairs). This is a mathematically complete search of the entire weight-2 symmetric rule space!
4. **Weight-3 Sweep**: Sweep all 40 non-additive LUT variants across all 220 weight-3 seeds (3 bits in the same cell, all channel pairs).
5. **Control Sweep**: Run the same seeds under the ADDITIVE control LUT to confirm that no moving gliders are produced (expected: 0 gliders, only stationary oscillators).
6. Candidates must have:
   - Perfect bit count preservation (remains exactly conserved).
   - Displacement > 2.0 lattice units over 200 steps.
   - Pattern spread < 4.0 units (localization).

### Stage 3: Three-Test Coherence Verification
Apply to any candidates found:
1. **Single-Bit Decomposition Test**: Run each of the N constituent bits alone. If any subset of M < N bits propagates with the same velocity and trajectory as the full N-bit glider, binding energy = 0 and F3 is triggered.
2. **Bit-Removal Stability Test**: Verify that removing any bit alters the remaining pattern's trajectory.
3. **O_h Covariance Test**: Apply all 48 O_h rotations to the glider seed (using `rotate_particle_list` with `M_g = S_rot.T @ S_pinv.T` as in `src/test_oh_covariance.py`). Verify that the rotated seeds propagate with rotated velocities.

### Output
Write a detailed markdown report of the findings and save it to `archive/iter_250/results/nonadditive_search_report.md`.
If no gliders are found, report this as a definitive null result (F2/F3 triggered). Keep language restrained, precise, and falsifiable. No hype.