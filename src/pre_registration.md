# RDF Scientific Pre-Registration

*   **Iteration:** 252
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
When the proven 2D hex glider rule (champion_rule_perfect from iter_222) is embedded
into a [111] hex plane of the 3D FCC lattice as a factorized 13-channel LGCA
(6 in-plane channels + 1 center channel following the 2D hex rule; 6 inter-plane
channels following an identity mapping), the resulting system supports a genuine
multi-bit bound glider with binding energy > 0 that propagates within the [111]
hex plane at v ≈ 0.469c. Furthermore, introducing controlled non-factorized coupling
between in-plane and inter-plane channels can produce 3D binding (bits spanning
multiple planes) while preserving glider stability at coupling strengths below a
critical threshold.

## 2. Falsification Criterion
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
    over 500 LUT variants × 50 seed configurations × 500 steps).

## 3. Proposed Method
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

## 4. Construction-vs-Empirical Classification (SRM Mandate)

Sub-goal 252.2 (Factorized Embedding at α=0) is a CODE-VERIFICATION AND ALIGNMENT TEST, not an empirical search. If the 2D hex glider rule is embedded into a [111] hex plane of the 13-channel FCC lattice with identity mappings on the 6 inter-plane channels, the glider's survival is 100% GUARANTEED BY CONSTRUCTION. It is an algebraic identity, not a physical discovery. No emergent or promotional language ("discovery of 3D gliders") may be used when reporting its propagation; it is merely a 2D glider running on a 3D coordinate projection.

## 5. Symmetry Degradation Warning (SRM Mandate)

By embedding the C3v-symmetric 2D hex rule into a single [111] plane family of the 13-channel FCC lattice, we are BREAKING the O_h hardware symmetry of the 3D universe. This is an anisotropic, layered 2.5D system — NOT an isotropic 3D spacetime. Any resulting "3D gliders" found via coupling (α > 0) must be explicitly evaluated for their dependence on this privileged plane. If they cannot propagate covariantly along the other three equivalent {111} plane families under O_h transformations, they are lattice-axis artifacts of the rule construction. This limitation must be stated clearly in all reports.

## 6. Expanded Falsification of Coupling Hypothesis (SRM Mandate)

The coupling hypothesis (α > 0 producing stable 3D bound states) is refuted if ANY of the following hold:
F4a: The "coupled" state fails the Single-Bit Decomposition Test (individual constituent bits can propagate on their own, proving the "bound state" is actually just parallel non-interacting composites).
F4b: The coupled state disperses or deheres under localized latency perturbations (proving it lacks binding energy to withstand coordinate distortion).
F4c: No stable configuration survives ≥ 300 steps for any α > 0.

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
