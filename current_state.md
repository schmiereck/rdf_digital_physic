Phase: 3 - C2-Symmetric Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
PIVOT. All previous approaches exploring highly symmetric (C6) rules under both synchronous and asynchronous update models have failed to produce moving particles ("gliders"). This entire research direction is now considered a dead end. The project has pivoted to challenge the fundamental assumption of high spatial symmetry.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels (iter_033, 061, 065).
- A valid, reversible, non-conserving rule kernel with only C2 (180-degree) symmetry exists (iter_072).

### Refuted Hypotheses
- Simple gliders exist for the tested C6-symmetric rules under a synchronous update model. (Falsified by exhaustive searches up to 4-bits in iter_060, 064, 069).
- Asynchronous update models (2-phase and 3-phase) enable glider propagation for C6 rules. (Falsified by iter_070, 071).

### In Progress
- **iter_073:** Testing the first C2-symmetric rule (from kernel A=3, B=14) for the existence of 4-bit gliders.
