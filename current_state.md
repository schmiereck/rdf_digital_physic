Phase: 3 - Focused Exploration (2D Hex Interactions)

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**UNBLOCKED.** We have a symmetric rule that produces a stable, non-trivial dynamic object (a 3-bit stationary oscillator). We are now probing its interaction properties.

### Confirmed Findings
- A formal method exists to find conflict-free, symmetric rule kernels with specific geometric and algebraic properties (iter_038).
- Adding a "contiguity" constraint to the kernel search is critical for producing dynamically interesting rules (iter_044).
- The rule generated from kernel `(A=3, B=6)` supports a stable, 3-bit, period-2 stationary oscillator (iter_044).

### Refuted Hypotheses
- Mathematically valid kernels without geometric constraints are not sufficient to produce motion (iter_040, iter_043).
- Hand-crafted, asymmetric rules are a dead end for creating a generalizable, physics-like system (iter_028, iter_031).

### In Progress
- **iter_045:** Staging the first interaction experiment between two 3-bit oscillators to test for emergent physics.
