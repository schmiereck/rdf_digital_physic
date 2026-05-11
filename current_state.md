Phase: 3 - Focused Exploration (2D Hex Interactions)

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**UNBLOCKED.** We have a symmetric rule that produces a stable, non-trivial dynamic object (a 3-bit stationary oscillator). We are now attempting to stage a valid interaction experiment.

### Confirmed Findings
- A formal method exists to find conflict-free, symmetric rule kernels with specific geometric ("contiguity") and algebraic properties (iter_038, iter_044).
- The rule generated from kernel `(A=3, B=6)` supports a stable, 3-bit, period-2 stationary oscillator (iter_044).

### Refuted Hypotheses
- The experimental setup of iter_045, with non-adjacent oscillators, failed to produce an interaction.
- Mathematically valid kernels without geometric constraints are not sufficient to produce motion (iter_040, iter_043).
- Hand-crafted, asymmetric rules are a dead end for creating a generalizable, physics-like system (iter_028, iter_031).

### In Progress
- **iter_047:** Staging the first interaction experiment between two *adjacent* 3-bit oscillators to test for emergent physics.
