# Current Research State
Phase: Phase 7.1 — Glider Taxonomy (13-Channel Cooperative Trapping NULL RESULT)

## Goal
Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.

## Confirmed (New in Phase 251)

- **2D hex v=0.469c glider is GENUINE with binding energy > 0 (iter_251, sub 251.2/iter_001):** Positive control re-confirmed. All 3 constituent bits annihilate when isolated. Full L-tromino survives at v=0.469c. 500/501 OR mismatches. Cooperative survival (weight-1→0) is the mechanism.

- **13-channel FCC engine works correctly (iter_251, sub 251.1):** src/fcc_engine_13ch.py implements pack/unpack/stream/collide for 13-bit states. All 500 generated LUTs pass bijectivity + bit conservation + O_h symmetry audits.

- **Cross-orbit weight-2 C↔E mapping is MATHEMATICALLY IMPOSSIBLE under O_h (iter_251, sub 251.1):** The stabilizer subgroups of orbit C (perpendicular prop pair) and orbit E (rest+prop pair) are non-conjugate in O_h. By the theorem on transitive G-sets (isomorphic iff stabilizers are conjugate), no O_h-equivariant bijection exists between these orbits. The same applies to B↔D. This eliminates the primary F5 compliance mechanism at weight-2 level.

- **Cooperative trapping produces STATIONARY OSCILLATORS, not propagating gliders (iter_251, sub 251.2):** 2500 search runs (100 LUTs × 25 seeds × 300 steps). Adjacent 2-bit seeds with rest channel: max displacement = 7.35 over 300 steps (v ≈ 0.024c). Adjacent 2-bit seeds without rest: max 214.35 (v ≈ 0.71c). The rest channel reduces motion by 29x.

- **ALL high-displacement configurations are non-interacting composites (iter_251, sub 251.2):** Top 20 runs use nonadjacent seeds with IDENTICAL displacement (323.6) across ALL LUT variants. Bits at separate cells never interact. The LUT cannot affect their trajectories. This is the composite exploit.

- **Rest channel is COUNTERPRODUCTIVE for directed motion under cooperative trapping (iter_251, sub 251.2):** The rest bit acts as an anchor, creating a stationary complex where the prop bit orbits the rest bit without net translation. This is the opposite of the predicted effect.

## Confirmed (Prior, Recontextualized)

- **LUT-08 is a non-interacting composite (iter_248):** Extended — ALL O_h-symmetric single-cell collision rules (additive AND non-additive) produce only non-interacting composites (iter_250).
- **2D hex v=0.469c sub-light glider (iter_222):** GENUINE. Confirmed in iter_250 and iter_251.
- **Complete fundamental 6-cycle single-bit spectrum (iter_248):** Still valid for 12-channel system.

## Refuted

- **13-channel cooperative trapping produces genuine multi-bit gliders with binding energy > 0 (iter_251, F1 likely triggered):** REFUTED. No adjacent-seed configuration produces meaningful propagation with the rest channel present. Max adjacent-with-rest displacement = 7.35 over 300 steps ≈ stationary oscillator.
- **Rest channel enables neighborhood-overlap binding in 3D FCC (iter_251):** REFUTED. Rest channel combined with cooperative trapping creates stationary oscillators (prop bit orbits rest bit), not propagating gliders.
- **Cross-orbit C↔E weight-2 mapping enables active channel mixing under O_h (iter_251, sub 251.1):** MATHEMATICALLY IMPOSSIBLE. Stabilizer subgroups of C and E are non-conjugate. No equivariant bijection exists.

## Incomplete (Blocked by Token Limits)

- Single-bit decomposition test (T1) on adjacent-seed candidates: Not run. Low displacement (7.35) makes it unlikely any genuine gliders exist, but formal F2 confirmation is pending.
- 12-channel control (F4): Not run. Expected result: 12-channel with Cartesian weight-1 produces similar composites to 13-channel without rest (already confirmed in iter_248/250).
- O_h covariance test (T3): Not run. No genuine candidates to test.
- F5 deep analysis (weight-3+ orbit pairings): Not completed. Whether weight-3+ pairings involve rest channel mixing is analytically determinable but was not computed.

## Open Questions

1. Can bit conservation be relaxed (with pre-registered justification based on 2D hex precedent) to enable cooperative survival (weight-1→0) in 3D FCC? This is the most promising direction since the 2D hex mechanism is the ONLY confirmed mechanism for genuine multi-bit binding.
2. Can multi-site collision operators replicate the neighborhood-overlap binding mechanism in 3D FCC?
3. Is O_h symmetry too restrictive for multi-bit binding? Would a subgroup (e.g., C4v or D4h) enable cross-orbit weight-2 mappings?
4. Can the rest channel be redesigned to enable "hopping" propagation rather than stationary orbiting?
5. Does reducing symmetry from O_h to a subgroup enable C↔E cross-orbit mapping?
6. Can the 2D hex binding mechanism be directly ported to 3D hexagonal close-packed lattices?
