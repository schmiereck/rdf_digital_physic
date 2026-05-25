# Research Manager Log - Iteration 249

## Iteration 249 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
An O_h-symmetric, reversible, bit-conserving FCC LGCA LUT with deliberately
constructed non-additive weight-2 entries — where the output for a weight-2
input state {ch_i, ch_j} is NOT the independent superposition of the two
weight-1 transpositions τ(i) and τ(j), but instead redirects one or both
output bits into channels belonging to a different transposition pair — admits
genuine multi-bit coherent gliders. Specifically, when two single-bit period-2
particles from different velocity cycles collide at the same cell, the
non-additive weight-2 interaction scatters them into channels that create a
stable two-bit bound state where both bits periodically co-locate at the same
lattice cell, and the state cannot be decomposed into independent single-bit
particles (fails the three-test coherence protocol from iter_248).

**Proposed Falsification Criterion:**
The hypothesis is refuted if ALL of the following hold simultaneously:
F1: Across all non-additive LUT variants tested (≥3 distinct interaction types:
    exchange, binding, scattering) and all O_h-distinct two-bit collision
    geometries (≥6 initial configurations per variant), no two-bit bound
    state survives ≥200 steps post-collision. All debris either separates
    into independent single-bit particles or thermalizes.
F2: Any two-bit candidate that does survive 200 steps passes the single-bit
    decomposition test (i.e., running each bit independently reproduces the
    multi-bit trajectory), proving it is still a non-interacting composite.
F3: Any bound state that passes F2 exists only along one lattice axis and
    disappears when initial conditions are rotated through O_h symmetry
    elements (proving it is a lattice-axis artifact, not genuine physics).
If ANY genuine multi-bit glider is found that: (a) survives ≥200 steps,
(b) fails the decomposition test (bits are interdependent), (c) is
destabilized by single-bit removal, and (d) transforms covariantly under
O_h rotations, then the hypothesis is confirmed.

**Proposed Method:**
SUB-GOAL A: Construct non-additive LUT variants
1. Enumerate all C(12,2)=66 weight-2 channel pairs on the FCC cuboctahedron.
2. Group into O_h orbits (expected: 3-5 orbits based on geometric relationship:
   adjacent, non-adjacent non-antipodal, antipodal).
3. For each orbit, identify the additive LUT-08 output (superposition of
   independent weight-1 transpositions).
4. Construct 3+ non-additive variants using orbit-pair output swaps:
   - LUT-INT-EXCHANGE: swap one output channel between two weight-2 orbits,
     creating cross-cycle leakage.
   - LUT-INT-BINDING: redirect weight-2 outputs so both bits enter the
     SAME velocity cycle (co-propagation tendency).
   - LUT-INT-SCATTERING: redirect weight-2 outputs to slow/stationary
     cycles, creating energy-like dissipation at collision sites.
5. For each variant, close modifications under full O_h group (48 elements).
6. Verify each variant is a valid permutation (reversible) and bit-conserving.
7. Document the exact channel-pair modifications and the physical reasoning
   for each interaction type BEFORE running any dynamics.

Files: src/lut_construction_nonadditive.py (new), modifying or extending
       the existing generate_symmetric_lut() logic.

SUB-GOAL B: Systematic collision search for genuine multi-bit gliders
1. For each non-additive LUT variant, set up all O_h-distinct two-bit
   collision initial conditions (two single-bit particles from different
   velocity cycles on collision courses on an L=64 grid).
2. Propagate each collision for 200+ steps.
3. Track all coherent multi-bit structures using the automated detection
   from iter_248 (CoM tracking, bit-cluster identification).
4. Apply the three-test coherence protocol to any candidate surviving
   ≥50 steps:
   Test A (decomposition): Run each bit independently; check if combined
   trajectory matches multi-bit trajectory. FAIL = genuine.
   Test B (bit-removal): Remove one bit from initial conditions; check
   if remaining pattern is destabilized. YES = genuine.
   Test C (collision interaction): Collide candidate with a test particle;
   check for non-trivial outcome. YES = genuine.
