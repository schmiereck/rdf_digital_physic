# Current Research State
Phase: Phase 7.1 — Glider Taxonomy (2D Hex Embedding REFUTED)

## Goal
Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.

## Confirmed (New in Phase 252)

- **Hex glider binding mechanism extracted (iter_252, sub 252.1b):** 4 critical neighborhood states (64, 70, 81, 104) drive initial cooperative binding. 200/201 OR-superposition mismatches (pervasive non-linearity). All 3 seed bits annihilate alone. 42 non-identity rule_dict entries.

- **F3 TRIGGERED: Pure LGCA embedding of hex rule is mathematically impossible (iter_252, sub 252.2b):** The hex CA's cooperative survival mechanism requires weight-1->0 local transitions, which violate bit conservation. No 13-bit bijective, bit-conserving LUT can reproduce the hex rule. Counterexample: state=1 (1 bit in, hex_state=4) maps to 0 output bits.

- **Hybrid engine (synchronous CA + LGCA) correctly projects 2D hex glider onto [111] plane (iter_252, sub 252.2b):** This is an algebraic identity by construction — the in-plane update is computed identically to the 2D case. Bit counts match exactly at every timestep. Decomposition test passes. The system is anisotropic (2.5D, not isotropic 3D) due to the privileged [111] plane.

- **Inter-plane coupling REFUTED (iter_252, sub 252.3, F4c):** For any coupling strength alpha>0, the glider dies immediately (0/10 survival for alpha=1,2,3). Coupling siphons center bits into outgoing inter-plane channels, destroying the cooperative survival pattern. At alpha=0, multi-layer seeds are independent per-layer composites (F4a).

## Confirmed (Prior, Recontextualized)

- **LUT-08 is a non-interacting composite (iter_248):** Extended — ALL O_h-symmetric single-cell collision rules (additive AND non-additive) produce only non-interacting composites. Now also confirmed: the 13-bit LGCA framework fundamentally cannot support cooperative survival.
- **2D hex v=0.469c sub-light glider (iter_222):** GENUINE, confirmed in iter_250, 251, 252. The ONLY confirmed mechanism for genuine multi-bit binding.
- **Complete fundamental 6-cycle single-bit spectrum (iter_248):** Still valid for 12-channel system.
- **Cooperative trapping with rest channel produces stationary oscillators (iter_251):** Still valid.

## Refuted

- **13-channel factorized LUT is simultaneously bijective, bit-conserving, and hex-compatible (iter_252, F3):** REFUTED. The hex rule changes Hamming weight on the 7-bit subspace. No bijective, bit-conserving LUT can match this. This is an algebraic impossibility.
- **Inter-plane coupling produces stable 3D bound states spanning 2+ planes (iter_252, F4c):** REFUTED. No stable configuration survives 300 steps for any alpha>0. The coupling destroys the cooperative survival pattern by siphoning center bits away from the [111] plane.
- **Multi-layer seeds under factorized embedding are genuine 3D bound states (iter_252, F4a):** REFUTED. At alpha=0, multi-layer seeds decompose into independent per-layer gliders (non-interacting composites).

## Architectural Conclusion

The single-cell LGCA collision operator (N-bit input -> N-bit bijective, bit-conserving output) is FUNDAMENTALLY INCOMPATIBLE with cooperative survival binding. This is proven across four successive phases:
- iter_248: All O_h-symmetric LUTs produce only non-interacting composites
- iter_250: Non-additive LUT variants also produce no genuine multi-bit gliders
- iter_251: 13-channel cooperative trapping produces only stationary oscillators
- iter_252: The proven 2D hex binding mechanism cannot be embedded into any bit-conserving LUT (F3), and coupling between bit-conserving and non-bit-conserving subsystems destroys the binding (F4c)

The root cause: cooperative survival requires weight-1->0 transitions (bits die when isolated), which violates the bit conservation axiom of the LGCA. This is a THEOREM, not a search limitation.

## In Progress

- None. The current research track (single-cell LGCA collision operators) is exhausted.

## Open Questions

1. Can a 3D SYNCHRONOUS CA on the FCC lattice (13-bit neighborhood -> 1-bit center output, NOT LGCA) produce cooperative survival binding? This generalizes the 2D hex CA architecture directly to 3D.
2. Can multi-site collision operators (reading neighbors' channels in addition to local state) reproduce cooperative survival within the LGCA framework?
3. Can bit conservation be relaxed for in-plane+center subsystems (with pre-registered justification from 2D hex precedent)?
4. Is O_h symmetry too restrictive? Would lower-symmetry groups enable cross-plane coupling?
5. Can the 2D hex binding mechanism be ported to a 3D hexagonal close-packed lattice?
6. Does the entire LGCA architecture need to be abandoned in favor of synchronous CA for 3D systems?
