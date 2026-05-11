Phase: 3 - Non-conserving Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
EXPLORATION. The long-held paradigm of requiring strict local bit-conservation has been abandoned after exhaustive searches failed to find any moving particles ("gliders"). A new paradigm is being tested, based on rules that are reversible but locally non-bit-conserving.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels (iter_033, 061).
- A valid, reversible, non-bit-conserving rule kernel (popcount 2↔3) exists, satisfying all structural constraints (iter_065).

### Refuted Hypotheses
- Monolithic or composite gliders exist for any of the tested symmetric, **strictly bit-conserving** rules (Falsified by iter_052, 054, 059, 060, 063, 064). The strict conservation constraint appears to prevent motion.
- The 3-bit seed `{(51,50), (51,49), (50,49)}` is stable under the non-conserving rule (Falsified by iter_066; it decays immediately).

### In Progress
- **iter_067:** Systematically searching for any stable 2-bit or 3-bit objects under the first non-conserving rule to characterize its fundamental dynamics.
