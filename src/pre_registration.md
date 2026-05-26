# RDF Scientific Pre-Registration

*   **Iteration:** 251
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
A 3D FCC LGCA with 13 channels (12 propagation + 1 rest-mass channel) and a **cooperative
tapping** collision rule — where weight-1 prop states undergo Cartesian transposition to their
antiparallel partner (bit-conserving, bijective, O_h-invariant), weight-1 rest states map to
themselves (stationary fixed point), and weight-2+ states have non-additive mappings with
parametric freedom — produces at least one genuine, dynamically-bound multi-bit glider with
binding energy > 0. The rest channel provides the persistent local interaction that was
structurally absent in the 12-channel system (where every bit must propagate away each step,
making all interactions transient). By allowing bits to remain at a cell across multiple time
steps, the rest channel enables the neighborhood-overlap binding mechanism that is confirmed
to produce the genuine 2D hex v=0.469c glider. The 5 distinct O_h orbit types of weight-2
states (antiparallel, obtuse, perpendicular, acute, rest+prop) provide sufficient parametric
freedom for the cooperative trapping dynamics to produce stable propagating bound states.

**Critical constraint:** The rule MUST be bijective and bit-conserving. The original
"cooperative survival" (weight-1→0) violated both. Cooperative trapping replaces it with
a bit-conserving, bijective mechanism.

## 2. Falsification Criterion
F1: No multi-bit configuration survives ≥200 steps under any tested 13-channel cooperative
trapping rule variant (sweeping ~500 variants × 30 seeds × 300 steps) → cooperative
trapping infeasible in 3D FCC even with rest channel.
F2: All surviving propagating configurations fail the single-bit decomposition test (removing
any single bit does not alter the propagation trajectory or speed) → survivors are
non-interacting composites, rest channel insufficient for genuine binding.
F3: Any discovered glider fails O_h covariance under all 48 cuboctahedron rotations →
glider is an axis-aligned lattice artifact, not a physical particle.
F4: The 12-channel cooperative trapping control (Cartesian transposition weight-1, no rest
channel) produces genuine multi-bit gliders at the same rate as the 13-channel system → rest
channel is not the enabling factor for binding.
F5: Active Channel Mixing — the hypothesis is refuted if the rest-mass channel is either
statically occupied (always 1) or never occupied (always 0) during any discovered
glider's propagation cycle, or if there is zero transition of bits between the 12
propagation channels and the 13th rest channel. The rest-mass channel must actively
act as a dynamical mediator (exchanging momentum/state) during the propagation period.
Any one of F1–F5 being triggered refutes the hypothesis.

## 3. Proposed Method
Step 1 — Positive Control: Run the known 2D hex v=0.469c glider rule and seed for 500 steps.
Verify glider survival with binding energy > 0 and cooperative survival (weight-1→0) active.
This validates the search methodology against a known positive result.

Step 2 — FCC-13 Engine: Extend src/fcc_engine.py (or equivalent) from 12 to 13 channels.
Channel 13 is a rest-mass channel: invariant under O_h rotations, does not shift during
propagation. Collision maps 13-bit states to 13-bit states per cell. Create
src/fcc_engine_13ch.py.

Step 3 — O_h Orbit Classification: Classify all weight-2 states of the 13-channel system
into 5 O_h orbit types: (1) antiparallel prop pair, 6 states; (2) obtuse prop pair, 24
states; (3) perpendicular prop pair, 12 states; (4) acute prop pair, 24 states; (5) rest+prop
pair, 12 states. Create src/cooperative_lut_13ch.py.

Step 4 — LUT Parametrization: Fix weight-0→0 and weight-1 cooperative trapping (prop
weight-1 → antiparallel partner; rest weight-1 → itself). Weight-2 orbit mappings are
self-maps only (cross-orbit C↔E and B↔D mappings are mathematically impossible under O_h
due to non-conjugate stabilizer subgroups). F5 compliance must be achieved through
weight-3+ orbit pairings where rest-channel states map to non-rest-channel states and
vice versa. Weight-3+ uses simplified rules. Yields ~500 viable rule variants.

Step 5 — Parametric Search: For each rule variant, test 30 diverse seeds (2–5 bits,
adjacent and non-adjacent, multiple O_h directions) on L=24 FCC toroidal grid. Run 300 steps.
Score by sustained_displacement × bit_stability. Create src/search_13ch.py.

Step 6 — Coherence Protocol: Top 10 candidates → extended 1000-step run on L=32. Apply
Three-Test Coherence Protocol: (T1) single-bit decomposition test, (T2) interaction
coherence under latency perturbation, (T3) O_h covariance under all 48 rotations. Create
src/coherence_test_13ch.py.

Step 7 — Control Experiment: Repeat the search on 12-channel FCC with cooperative trapping
(no rest channel) using identical seeds and scoring. Compare genuine glider counts with
FCC-13 to isolate the effect of the rest channel.

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
