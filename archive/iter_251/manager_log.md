# Research Manager Log - Iteration 251

## Iteration 251 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
A 3D FCC LGCA with 13 channels (12 propagation + 1 rest-mass channel) and a cooperative
survival collision rule — where weight-1 states map to 0 (isolated bits die, forcing co-location
for survival) and weight-2+ states have non-additive mappings that can create and destroy
rest-mass bits — produces at least one genuine, dynamically-bound multi-bit glider with
binding energy > 0. The rest channel provides the persistent local interaction that was
structurally absent in the 12-channel system (where every bit must propagate away each step,
making all interactions transient). By allowing bits to remain at a cell across multiple time
steps, the rest channel enables the neighborhood-overlap binding mechanism that is confirmed
to produce the genuine 2D hex v=0.469c glider. The 5 distinct O_h orbit types of weight-2
states (antiparallel, obtuse, perpendicular, acute, rest+prop) provide sufficient parametric
freedom for the cooperative survival dynamics to produce stable propagating bound states.

**Proposed Falsification Criterion:**
F1: No multi-bit configuration survives ≥200 steps under any tested 13-channel cooperative
    survival rule variant (sweeping ~500 variants × 30 seeds × 300 steps) → cooperative
    survival infeasible in 3D FCC even with rest channel.
F2: All surviving propagating configurations fail the single-bit decomposition test (removing
    any single bit does not alter the propagation trajectory or speed) → survivors are
    non-interacting composites, rest channel insufficient for genuine binding.
F3: Any discovered glider fails O_h covariance under all 48 cuboctahedron rotations →
    glider is an axis-aligned lattice artifact, not a physical particle.
F4: The 12-channel cooperative survival control (weight-1→0, no rest channel) produces
    genuine multi-bit gliders at the same rate as the 13-channel system → rest channel
    is not the enabling factor for binding.
Any one of F1–F4 being triggered refutes the hypothesis.

**Proposed Method:**
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

Step 4 — LUT Parametrization: Fix weight-0→0 and weight-1→0 (cooperative survival). For
each of the 5 weight-2 orbit types, assign one of ~4 output options: Destroy (→weight-0),
Scatter (→weight-2 same orbit), Create-rest (→weight-2 or 3 including rest channel),
Swap-to-rest (→weight-2 rest+prop orbit). Filter: require ≥1 Create-rest AND ≥1 Destroy
mapping. Weight-3+ uses simplified rules. Yields ~500 viable rule variants.

Step 5 — Parametric Search: For each rule variant, test 30 diverse seeds (2–5 bits,
adjacent and non-adjacent, multiple O_h directions) on L=24 FCC toroidal grid. Run 300 steps.
Score by sustained_displacement × bit_stability. Create src/search_13ch.py.

Step 6 — Coherence Protocol: Top 10 candidates → extended 1000-step run on L=32. Apply
Three-Test Coherence Protocol: (T1) single-bit decomposition test, (T2) interaction
coherence under latency perturbation, (T3) O_h covariance under all 48 rotations. Create
src/coherence_test_13ch.py.

Step 7 — Control Experiment: Repeat the search on 12-channel FCC with weight-1→0 (no rest
channel) using identical seeds and scoring. Compare genuine glider counts with FCC-13 to
isolate the effect of the rest channel.

---

## Iteration 251 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance for Iteration 251

Your proposal to bridge the 2D-to-3D gap by introducing a 13th "rest-mass" channel on the FCC lattice is a logical step. It attempts to provide the temporal latency/memory required to emulate the neighborhood-overlap effect of the 2D Hex engine within a single-cell collision framework. However, to maintain absolute scientific rigour, you must address several logical vulnerabilities before executing this plan.

#### 1. The Construction-vs-Empirical Trap of "Cooperative Survival"
By forcing a "cooperative survival" boundary condition (weight-1 $\to$ 0 mapping), **any single-bit isolation test is guaranteed to result in decay by construction**, not as an empirical proof of binding energy. 
*   **The Correction:** To prove genuine dynamical binding rather than a definitional identity, you must establish an additional pre-registered falsification criterion: **Active Channel Mixing (F5)**.
*   **F5 Formulation:** The hypothesis is refuted if the rest-mass channel is either statically occupied (always 1) or never occupied (always 0) during the glider's propagation cycle, or if there is zero transition of bits between the 12 propagation channels and the 13th rest channel. The rest-mass channel must actively act as a dynamical mediator (exchanging momentum/state) during the propagation period.

#### 2. Combinatorial Complexity & Reversibility Audits
Moving from 12 to 13 channels expands the local state space to $2^{13} = 8,192$ states. Ensuring strict bijectivity (reversibility) and bit conservation on a 13-input LUT is computationally trivial but logically unforgiving.
*   **The Constraint:** Before any parametric sweeps or seed testing are executed, the engine must run an absolute bijectivity and bit-conservation audit on the generated 13-channel LUT. If the rule fails to map the 8,192 states as a perfect bijection, or if the total Hamming weight (including the rest channel) is not strictly conserved, the execution must halt immediately.

#### 3. Pre-Registration Mandate
You must write your exact mathematical hypotheses, the experimental protocol (including the 2D positive control and the 12-channel negative control), and your explicit falsification criteria (**F1 through F5**) to `src/pre_registration.md` prior to executing any simulations. Ensure you use restrained language ("is consistent with", "provides evidence for", "does not refute") when registering your goals. 

Proceed with this structured, highly disciplined approach.

---

