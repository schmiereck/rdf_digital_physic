# Research Manager Log - Iteration 252

## Iteration 252 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
When the proven 2D hex glider rule (champion_rule_perfect from iter_222) is embedded
into a [111] hex plane of the 3D FCC lattice as a factorized 13-channel LGCA
(6 in-plane channels + 1 center channel following the 2D hex rule; 6 inter-plane
channels following an identity mapping), the resulting system supports a genuine
multi-bit bound glider with binding energy > 0 that propagates within the [111]
hex plane at v ≈ 0.469c. Furthermore, introducing controlled non-factorized coupling
between in-plane and inter-plane channels can produce 3D binding (bits spanning
multiple planes) while preserving glider stability at coupling strengths below a
critical threshold.

**Proposed Falsification Criterion:**
Refuted if any of the following hold:
F1: The 2D hex glider does not survive embedding into the 3D FCC lattice
    (no stable propagation for 200+ steps from the L-tromino seed on the [111] plane).
F2: The embedded glider propagates but fails the Single-Bit Decomposition Test
    (isolated constituent bits survive independently, proving it's a non-interacting composite).
F3: The 13-channel factorized LUT cannot be constructed to be simultaneously
    bijective, bit-conserving, and compatible with the 2D hex rule on in-plane+center channels.
F4: For all tested coupling strengths (0.0 to 1.0 in 0.1 increments), either the
    glider is destroyed (disperses within 200 steps) or no 3D binding emerges
    (no configuration with bits on 2+ planes passes the Three-Test Coherence Protocol
    over 500 LUT variants × 50 seed configurations).

**Proposed Method:**
Sub-goal 252.1 (Mechanism Extraction — Medium):
  - Load champion_rule_perfect.json from archive, trace the v=0.469c glider for one full period
  - Identify cooperative survival signature: which LUT entries enable binding
  - Document period, spatial extent, channel transition sequence
  - Files: src/analyze_hex_mechanism.py

Sub-goal 252.2 (3D FCC Embedding — High):
  - Build src/fcc_engine_embed.py: 13-channel FCC LGCA with [111] plane awareness
    (6 in-plane + 1 center + 6 inter-plane channels)
  - Construct factorized LUT: hex_rule on in-plane+center, identity on inter-plane
  - Verify bijectivity, bit conservation, C3v symmetry
  - Run positive control (2D hex standalone) and negative control (12-ch O_h LUT-08)
  - Place L-tromino seed on [111] plane, run 300 steps
  - Apply Single-Bit Decomposition Test if glider survives
  - Files: src/fcc_engine_embed.py, src/test_embedded_glider.py

Sub-goal 252.3 (Inter-Plane Coupling — High, conditional on 252.2):
  - Design coupled LUTs with coupling parameter α ∈ [0,1]
  - Sweep α in 0.1 increments; at each α test 500 LUT variants × 50 seeds × 300 steps
  - Apply Three-Test Coherence Protocol to survivors with displacement > 50
  - Search for 3D gliders spanning 2+ hex planes
  - Files: src/interplane_coupling.py

Sub-goal 252.4 (Symmetry Characterization — Medium, conditional on 252.3):
  - Test O_h covariance (expected to fail due to C3v symmetry) and C3v covariance
  - Document symmetry properties of any discovered 3D gliders
  - Files: results in sub 252.3 output

---

## Iteration 252 -> Planner [Strategic Guidance]

# Strategic Guidance: Skeptical Review of Iteration 252 Plan

To maintain scientific rigour and prevent the team from misinterpreting algebraic embeddings as emergent physics, you must execute the proposed plan under the following strict directives:

### 1. The Construction-vs-Empirical Test (Sub-goal 252.2 is Definitional)
Let us be entirely clear: **if you embed the validated 2D hex glider into a 3D FCC lattice by factorizing the extra channels with an identity mapping, its survival is 100% guaranteed by construction.** It is an algebraic identity, not a physical discovery. 
* **Instruction:** You must explicitly classify Sub-goal 252.2 as a **code-verification and alignment test**, not an empirical search. Do not use emergent or promotional language ("discovery of 3D gliders") when reporting its propagation; it is merely a 2D glider running on a 3D coordinate projection.

### 2. Explicit Symmetry Degradation Warning
By embedding the $C_{3v}$-symmetric 2D hex rule into a single [111] plane family of the 13-channel FCC lattice, you are **breaking the $O_h$ hardware symmetry of the 3D universe**. 
* **Instruction:** If you proceed with this anisotropic model, you must use highly disciplined language. You are simulating a *layered, anisotropic 2.5D system*, not an isotropic 3D spacetime. 
* Any resulting "3D gliders" found via coupling ($\alpha > 0$) must be explicitly evaluated for their dependence on this privileged plane. If they cannot propagate covariantly along the other three equivalent $\{111\}$ plane families under $O_h$ transformations, they are lattice-axis artifacts of your rule construction. State this limitation clearly in your pre-registration.

### 3. Rigorous Falsification of the Coupling Hypothesis ($\alpha > 0$)
Your hypothesis that non-factorized coupling ($\alpha > 0$) can produce stable 3D bound states spanning multiple planes is highly ambitious but prone to parameter-tuning exploits. 
* **Mandated Falsification Criterion:** Your pre-registration must state that the coupling hypothesis is **refuted** if:
  1. The "coupled" state fails the *Single-Bit Decomposition Test* (meaning individual constituent bits can propagate on their own, proving the "bound state" is actually just a set of parallel non-interacting composites).
  2. The coupled state disperses or deheres under localized latency perturbations (proving it lacks the binding energy to withstand coordinate distortion).
  3. No stable configuration survives $\ge 300$ steps for any $\alpha > 0$.

Before running any simulations, ensure that your exact hypothesis, the $C_{3v}$ anisotropy caveat, and these quantitative falsification criteria are committed to `src/pre_registration.md`. Document any null results with the same precision as a positive finding. Proceed on this basis.

---

