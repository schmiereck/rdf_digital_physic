# RDF Scientific Pre-Registration

*   **Iteration:** 245
*   **Pre-Registration File:** src/pre_registration.md

## CPT Operator Definitions

**Parity (P):** Spatial reflection in Cartesian space. Specifically, we invert the x-coordinate: (x,y,z) → (−x,y,z). On the lattice, this is implemented by converting (l,r,c) → Cartesian via BT_inv, negating x, then converting back via BT. This produces the enantiomeric glider with opposite chirality (χ → −χ). The P operator does NOT change the channel assignments of the glider bits.

**Charge Conjugation (C):** On this lattice, "charge" is chirality (the signed 4-volume of the glider's bit positions in Cartesian space). C maps a particle to its enantiomer, which is identical to P on this lattice because chirality is the only discrete charge. C is NOT bitwise inversion (0↔1); bitwise inversion would destroy the glider structure and is not a symmetry of the rule.

**Time Reversal (T):** Running the CA backward: streaming in reverse and applying the inverse LUT. The T-reversed glider propagates in the opposite direction under the inverse rule.

**CPT = C·P·T:** On our lattice, since C≡P, CPT ≡ P²·T = T (since P²=identity for a single reflection). The CPT-conjugate of the LUT-08 glider requires the inverse rule to propagate stably, and is NOT the appropriate object for forward-rule collision experiments.

**For forward-rule collision experiments, the "antiparticle" is defined as the P-reflected (enantiomeric) glider, which is stable under the forward rule by O_h symmetry.**

## 1. Hypothesis
The CPT-conjugate of the LUT-08 sub-light glider (obtained by spatial reflection
of its 4-bit pattern, yielding opposite chirality and reversed velocity) is a
stable, bit-conserving sub-light glider under the forward LUT-08 rule. When a
LUT-08 particle and its CPT-antiparticle undergo head-on collision, they
annihilate cleanly (≤2 residual non-propagating bits, total bit count conserved
at 8), producing exclusively v=1c single-bit propagating states. This outcome
qualitatively differs from same-chirality particle-particle collisions, which
scatter elastically (as established in iter_242).

## 2. Falsification Criterion
The hypothesis is refuted if ANY of the following hold:
1. The CPT-conjugate glider is not bit-conserving during solo propagation
   over ≥80 steps (bit count deviates from 4 at any step).
2. In ≥3 out of 5 head-on particle-antiparticle collision configurations,
   the residual non-propagating bit count exceeds 2 after the interaction
   completes (i.e., annihilation is not "clean").
3. Particle-antiparticle collisions show the same elastic-scattering outcome
   as particle-particle collisions (no qualitative matter-antimatter
   distinction), with both gliders emerging intact post-collision.
4. The collision outcome is not O_h-covariant: rotating the collision axis
   through one O_h symmetry element changes the outcome from annihilation
   to elastic scattering, indicating a lattice-axis artifact rather than
   genuine physics.

## 3. Proposed Method
Step 1: Construct CPT-antiparticle pattern.
  - Load the LUT-08 glider JSON from iter_224 archive.
  - Apply spatial reflection (invert one Cartesian coordinate) to obtain
    the enantiomeric 4-bit pattern. This is the CPT-conjugate seed.
  - Place it with velocity directed toward the original glider's approach path.

Step 2: Verify CPT-conjugate solo stability (CONTROL A).
  - Run the reflected glider alone on a 32³ FCC grid for 80 steps under
    the forward LUT-08 rule.
  - Measure: bit count at each step, center-of-mass velocity, chirality
    sequence. Must be 4 bits throughout, sub-light velocity, opposite
    chirality to the original.

Step 3: Run particle-particle elastic collision (CONTROL B — replicate iter_242).
  - Place two SAME-chirality LUT-08 gliders on head-on collision course.
  - Run for 80+ steps. Confirm elastic scattering (both gliders emerge
    intact). This validates the platform against known results.

Step 4: Run particle-antiparticle head-on collisions (EXPERIMENT).
  - 5 collision configurations with different impact parameters (offset
    distances 0, 1, 2, 3, 4 lattice units perpendicular to collision axis).
  - For each: place LUT-08 particle and CPT-antiparticle on head-on course
    on a 32³ grid. Run for 80+ steps.
  - Measure at each step: total bit count, chirality sum, number of
    propagating v=1c single-bit states, number of residual non-propagating
    bits, sub-lattice occupancy.

Step 5: O_h covariance test.
  - Take the collision configuration that shows the strongest annihilation
    signal (if any). Rotate the collision axis through one non-trivial
    O_h element (e.g., swap two Cartesian axes). Re-run.
  - If the outcome changes qualitatively (annihilation → elastic), the
    effect is a lattice-axis artifact and the hypothesis is refuted.

Step 6: Analyze and report.
  - Compare particle-antiparticle outcomes against particle-particle control.
  - If annihilation is observed: characterize products (bit count, velocity,
    chirality of products). Check total chirality = 0 (particle+antiparticle
    have equal and opposite chirality, so sum should be 0 before and after).
  - If no annihilation (elastic scattering): document as null result. The
    enantiomeric glider is still an "antiparticle" in the CPT sense, but
    annihilation is not among its physical consequences on this lattice.

Files to create/modify:
- src/phase7_3_antiparticle.py: main experiment script (construct CPT-conjugate,
  run solo stability, run collisions, run O_h test)
- src/pre_registration.md: this plan document
- src/phase7_3_analysis.py: post-processing and comparison against controls

Key parameters (declared in advance):
- Grid: 32³ FCC (sufficient per iter_232 Cavendish test precedent)
- Steps: 80 per run
- Impact parameters: 0, 1, 2, 3, 4 lattice units
- Clean annihilation threshold: ≤2 residual non-propagating bits
- O_h test: one non-trivial rotation (axis swap)

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
