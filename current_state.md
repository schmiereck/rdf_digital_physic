Phase: 3 - W=3 Cyclic Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. Two separate, principled, symmetric W=3 rules generated from 2-cycle (involution) kernels have been exhaustively tested. Both failed to produce any moving particles ("gliders") at 3-bit or 4-bit complexity. This suggests the involution-based rule generation method is too restrictive to support motion. We are now pivoting to test a new class of rules based on 3-cycles (A→B→C→A).

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels based on multiple constraints (iter_038, iter_044, iter_049).
- The first W=3 involution rule (A=7, B=14) supports stable still lifes but no 3-bit or 4-bit gliders (iter_051, iter_052, iter_054).
- The second W=3 involution rule (A=11, B=14) supports stable still lifes and oscillators but no 3-bit or 4-bit gliders (iter_058, iter_059, iter_060).

### Refuted Hypotheses
- Simple (3-bit, 4-bit) monolithic or composite particles can produce motion under W=3 involution rules. (iter_052, iter_054, iter_055, iter_057, iter_059, iter_060).

### In Progress
- **iter_061:** Searching for the existence of a valid 3-cycle kernel at Hamming Weight 3, which would form the basis of a new, potentially motion-supporting rule.