5. For any genuine glider, measure: bit count, period, velocity vector,
   and whether bits share a cell during propagation.

Files: src/experiment_249_interacting_lut.py (new),
       src/coherence_testing.py (new or extended from iter_248 code).

SUB-GOAL C: O_h covariance and control verification
1. For any genuine coherent glider found, rotate initial conditions
   through all 48 O_h elements. Verify the glider exists and moves
   in the expected rotated direction.
2. Run the identical collision search on the original (additive) LUT-08
   as control. Confirm null result (reproduces iter_248 finding).
3. Compare: any gliders found with non-additive LUTs that do NOT exist
   with additive LUT-08 constitute evidence for the hypothesis.

Files: Integrated into src/experiment_249_interacting_lut.py.

SUB-GOAL D (secondary): Check 2D hex glider coherence
1. Apply the same single-bit decomposition test to the 2D hex v=0.469c
   glider (champion_rule_perfect.json from iter_222).
2. If it also decomposes, the monospecific spectrum is a general feature
   of additive LGCA constructions across lattice types.
3. If it does NOT decompose, the 2D hex lattice or rule construction
   has a fundamental advantage that should be understood and ported.

Files: src/check_hex_glider_coherence.py (new), using existing 2D hex engine.

---

## Iteration 249 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance for Iteration 249

The realization from Iteration 248—that our 3D gliders are non-interacting composites due to the additive nature of the single-cell collision step—is a major step forward. Your proposal to introduce **non-additive weight-2 entries** to the 3D FCC LUT is the logical next step to see if true, emergent bound states can exist. However, the plan as proposed contains a critical logical flaw and requires tightening to prevent "post-hoc tuning" of interactions.

#### 1. Logical Gate in Falsification Criteria (Critical Correction)
Your draft plan states that the hypothesis is refuted if *"ALL of the following hold simultaneously: F1, F2, and F3"*. **This is a dangerous logical error.** 
If you find a state that survives 200 steps (violating F1) but it is shown to be a trivial non-interacting composite (satisfying F2), your current AND-gate would prevent the hypothesis from being refuted! 
*   **Correction:** The falsification gate must be an **OR-gate**. Your hypothesis of "genuine multi-bit coherent gliders" is **refuted** if:
    *   **F1:** No multi-bit configurations survive $\ge 200$ steps post-collision under any non-additive LUT variant, **OR**
    *   **F2:** Any surviving state *passes* the single-bit decomposition test (proving it is still a non-interacting composite), **OR**
    *   **F3:** Any surviving state is a lattice-axis artifact (fails to transform covariantly under $O_h$ rotations), **OR**
    *   **F4:** The constructed non-additive LUTs violate reversibility (not a bijection) or bit conservation.

#### 2. Rigorous Pre-Registration & Conservation Auditing
Before running any collisions, you must programmatically verify that your non-additive LUT mutations are strictly **reversible (bijections)** and **bit-conserving**. 
*   In your pre-registration file `src/pre_registration.md` (which must be written before execution), explicitly state the mathematical rules/orbits you are modifying and how you will guarantee these bijections. 
*   Do not "tweak" individual entries post-hoc to make a specific glider hold together; if you sweep a parameter space of interactions, pre-register the exact bounds of that sweep.

#### 3. The 2D Hex Glider Decoupling Test (High Priority)
Sub-goal D is highly elegant and strategically vital. We must know if the celebrated 2D hex $v=0.469c$ glider (`champion_rule_perfect.json`) is also a non-interacting composite of single-bit structures, or if its rule-table contains genuine non-additive terms that bind its constituent bits. 
*   If the 2D hex glider *does* decompose, then our entire historical understanding of "coherent gliders" in this project must be re-framed as composite-stream physics.
*   If it *does not* decompose, it serves as a mathematical proof-of-concept that reversible, local CA rules can indeed bind discrete bits into true particles.

Proceed to pre-registration and execution once you have corrected the falsification logic. Maintain a neutral, precise vocabulary when reporting outcomes.

---

