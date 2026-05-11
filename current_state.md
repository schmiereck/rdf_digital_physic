Phase: 3 - W=3 Cyclic Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. We have a new, more complex class of rule based on a 3-cycle (A→B→C→A). A preliminary search confirmed it supports at least one stable, stationary 3-bit object (iter_062). However, it is unknown if this rule can produce *moving* objects (gliders), which are required to achieve the Phase 3 goal of staging a collision.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels based on n-cycles (iter_061).
- The 3-cycle rule (from kernel A=7, B=11, C=14) supports at least one stable, bit-conserving, 3-bit stationary object ("still life") (iter_062).

### Refuted Hypotheses
- W=3 involution rules (A↔B) can support gliders at 3-bit or 4-bit complexity. Two different such rules were exhaustively tested and found to only produce stationary objects (iter_052, iter_054, iter_059, iter_060).

### In Progress
- **iter_063:** Exhaustively searching all 11 contiguous 3-bit patterns for a glider under the new 3-cycle rule to determine if it is capable of producing motion.
