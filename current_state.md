Phase: 3 - W=3 Cyclic Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. We have a new class of rule based on a 3-cycle (A→B→C→A). An exhaustive search proved it supports a rich variety of stable, but only stationary, 3-bit objects. It is unknown if this rule can produce *moving* objects (gliders), which are required to stage a collision.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels based on n-cycles (iter_061).
- The 3-cycle rule (from kernel A=7, B=11, C=14) supports stable, bit-conserving, stationary objects (still lifes and oscillators) for all 11 possible 3-bit contiguous patterns (iter_062, iter_063).

### Refuted Hypotheses
- The 3-cycle rule (A=7,B=11,C=14) supports stable, bit-conserving, 3-bit gliders. (Falsified by exhaustive search in iter_063).
- W=3 involution rules (A↔B) can support gliders at 3-bit or 4-bit complexity. (Falsified by exhaustive searches in previous campaigns).

### In Progress
- **iter_064:** Exhaustively searching all contiguous 4-bit patterns for a glider under the 3-cycle rule to determine if motion emerges at a higher complexity.
