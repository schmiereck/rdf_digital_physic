Phase: 3 - Focused Exploration (2D Hex Interactions)

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED.** The previous rule (from a W=2 kernel) was proven unsuitable for interaction studies as it was not bit-conserving in multi-particle scenarios. We are pivoting to test a new, more complex rule based on a W=3 kernel.

### Confirmed Findings
- A formal method exists to find symmetric rule kernels with specific geometric and algebraic constraints (iter_038, iter_044).
- A valid, contiguous, center-flipping, conflict-free rule kernel exists at Hamming Weight 3 (A=7, B=14) (iter_049).

### Refuted Hypotheses
- **The W=2 rule `(A=3, B=6)` does not conserve bit count during multi-particle interactions.** This makes it an invalid "physical" rule (iter_047, iter_048).
- The W=2 rule only produces stationary objects (fixed points or oscillators), not gliders (iter_040, iter_044).

### In Progress
- **iter_050:** Generating and testing the fundamental dynamics of the first rule based on the W=3 kernel (A=7, B=14).
