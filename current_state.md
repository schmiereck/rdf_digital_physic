Phase: 3 - Focused Exploration (2D Hex Interactions)

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED:** Inability to generate a symmetric rule that produces non-trivial motion (gliders or complex oscillators).

### Confirmed Findings
- A formal method exists to find conflict-free, symmetric rule kernels satisfying disjoint orbits and center-bit flipping (iter_038).
- The geometric structure of a kernel is critical; non-contiguous bit patterns can lead to dynamically inert, self-trapping rules (iter_043).
- The first two valid kernels found via our formal search (`A=65,B=6` and `A2=96,B2=40`) both produce only stationary patterns (fixed points/still-lifes), not motion (iter_040, iter_043).

### Refuted Hypotheses
- Simply being mathematically valid is not sufficient for a kernel to produce interesting dynamics (iter_040, iter_043).
- Hand-crafted, asymmetric rules are a dead end for creating a generalizable, physics-like system (iter_028, iter_031).

### In Progress
- **iter_044:** Refining the formal kernel search with an additional geometric "contiguity" constraint to avoid the self-trapping failure mode observed in iter_043.
