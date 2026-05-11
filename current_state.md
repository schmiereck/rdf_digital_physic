Phase: 3 - W=3 Cyclic Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
UNBLOCKED. Exhaustive searches proved that our previous class of rules (W=3 involutions) do not support moving particles (gliders), blocking the project. A successful search in iter_061 identified a valid kernel for a new, more complex class of rule based on a 3-cycle (A→B→C→A). We are now testing the dynamics of the first rule from this new class.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels based on n-cycles and multiple geometric/algebraic constraints (iter_038, iter_049, iter_061).
- A valid 3-cycle kernel exists at W=3: (A=7, B=11, C=14) (iter_061).

### Refuted Hypotheses
- W=3 involution rules (A↔B) can support moving particles (gliders) at 3-bit or 4-bit complexity. Two different such rules were exhaustively tested and found to only produce stationary objects (iter_052, iter_054, iter_059, iter_060).

### In Progress
- **iter_062:** Characterizing the dynamics of the first 3-cycle rule by searching for stable 3-bit objects.
