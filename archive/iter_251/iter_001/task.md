## Task: Implement FCC-13 Engine and Cooperative Trapping LUT Infrastructure

You are implementing the core infrastructure for a 13-channel 3D FCC LGCA with cooperative trapping dynamics. Read src/pre_registration.md first — you must adhere to all pre-registered hypotheses and falsification criteria.

### Context
The 12-channel FCC LGCA (src/engine_3d.py) cannot produce genuine multi-bit bound gliders because all interactions are transient — every bit must propagate away each step. The 2D hex v=0.469c glider (iter_222/250) IS genuine (binding energy > 0) because its rule uses neighborhood-overlap bit creation, which is structurally absent in single-cell 3D FCC.

The 13th channel is a **rest-mass channel** (channel index 12) that does NOT shift during propagation. This provides the "sticky" interaction site that enables sustained multi-step interactions within a single cell.

### CRITICAL DESIGN CONSTRAINT
The Manager mandates **bijectivity + bit conservation**. The original "cooperative survival" (weight-1→0) violates both. Instead, use **cooperative trapping**:
- Weight-1 prop states → antiparallel partner (Cartesian transposition): bit-conserving, bijective, O_h-invariant
- Weight-1 rest state → itself: stationary fixed point
- Weight-2+ states: O_h-equivariant non-additive mappings with parametric freedom

### Deliverable 1: Update src/pre_registration.md
Add F5 as specified by the Manager:
```
F5: Active Channel Mixing — the hypothesis is refuted if the rest-mass channel is either 
statically occupied (always 1) or never occupied (always 0) during any discovered 
glider's propagation cycle, or if there is zero transition of bits between the 12 
propagation channels and the 13th rest channel. The rest-mass channel must actively 
act as a dynamical mediator (exchanging momentum/state) during the propagation period.
```
Also update the hypothesis to reflect cooperative trapping (not cooperative survival) and note the bit-conservation constraint.

### Deliverable 2: Create src/fcc_engine_13ch.py
Extend src/engine_3d.py to 13 channels:

