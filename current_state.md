# Current Research State
Phase: Emergent Dynamic Two-Body Gravitational Attraction (Phase 5.2) completed.

## Goal
Demonstrate dynamic, self-consistent mutual two-body gravitational attraction on a physical CA grid where co-moving particles generate their own coordinate-latency fields, causing them to deflect towards each other under strict localism and bit conservation.

## Confirmed
- The 3D FFT periodic Gaussian smoothing engine (`ClosedLoopLatchingEngineV2`) has been successfully implemented and verified (iter_234.1).
- Emergent dynamic mutual attraction has been physically demonstrated using two parallel, co-moving 4-bit sub-light gliders (LUT-08) on a 32^3 toroidal grid (iter_234.3).
- Perfect mutual attraction was confirmed at initial separation = 5.0, alpha = 2.0, threshold = 0.045, gamma = 0.90, and eta = 2.0:
  - The gliders dynamically deflect towards each other, reducing their separation from 5.0 to 4.5 cells (mutual deflection = +0.50 lattice units) (iter_234.3).
  - The deflection grows stably and persists all the way to 160 steps with perfect total bit conservation (exactly 8 bits, 4+4 split) and structural stability (iter_234.3).
  - The Vacuum Control run (eta = 0.0) exhibits exactly 0.00 deflection, verifying that attraction is driven purely by the dynamic coordinate-latency field (iter_234.3).
- The **Jeans-like Dispersing Threshold** is confirmed: wide Gaussian smoothing (sigma=2.5) dilutes potentials; mutual attraction is only active when the initial separation is within the overlapping gradient region (<= 5 cells) (iter_234.2, iter_234.3).

## Refuted
- The assumption that self-consistent dynamic gravity would lead to chaotic disintegration or immediate fusion of sub-light gliders; with tuned Gaussian smoothing and thresholds, gliders exhibit clean, stable, and discrete geodesic attraction (iter_234.3).

## Best Result
- At an initial separation of 5.0, two 4-bit gliders attract each other, producing a clean, stable deflection of +0.50 lattice units at step 160 with perfect bit conservation (iter_234.3).

## In Progress
- Preparing to explore orbital capture and dynamic scattering under non-parallel launch configurations (Phase 5.3).

## Open Questions
- Can we observe mutual orbital capture or fallback between two gliders launched with non-parallel velocity vectors?
- Does the emergent gravitational attraction scale linearly with the deposition rate eta (the dynamic coupling constant)?
- Can we form a stable, dynamic multi-body cluster or bound state with three or more co-moving gliders?
