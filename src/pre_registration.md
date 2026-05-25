# RDF Scientific Pre-Registration

*   **Iteration:** 247
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
Same-chirality LUT-08 collisions produce debris from which at least one
stable propagating glider species (distinct from LUT-08 in bit-count,
period, or velocity) emerges within 200 steps post-collision, demonstrating
that collision kinetic energy can be converted into the rest mass of new
particle species. Specifically: among the 9 same-chirality impact-parameter
configurations tested in iter_247, at least one will yield debris containing
a propagating glider with bit-count ≠ 4 or velocity ≠ LUT-08's velocity,
detectable by automated cluster-tracking and periodicity analysis on an L=64
grid over 300 steps.

## 2. Falsification Criterion
The hypothesis is REFUTED if ANY of the following hold:
F1: No stable propagating patterns (periodic-displacement bit clusters)
    detected in collision debris across all 9 same-chirality impact
    parameters after 200 steps post-collision settling time.
F2: All detected propagating patterns are LUT-08 gliders (4-bit,
    same velocity and period as original) — indicating inelastic
    scattering without new species production.
F3: All stable debris objects are stationary (oscillators/still-lifes)
    with zero net displacement — debris, not pair production.
F4: The pair production (if any) is not robust to ±1 lattice-unit
    impact-parameter variation — indicating a narrow geometric
    artifact rather than a physical process.

## 3. O_h-Equivalence Filter
Any 4-bit propagating cluster whose velocity matches any of the 48 O_h-rotated
LUT-08 velocities (within 0.3 cells/tick) AND whose period is 2 (±1 step) is
classified as "LUT-08_scattered", NOT a new species.

## 4. 300-Step Vacuum Isolation Test
Any candidate not matching LUT-08's orbit must survive 300 steps alone on a
clean L=64 grid with constant bit count, stable velocity, and maintained
periodicity.

## 5. Pre-Registration Compliance
This experiment adheres to the pre-registered protocol. Any deviation from
the planned analysis will be explicitly documented in the results file with
justification.

## 6. Proposed Method
Step 1: Create src/experiment_247_pair_production.py that implements:
  a) Same-chirality LUT-08 collision setup on L=64 FCC grid
     (reusing iter_245/246 infrastructure), placing two LUT-08
     gliders of identical chirality on a head-on or offset collision
     course with 9 different impact parameters (dy = 0, ±1, ±2, ±3, ±4).
  b) Each collision runs for 300 steps on L=64 with periodic boundaries.
  c) Automated debris analysis starting at step 60 (post-collision):
     - Every 10 steps, identify connected bit clusters (toroidal Manhattan
       distance ≤ 4)
     - Track each cluster's center-of-mass over 40-step windows
     - Classify clusters by: bit-count, average displacement per period,
       periodicity (autocorrelation of cluster shape), velocity
     - Flag as "propagating glider" if: periodic displacement ≥ 2 cells
       over ≥ 2 periods with <20% velocity variance
  d) Compare detected gliders against LUT-08 signature (4-bit,
     v≈[0.5,0.0,1.0] cells/tick, period ≈ 2 steps) using the O_h-Equivalence
     Filter.
  e) Any detected glider failing the O_h filter is a "new species" —
     evidence for pair production.

Step 2: Run vacuum control — single LUT-08 glider on same grid for
300 steps, confirm no spontaneous debris gliders appear.

Step 3: For any new glider species discovered, run a 300-step
stability test (solo propagation on clean grid) to confirm it is
a genuine stable particle, not a transient debris pattern.

Step 4: Compile results table: for each collision config, report
(impact_param, debris_bit_count, n_stationary_objects,
n_propagating_glider, glider_species_if_any, is_LUT_08,
robustness_to_±1_variation).

Files to create/modify:
- src/experiment_247_pair_production.py (main experiment, ~200 lines)
- src/pre_registration.md (this plan)

Expected outputs:
- Collision debris analysis for 9 impact parameters
- Vacuum control result
- Stability verification for any candidate new species
- Verdict: SUPPORTED (new species found, robust), INCONCLUSIVE (new species
  found but F4-fails), or REFUTED (F1/F2/F3 triggered)

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
