Phase: 3 - Focused Exploration (2D Hex Interactions)
### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED:** Inability to create a non-trivial, moving, symmetric 2D particle for use in collision experiments.

### Confirmed Findings
- A formal method exists to find conflict-free, symmetric rule kernels from disjoint rotational orbits with center-bit flipping properties (iter_036, iter_038).
- The first valid kernel found by this method, `(A=65, B=6)`, produces a rule that results in a stable, non-moving 2-bit pattern (a still-life) from a minimal seed (iter_040).
- A symmetric swap-based update model can create localized oscillators (iter_020).
- A hand-crafted, non-symmetric rule can produce a stable "arrowhead" glider (iter_024), but this rule is a developmental dead-end due to lack of symmetry.

### Refuted Hypotheses
- Simple rules on a standard 2D CA grid produce trivial global shifts, not localized particles (iter_017).
- Symmetric rules based on kernels from the *same* rotational orbit are dynamically inert (iter_035).
- Hand-crafted rules are brittle and do not respect the lattice's rotational symmetry (iter_028, iter_031).

### In Progress
- **iter_041:** Searching for the next valid rule kernel and testing its dynamics, to see if it can produce motion where the first one failed.
