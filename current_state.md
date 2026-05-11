Phase: 3 - Focused Exploration (2D Hex Interactions)

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED.** The current rule (from a W=2 kernel) has been proven unsuitable for interaction studies as it is not bit-conserving in multi-particle scenarios. We are now pivoting to find a more complex and robust rule by searching for a valid kernel at Hamming Weight 3.

### Confirmed Findings
- A formal method exists to find symmetric rule kernels with specific geometric and algebraic constraints (iter_038, iter_044).
- The rule generated from the W=2 kernel `(A=3, B=6)` supports a stable, 3-bit, period-2 stationary oscillator (iter_044).

### Refuted Hypotheses
- **The W=2 rule `(A=3, B=6)` does not conserve bit count during multi-oscillator interactions.** This makes it an invalid "physical" rule for our purposes (iter_047, iter_048).

### In Progress
- **iter_049:** Searching for a valid rule kernel at Hamming Weight 3 to serve as the foundation for a new, more robust rule.
