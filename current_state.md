Phase: 3 - Focused Exploration (2D Hex Interactions)

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**UNBLOCKED.** We have a symmetric rule that produces a stable, non-trivial dynamic object (a 3-bit stationary oscillator). We are now attempting to stage a valid interaction experiment by correcting the flaws from previous attempts.

### Confirmed Findings
- A formal method exists to find conflict-free, symmetric rule kernels with specific geometric ("contiguity") and algebraic properties (iter_038, iter_044).
- The rule generated from kernel `(A=3, B=6)` supports a stable, 3-bit, period-2 stationary oscillator (iter_044).

### Refuted Hypotheses
- Interacting oscillators must be placed at a critical distance. Too close leads to chaotic, non-conserving mergers (iter_047), and too far leads to no interaction (iter_045).
- Hand-crafted, asymmetric rules are a dead end for creating a generalizable, physics-like system (iter_028, iter_031).

### In Progress
- **iter_048:** Staging an interaction experiment between two 3-bit oscillators placed at the critical "just right" distance to test for emergent physics.
