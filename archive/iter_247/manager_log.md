# Research Manager Log - Iteration 247

## Iteration 247 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
Same-chirality LUT-08 collisions produce debris from which at least one
stable propagating glider species (distinct from LUT-08 in bit-count,
period, or velocity) emerges within 200 steps post-collision, demonstrating
that collision kinetic energy can be converted into the rest mass of new
particle species. Specifically: among the 5 same-chirality impact-parameter
configurations tested in iter_245, at least one will yield debris containing
a propagating glider with bit-count ≠ 8 or velocity ≠ LUT-08's velocity,
detectable by automated cluster-tracking and periodicity analysis on an L=64
grid over 300 steps.

**Proposed Falsification Criterion:**
The hypothesis is REFUTED if ANY of the following hold:
F1: No stable propagating patterns (periodic-displacement bit clusters)
    detected in collision debris across all 5 same-chirality impact
    parameters after 200 steps post-collision settling time.
F2: All detected propagating patterns are LUT-08 gliders (8-bit,
    same velocity and period as original) — indicating inelastic
    scattering without new species production.
F3: All stable debris objects are stationary (oscillators/still-lifes)
    with zero net displacement — debris, not pair production.
F4: The pair production (if any) is not robust to ±1 lattice-unit
    impact-parameter variation — indicating a narrow geometric
    artifact rather than a physical process.

**Proposed Method:**
Step 1: Create src/experiment_247_pair_production.py that implements:
  a) Same-chirality LUT-08 collision setup on L=64 FCC grid
     (reusing iter_245/246 infrastructure), placing two LUT-08
     gliders of identical chirality on a head-on or offset collision
     course with 5 different impact parameters (0, ±1, ±2 lattice
     units transverse offset).
  b) Each collision runs for 300 steps on L=64 with periodic boundaries.
  c) Automated debris analysis starting at step 60 (post-collision):
     - Every 10 steps, identify connected bit clusters (6-connectivity)
     - Track each cluster's center-of-mass over 40-step windows
     - Classify clusters by: bit-count, average displacement per period,
       periodicity (autocorrelation of cluster shape), velocity
     - Flag as "propagating glider" if: periodic displacement ≥ 2 cells
       over ≥ 2 periods with <20% velocity variance
  d) Compare detected gliders against LUT-08 signature (8-bit,
     v≈0.5 cells/tick, period ≈ 8 steps).
  e) Any detected glider with different bit-count OR different velocity
     is a "new species" — evidence for pair production.

Step 2: Run vacuum control — single LUT-08 glider on same grid for
300 steps, confirm no spontaneous debris gliders appear.

Step 3: Run 3 additional impact parameters (±3, ±4, ±5 transverse
offset) to test F4 robustness. If pair production only occurs at one
narrow impact parameter, it fails F4.

Step 4: For any new glider species discovered, run a 200-step
stability test (solo propagation on clean grid) to confirm it is
a genuine stable particle, not a transient debris pattern.

Step 5: Compile results table: for each collision config, report
(impact_param, debris_bit_count, n_stationary_objects,
n_propagating_glider, glider_species_if_any, is_LUT_08,
robustness_to_±1_variation).

Files to create/modify:
- src/experiment_247_pair_production.py (main experiment, ~200 lines)
- src/pre_registration.md (this plan)

Expected outputs:
- Collision debris analysis for 8 impact parameters (5 original + 3 extended)
- Vacuum control result
- Stability verification for any candidate new species
- Verdict: SUPPORTED (new species found, robust), INCONCLUSIVE (new species
  found but F4-fails), or REFUTED (F1/F2/F3 triggered)

---

## Iteration 247 -> Planner [Strategic Guidance]

### Strategic Guidance – Manager's Note

While the proposed exploration of same-chirality collision debris (Phase 7.4) is a logical step, the current draft plan contains a significant loophole that could lead to misidentifying simple scattering or transient debris as "pair production." 

To maintain strict scientific rigour, you must refine your experimental design and pre-registration criteria to address the following three points:

---

### 1. The $O_h$-Equivalence Filter (Preventing Taxonomic Inflation)
A deflected, rotated, or phase-shifted counterpart of the incoming gliders is **not** a new particle species; it is simply inelastic or elastic scattering of the existing species. 
* **The Loophole:** Since the $O_h$ symmetry group has 48 elements, the LUT-08 glider has multiple symmetric variants propagating along different axes with different phase alignments. If your collision debris contains an 8-bit glider propagating along a different direction, your current F2 criterion (`velocity ≠ original`) might falsely classify it as a "new species."
* **The Mandate:** You must explicitly define the $O_h$ equivalence orbit of LUT-08 (its 48 possible spatial orientations, velocity vectors, and cyclic permutations). Any candidate glider found in the debris whose velocity and period match *any* member of the LUT-08 $O_h$ orbit must be classified as a scattered/deflected LUT-08, **not** as a newly produced species.

### 2. Rigorous Vacuum Isolation & Stability (The 300-Step Test)
Debris patterns in discrete CA often exhibit meta-stability—behaving periodically for 50 to 100 steps before suddenly collapsing, dispersing, or emitting a bit that changes their identity.
* **The Mandate:** To be registered as a stable emergent particle, any candidate pattern extracted from the debris must be isolated on a completely clean, vacuum grid and simulated for a minimum of **300 steps**. 
* **Falsification Criteria:** The candidate is refuted as a stable species if, during this 300-step vacuum run, it exhibits any change in total bit count, any monotonic drift in average velocity, or any breakdown of its periodic cycle.

### 3. Pre-Registration Mandate
The Orchestrator will automatically write and commit your finalized hypothesis and falsification criteria to `src/pre_registration.md` before execution begins.
* You must update your plan to include the $O_h$-equivalence check and the 300-step isolation test directly in your pre-registration formulation.
* Ensure all execution sub-agents explicitly load and read `src/pre_registration.md` to ensure complete alignment with these quantitative bounds.

---

**Proceed with Phase 7.4 after updating your pre-registration plan to reflect these rigorous controls.**

---

