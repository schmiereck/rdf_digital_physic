# Current Research State
Phase: Phase 7.1 — Glider Taxonomy Complete

## Goal
Systematically search and classify stable sub-light glider species on the 3D FCC lattice, grouping them into unique O_h symmetry orbits and verifying stability over >=1000 steps.

## Confirmed
- **Smoke-Test Protocol & Transform Validation (iter_241.5):** Verified that the O_h symmetry orbit checker correctly identifies the LUT-08 reference glider as O_h-isomorphic to its canonical phase shapes, while random non-aligned seeds are correctly flagged as unstable or non-equivalent.
- **Uniqueness of LUT-08 Glider (iter_241.5):** Ran a controlled systematic sweep of weight-4 and weight-5 configurations on a 3D FCC grid under the conservative LUT-08 rule. No novel stable propagating gliders were found outside the O_h orbit of LUT-08, demonstrating the extreme isolation of LUT-08 within local configuration space.
- **Soliton Collision Cross-Sections (iter_239):** Collision of two sub-light gliders on a 2D hex lattice exhibits deterministic phase-dependent scattering and periodic annihilation matching the glider's period-6 internal cycle.

## Refuted
- **Taxonomic Inflation:** Discarded candidates matching any of the 48 octahedral transformations of the LUT-08 reference shape or its phase translations, eliminating redundant classifications.
- **Superluminal Speeds:** Normalized coordinate velocities against the diagonal light limit c = sqrt(2).

## Best Result
- Highly optimized, flat, and fully verified 3D FCC search engine script under 110 lines (`src/fcc_glider_search.py`) running with standard-library-only structures.

## In Progress / Planned
- Implement Phase 7.2 to analyze the internal charges/chirality of the LUT-08 glider and test additive conservation laws during multi-particle interactions.

## Open Questions
- What are the underlying conserved quantities (charges/chirality) that protect the LUT-08 glider from decay?
- Do other local, reversible O_h-symmetric 3D rules support a broader particle zoo (W > 12)?
