Phase: 3 - Non-conserving Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
EXPLORATION. The long-held paradigm of requiring strict local bit-conservation has been abandoned. A new paradigm is being tested, based on rules that are reversible but locally non-bit-conserving. The first such rule (kernel A=3↔B=14) is being characterized.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels for both conserving and non-conserving rules (iter_033, 061, 065).
- The non-conserving rule (A=3↔B=14) supports a stable 1-bit still life, which is a decay product of a specific 3-bit seed (iter_067).

### Refuted Hypotheses
- Monolithic or composite gliders exist for any of the tested symmetric, **strictly bit-conserving** rules (Falsified by iter_052, 054, 059, 060, 063, 064).
- All 2-bit contiguous seeds are stable under the non-conserving rule (Falsified by iter_067; they all decay to zero).

### In Progress
- **iter_068:** Exhaustively searching all 11 contiguous 3-bit seeds under the non-conserving rule to find any stable, multi-bit objects and fully characterize the rule's dynamics at this complexity.
