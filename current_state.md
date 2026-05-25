# Current Research State
Phase: Phase 7.3 — Antiparticles & CPT Symmetries (Null Result)

## Goal
Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.

## Confirmed
- **Chirality and Z2 Enantiomorphism (iter_242):** LUT-08 has chiral charge alternating between -4.0 (even) and +2.0 (odd). Spatial reflection negates chirality.
- **100% Elastic Collisions & Additive Conservation (iter_242):** 10/10 opposite-chirality collisions conserve bit count, chirality sum, and sub-lattice parities.
- **Antiparticle (P-reflected enantiomer) exists and is stable (iter_245):** The x-reflected LUT-08 glider propagates stably under the forward LUT-08 rule with opposite chirality (constructional result guaranteed by O_h symmetry).
- **Opposite-chirality collisions are perfectly elastic (iter_245):** 5/5 impact-parameter configurations between LUT-08 and its P-reflected antiparticle produce elastic scattering (both gliders emerge intact, 0 residual debris).
- **Same-chirality collisions are destructive (iter_245, with caveat):** 5/5 same-chirality collision configurations produce Partial (3/5) or Chaotic (2/5) outcomes. Caveat: the same-chirality "reversed-velocity" glider (pC) has only approximately opposite velocity; no O_h proper rotation exactly reverses the LUT-08 velocity direction.

## Refuted
- **Annihilation hypothesis (iter_245):** REFUTED. Opposite-chirality (particle-antiparticle) collisions do NOT annihilate; they scatter elastically. The P-reflected enantiomer exists but does not exhibit matter-antimatter annihilation behavior on this lattice.
- **O_h covariance of collision dynamics (iter_245):** REFUTED. Rotating the collision setup through a proper O_h element changes the outcome from Elastic to Chaotic. This may be a toroidal boundary artifact (needs verification on larger grid with open boundaries).

## Best Result
- **Complete CPT experiment (iter_245):** 112-line script testing antiparticle stability, 5 opposite-chirality collisions, 5 same-chirality collisions, and O_h covariance. Clean null result on annihilation with precise falsification evaluation.
- **CPT Operator Definitions (iter_245):** Precise mathematical definitions of P, C, T, and CPT on the discrete FCC lattice documented in `src/pre_registration.md`.

## In Progress / Planned
- O_h non-covariance needs verification on larger grid (L=64+) with open boundaries to distinguish boundary artifact from genuine physics failure.
- Phase 7.4 (Pair Production & Annihilation): The original goal was to demonstrate high-energy collisions producing new particle pairs. Given the Phase 7.3 null result (no annihilation), Phase 7.4 may need to be re-scoped to focus on whether pair production can occur from kinetic energy input even without an annihilation channel.

## Open Questions
1. Is the O_h non-covariance a genuine physics effect or a toroidal boundary artifact? (Test on L=64+)
2. Can a perfectly head-on same-chirality collision be achieved with a glider whose velocity aligns with an O_h axis?
3. Do other FCC glider species show annihilation with their enantiomers?
4. Is the elastic-opposite / destructive-same asymmetry a general O_h-symmetric CA feature or LUT-08 specific?
5. Can annihilation be achieved with anti-phase-aligned collision geometries?
6. What is the broader particle zoo beyond LUT-08? (W > 12 searches)
