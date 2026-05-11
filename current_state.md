Phase: 3 - Focused Exploration (2D Hex Interactions)
### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED:** Inability to create a non-trivial, moving, symmetric 2D particle for use in collision experiments.

### Confirmed Findings
- A formal method exists to find conflict-free, symmetric rule kernels satisfying disjoint orbits and center-bit flipping (iter_038).
- The first valid kernel found by this method (`A=65, B=6`) generates a rule that produces a stable, non-moving 2-bit fixed point (a still-life) from a minimal seed (iter_040).

### Refuted Hypotheses
- Simple rules on a standard 2D CA grid produce trivial global shifts, not localized particles (iter_017).
- Symmetric rules based on kernels from the *same* rotational orbit are dynamically inert (iter_035).
- Hand-crafted rules are brittle and do not respect the lattice's rotational symmetry (iter_028, iter_031).
- The first valid symmetric rule kernel (A=65, B=6) does not produce motion (iter_040).

### In Progress
- **iter_043:** Finding the *second* valid rule kernel from our formal search and testing its dynamics to see if it can produce motion.
