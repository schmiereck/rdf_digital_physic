# RDF Scientific Pre-Registration

*   **Iteration:** 246
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
The O_h non-covariance of LUT-08 opposite-chirality collision outcomes observed
on the L=32 toroidal grid in iter_245 (where rotating the collision setup through
an O_h proper rotation changed the outcome from Elastic to Chaotic) is caused by
interaction of glider trajectories and collision debris with the periodic boundary.
On an L=64 FCC grid with collision center at (32,32,32) — ensuring that debris
cannot reach any boundary within 80 simulation steps — the same O_h-rotated
opposite-chirality collision will produce the same qualitative outcome (Elastic)
as the unrotated collision, confirming O_h covariance of collision dynamics in
the bulk lattice.

## 2. Falsification Criterion
The hypothesis is REFUTED if, on the L=64 grid with collision center at (32,32,32),
the O_h-rotated opposite-chirality collision produces a qualitatively different
outcome (Chaotic or Partial) from the unrotated collision (Elastic). Specifically:

F1: If the rotated collision outcome classification differs from the unrotated
    classification (using the same Elastic/Partial/Chaotic taxonomy as iter_245),
    the non-covariance is genuine bulk physics, not a boundary artifact.

F2: If the unrotated collision itself changes outcome on L=64 (i.e., the L=32
    Elastic result was itself a boundary artifact), then the entire iter_245
    collision catalog is unreliable on L=32 and must be re-characterized.

F3: If the solo stability of either glider variant fails on L=64 (the rotated
    glider is not a valid LUT-08 on the larger grid), the comparison is invalid
    and the experiment must be re-designed.

F4-enhanced (Grid-Rounding Diagnostic): If the O_h-rotated collision produces a different outcome than the unrotated collision on L=64, AND the coordinate-rounding diagnostic shows that the rotated configuration has a different relative sub-lattice phase or different minimum spatial separation than the unrotated configuration, the non-covariance is classified as a DEFINITIONAL ALIGNMENT MISMATCH (coordinate-rounding artifact), NOT a failure of dynamic O_h covariance in the CA rule. In this case, the non-covariance is attributed to the discrete lattice's inability to represent the rotated configuration with sufficient geometric fidelity.

F5 (Multi-rotation consistency): If F4-enhanced identifies a coordinate-rounding mismatch, but at least one OTHER proper O_h rotation produces the same Elastic outcome as the unrotated configuration (with matching sub-lattice phases), then O_h covariance is partially confirmed for axis-aligned rotations, with the limitation documented.

A result where both unrotated and rotated collisions produce Elastic outcomes
on L=64 would NOT REFUTE the hypothesis, and would constitute evidence that
the iter_245 non-covariance was a boundary artifact.

## 3. Proposed Method
Step-by-step experimental protocol:

1. CREATE src/experiment_246_oh_covariance_64.py extending the collision
   experiment framework from iter_245 (112-line script).

2. CONFIGURE L=64 FCC grid with toroidal boundaries. The collision center
   is at (32,32,32). The LUT-08 glider velocity is sub-light (v < 1 cell/step),
   so over 80 steps the maximum displacement is < 80 cells. With center at
   grid center, debris cannot wrap around within the simulation window.

3. IDENTIFY the exact O_h rotation used in iter_245 that produced the
   Chaotic outcome. The script must apply the SAME rotation matrix to
   both glider positions and internal bit patterns.

4. RUN three collision configurations on L=64:
   (a) Unrotated opposite-chirality collision: LUT-08 (particle) approaching
       P-reflected LUT-08 (antiparticle) — expected Elastic (reproduces iter_245)
   (b) O_h-rotated opposite-chirality collision: same setup rotated through
       the O_h element from iter_245 — was Chaotic on L=32, predicted Elastic on L=64
   (c) Second O_h rotation (e.g., 90° about a different axis): additional
       probe for thoroughness — predicted Elastic

5. RUN solo stability controls for each glider variant (unrotated particle,
   unrotated antiparticle, rotated particle, rotated antiparticle) on L=64
   for 80 steps. Verify each propagates stably.

6. CLASSIFY outcomes using the same taxonomy as iter_245:
   - Elastic: both gliders emerge intact with 0 residual debris bits
   - Partial: some glider structure survives with residual debris
   - Chaotic: no recognizable glider survives, bit count grows or disperses

7. COMPARE outcomes: if (a) and (b) both produce Elastic, O_h covariance
   is confirmed in the bulk and the iter_245 non-covariance was a boundary
   artifact. If they differ, non-covariance is genuine.

8. SECONDARY ANALYSIS (no separate hypothesis — data collection only):
   Run the same-chirality destructive collisions on L=64 and characterize
   the debris. Specifically:
   - Count debris bits at each timestep
   - Check if debris stabilizes into recognizable patterns after 80 steps
   - If stable patterns are found, compare against the glider catalog from
     iter_241 to identify whether new particle species are produced
   This data will inform the Phase 7.4 hypothesis but does not constitute
   a standalone claim in this iteration.

FILES TO CREATE/MODIFY:
- src/experiment_246_oh_covariance_64.py (new, main experiment)
- src/pre_registration.md (updated with this plan)

PARAMETERS (declared in advance):
- Grid: L=64 FCC, toroidal boundaries
- Collision center: (32, 32, 32)
- Initial separation: ~10 cells along approach axis
- Simulation steps: 80
- Glider: LUT-08 (4-bit sub-light, from iter_224)
- Antiparticle: P-reflected LUT-08 (from iter_245)
- O_h rotation: same as iter_245 (to be identified from iter_245 archive code)

CONTROL: 
- Vacuum run (no gliders) on L=64 for 80 steps (verify grid stays empty)
- Solo runs for each glider variant (verify stability)
- Original L=32 result from iter_245 serves as the "prior observation"
  being tested — no need to re-run on L=32

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
