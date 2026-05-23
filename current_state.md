# Current Research State
Phase: Phase 7.2 — Charge & Chirality Analogs Complete

## Goal
Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid. Phase 7.2 specifically analyzed the internal charges and chirality of the stable LUT-08 sub-light glider on the 3D FCC lattice, and tested additive conservation laws.

## Confirmed
- **Chirality and Z2 Enantiomorphism (iter_242):** Reconstructed the precise projection matrices mapping grid coordinate offsets to physical Cartesian FCC nearest-neighbor vectors. Proved that the 4-bit sub-light glider LUT-08 possesses a chiral charge \(\chi(t)\) which alternates between \(-4.0\) (even steps) and \(+2.0\) (odd steps), displaying a phase-translation periodicity of 2 steps. Spatial reflection (\(x \to -x\)) negates this charge, confirming a pair of enantiomers.
- **Sub-lattice Charge and Cyclic Permutations (iter_242):** Showed that the sub-lattice occupancy vector \(\mathbf{q}(t)\) alternates between \((0, 1, 1, 2)\) (even steps) and \((2, 1, 1, 0)\) (odd steps). The transition is governed by a permutation vector swapping simple cubic sub-lattices.
- **100% Elastic Collisions & Additive Conservation (iter_242):** Evaluated 10 distinct collision configurations of two gliders. In all 10 runs, the gliders collide, interact locally, and emerge intact. Total bit count, chirality sum, and asymptotic sub-lattice parities are perfectly conserved, establishing them as genuine conserved charges.

## Refuted
- **Charge Mixing:** Refuted the concern that sub-lattice charges or chiralities are mixed uncontrollably during interactions; they display periodic phase dynamics in vacuum and are perfectly conserved asymptotically in collisions.

## Best Result
- **Complete Conservation Verification Pipeline (iter_242):** Python scripts (`src/glider_charge_analysis.py` and `src/glider_collision_charge_analysis.py`) demonstrating Z2 enantiomorphism and 100% elastic collision conservation on the 3D FCC grid.

## In Progress / Planned
- Prepare for Phase 7.3 to construct and characterize time-reversed counterparts of the LUT-08 gliders (antiparticles), verify CPT-like symmetries, and demonstrate clean particle-antiparticle annihilation.

## Open Questions
- What is the CPT-reversed counterpart of the LUT-08 sub-light glider?
- Do other 3D O_h-symmetric rules support a broader particle zoo (W > 12)?
