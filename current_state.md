Phase: 3 - Non-conserving Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
EXPLORATION. The long-held paradigm of requiring strict local bit-conservation has been abandoned after exhaustive searches failed to find any moving particles ("gliders"). A new paradigm is being tested, based on rules that are reversible but locally non-bit-conserving, allowing bit count to fluctuate.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels (iter_033, 061).
- A valid, reversible, non-bit-conserving rule kernel (popcount 2↔3) exists, satisfying all structural constraints (iter_065).

### Refuted Hypotheses
- Monolithic or composite gliders exist for any of the tested symmetric, **strictly bit-conserving** rules (Falsified by iter_052, 054, 059, 060, 063, 064). The strict conservation constraint appears to prevent motion.

### In Progress
- **iter_066:** Testing the dynamics of the first non-conserving rule (from kernel A=3, B=14) to see if it supports any stable objects.