1. **SHIFTS_13**: Same 12 shifts as SHIFTS in engine_3d.py, plus channel 12 has shift (0,0,0) (rest channel doesn't move).

2. **pack_13(grid)**: Pack (L,H,W,13) grid → (L,H,W) uint16 array.
   - Bit i of packed value = grid[..., i] for i in 0..12
   
3. **unpack_13(packed)**: Unpack (L,H,W) → (L,H,W,13) uint8 array.

4. **stream_13(grid, reverse=False)**: Same as stream() but for 13 channels. Channel 12 gets np.roll with shift (0,0,0) — effectively a no-op copy.

5. **collide_13(grid, lut)**: Same as collide() but lut has size 8192 (2^13).

6. **invert_lut_13(lut)**: Invert an 8192-entry permutation LUT.

7. **verify_lut_13(lut)**: Check bijection (8192 unique values), bit conservation (hamming(s) == hamming(lut[s]) for all s), O_h symmetry (see below).

### Deliverable 3: Create src/cooperative_lut_13ch.py
This is the core LUT construction module. It must:

#### 3a. O_h Permutations for 13 Channels
The O_h action on 13 channels: for each of the 48 signed-permutation matrices acting on FCC vectors, produce a permutation of {0,...,12} where channels 0-11 are permuted as in the 12-channel system and channel 12 maps to itself.

Build this by:
```python
# For each 12-channel perm sigma from get_oh_permutations():
# 13-channel perm = sigma + (12,)  (i.e., sigma[0]...sigma[11], 12)
```

#### 3b. Orbit Classification for 13-Channel System
Compute orbits of {0,...,8191} under the 48 O_h 13-channel permutations. Group by Hamming weight.

The weight-2 orbits should include exactly 5 types:
1. **Antiparallel prop pair** (6 states): e.g., {ch0, ch3} — 6 pairs of antiparallel channels
2. **Obtuse prop pair** (24 states): pairs at 120° angle
3. **Perpendicular prop pair** (12 states): pairs at 90° angle  
4. **Acute prop pair** (24 states): pairs at 60° angle
5. **Rest+prop pair** (12 states): {ch12, ch_k} for k=0..11

Verify: 6 + 24 + 12 + 24 + 12 = 78 = C(13,2). ✓

#### 3c. Parametric LUT Family
Build a function `build_cooperative_lut_13ch(config)` that generates LUTs:

**Weight-0**: state 0 → 0 (fixed)

**Weight-1** (13 states): 
- Prop weight-1 states: Cartesian transposition — prop[k] → prop[antiparallel(k)]
  - CARTESIAN_PAIRS = [(0,3), (1,2), (4,7), (5,6), (8,11), (9,10)]
  - State (1<<k) maps to (1<<antiparallel(k))
- Rest weight-1 state (1<<12): maps to itself (1<<12)

**Weight-2** (78 states in 5 orbits):
For each orbit, choose a target orbit of the same size and an equivariant mapping. The parametric choices are:
- Orbit A (antiparallel, size 6): must map to A (only same-size orbit)
- Orbits B (obtuse, size 24) and D (acute, size 24): can map B→B, B↔D, or D→D
- Orbits C (perpendicular, size 12) and E (rest+prop, size 12): can map C→C, C↔E, or E→E

**CRITICAL for F5**: The C↔E swap is the key active channel mixing mechanism. When orbit E (rest+prop) maps to orbit C (perpendicular prop pair), a rest bit + prop bit converts to two prop bits (rest bit "freed"). When orbit C maps to orbit E, two prop bits convert to rest + prop (rest bit "created").

**Requirement**: At least one LUT variant MUST include C↔E or E→C mapping to satisfy F5.

For each orbit mapping choice, construct the equivariant bijection:
1. Pick representative of source orbit
2. Find valid target in destination orbit (matching stabilizer)
3. Propagate by O_h: f(g·rep) = g·target for all g

**Weight-3+**: Use the existing O_h-equivariant orbit pairing strategy from src/search_3d_gliders.py's `generate_symmetric_lut()`. Pool orbits by signature (weight, size, stabilizer conjugacy class) and pair randomly with seed.

**Total parametric freedom for weight-2**:
- A: 1 choice (self-map, but may have multiple equivariant self-maps)
- B↔D: 3 choices (B→B, B→D, D→D), each may have multiple equivariant options
- C↔E: 3 choices (C→C, C→E, E→E), each may have multiple equivariant options
- Plus stabilizer-compatible target choices within each orbit mapping

Enumerate all valid O_h-equivariant weight-2 configurations. Target ~100-500 variants.

#### 3d. Bijectivity + Bit Conservation Audit
For EVERY generated LUT:
1. Check bijection: len(np.unique(lut)) == 8192
2. Check bit conservation: hamming(s) == hamming(lut[s]) for all s in 0..8191
3. Check O_h symmetry: lut[action[g, s]] == action[g, lut[s]] for all g, s

If any LUT fails, do NOT include it in the search. Log the failure.

#### 3e. Output
Save:
- src/fcc_engine_13ch.py
- src/cooperative_lut_13ch.py
- A summary file archive/iter_251/results/infrastructure_report.json with:
  - n_lut_variants: number of valid LUT variants generated
  - n_lut_variants_with_f5: number including C↔E or E→C mapping
  - audit_pass_rate: fraction of generated LUTs passing all 3 audits
  - weight2_orbit_info: details of the 5 weight-2 orbit types
  - sample_lut_shape: [8192] 
  - weight1_mapping: description of the cooperative trapping weight-1 sub-table

### Implementation Notes
- Reuse infrastructure from src/search_3d_gliders.py (get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, hamming)
- Reuse the orbit-pairing strategy from generate_symmetric_lut() for weight-3+
- The 13-channel O_h action is trivially derived from the 12-channel action by appending identity on channel 12
- Be careful with numpy dtypes: 13-bit values need uint16 (max 8191)
- The weight-2 orbit classification MUST be verified programmatically (don't hardcode orbit memberships — compute them from the O_h action)

### Success Criteria
- fcc_engine_13ch.py implements all 7 functions correctly
- cooperative_lut_13ch.py generates ≥50 valid LUT variants passing all 3 audits
- At least 10 variants include C↔E or E→C weight-2 mapping (F5 compliance)
- infrastructure_report.json is written to archive/iter_251/results/
