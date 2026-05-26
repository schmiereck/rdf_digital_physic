# RDF Scientific Pre-Registration

*   **Iteration:** 250
*   **Pre-Registration File:** src/pre_registration.md

## 0. Top Priority Directive
The 2D Hex Decomposition Check (Experiment 250) is the ABSOLUTE PRIORITY for this iteration. No 3D FCC non-additive LUT construction may proceed until a definitive verdict is reached on whether the 2D hex v=0.469c sub-light glider from iter_222 is a genuinely bound multi-bit particle or a non-interacting composite. This check is prerequisite to all Phase 250+ 3D FCC work.

## 1. Hypothesis
A bijective, bit-conserving LUT for the 12-channel FCC lattice, constructed by
introducing non-additive weight-2 mappings (where at least one weight-2 input
state maps to an output different from the independent sum of its weight-1
component transitions), can support at least one genuine dynamically-bound
multi-bit glider with binding energy > 0 that survives ≥200 propagation steps.

Specifically: starting from LUT-08's weight-1 sub-table (6 period-2
transpositions: ch0↔ch3, ch1↔ch2, ch4↔ch7, ch5↔ch6, ch8↔ch11, ch9↔ch10),
we replace the additive weight-2 sub-table with a non-additive permutation
of the 66 weight-2 states. When seeded with ≥2 bits in the same cell, at
least one such LUT variant will produce a stable propagating pattern where
the bits maintain correlated trajectories (binding energy > 0, verified by
Single-Bit Decomposition Test).

## 2. Falsification Criterion
F1 (Construction Impossibility): Refuted if no bijective, bit-conserving
non-additive weight-2 permutation can be constructed from LUT-08's weight-1
sub-table while maintaining O_h symmetry.

F2 (No Stable Structures): Refuted if ALL non-additive LUT variants produce
only chaotic (bit explosion >3x initial) or frozen (zero displacement after
step 50) dynamics from every multi-bit seed with ≥2 bits in the same cell,
with no structure surviving 200 steps.

F3 (Composite Only): Refuted if any stable propagating multi-bit structure
found under a non-additive LUT fails the Single-Bit Decomposition Test —
i.e., removing any single bit from the glider leaves the remaining bits'
propagation trajectory and speed unchanged, proving binding energy = 0.

F4 (O_h Non-Covariance): For O_h-symmetric LUT variants, refuted if any
found glider fails to transform covariantly under all 48 elements of O_h
(the glider's velocity and internal structure must rotate consistently).

F5 (2D Hex Null Result): If the 2D hex v=0.469c glider from iter_222 is
found to be a non-interacting composite (binding energy = 0), this is
consistent with the hypothesis that monospecificity is a general property
of synchronous LGCA with single-cell collisions, and does not refute the
3D FCC construction program. However, if the 2D hex glider IS genuine
(binding energy > 0), this provides evidence for the existence of
non-additive coherence mechanisms that the 3D FCC program must replicate.

## 3. O_h Symmetry Constraint
O_h symmetry is a non-negotiable physical constraint for all 3D FCC LUT
variants. The lattice symmetry must be respected by the transition rules.
No relaxation of O_h symmetry is permitted. All non-additive constructions
must preserve the full O_h point group covariance.

## 4. Proposed Method
EXPERIMENT 250: 2D Hex Decomposition Check (MANDATORY FIRST STEP)

Step 1: Load the iter_222 v=0.469c sub-light glider from the 2D hex grid.
Step 2: Extract individual bits and test if they propagate independently.
Step 3: Test all 2-bit subsets for interaction effects.
Step 4: Compare full glider against logical OR superposition of single-bit runs.
Step 5: Determine binding energy verdict:
  - If any individual bit ANNIHILATES when run alone but survives in the
    full glider → binding energy > 0, GENUINE GLIDER
  - If all individual bits survive alone with the same velocity as the full
    glider AND the full glider matches the OR superposition → non-interacting
    composite, binding energy = 0
  - If bits survive alone but with DIFFERENT velocity/trajectory than in the
    full glider → binding energy > 0, genuine coherence
  - If the full glider differs from OR superposition at some steps →
    interaction exists (need to determine if constructive binding or
    transient perturbation)

Step 6: If the 2D hex glider is genuine, analyze the precise mathematical
mechanism that allows 2D hexagonal single-cell collisions to support binding
where the 3D FCC single-cell collisions failed.

Step 7: If the 2D hex glider is also a non-interacting composite, document
this as a foundational null result. This would be consistent with the
hypothesis that monospecificity is a general LGCA/synchronous-CA property,
not just an FCC artifact.

Files to create/modify:
- src/experiment_250_hex_decomposition.py: 2D hex decomposition check
- src/pre_registration.md: Pre-registration document (this file)
- archive/iter_250/results/hex_decomposition.json: Experimental results

---
*Updated by Research Manager for Phase 250 execution.*
