Phase: 3 - C2-Symmetric Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
PIVOT. All previous approaches exploring highly symmetric (C6) rules under both synchronous and asynchronous update models have failed to produce moving particles ("gliders"). This entire research direction is now considered a dead end. The project is now challenging the fundamental assumption of high spatial symmetry by pivoting to a search for rules with only C2 (180-degree) symmetry.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels for C6-symmetric rules (iter_033, 061, 065).
- Under synchronous updates, no C6-symmetric rules tested (conserving or non-conserving) support gliders for monolithic 3-bit or 4-bit seeds (iter_060, 064, 069).

### Refuted Hypotheses
- Simple gliders exist for the tested C6-symmetric rules under a synchronous update model. (Falsified by iter_060, 064, 069).
- Asynchronous update models (2-phase and 3-phase) enable glider propagation for the non-conserving C6 rule. (Falsified by iter_070, 071).

### In Progress
- **iter_072:** A formal search for the existence of a valid, reversible, non-conserving rule kernel with only C2 (180-degree) symmetry.
