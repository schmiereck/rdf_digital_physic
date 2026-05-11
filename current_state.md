Phase: 3 - Focused Exploration (2D Hex Interactions)
### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED:** Inability to create a non-trivial, moving, symmetric 2D particle for use in collision experiments.

### Confirmed Findings
- A symmetric swap-based update model can create localized oscillators (iter_020).
- A hand-crafted, non-symmetric rule can produce a stable "arrowhead" glider (iter_024), but this rule is a developmental dead-end.
- A formal method now exists to find conflict-free, symmetric rule kernels from *disjoint rotational orbits* (iter_036). Kernel `(A=65, B=6)` is the first valid candidate found by this method.

### Refuted Hypotheses
- Simple rules on a standard 2D CA grid produce trivial global shifts (iter_017).
- Rules based on symmetric seeds or symmetric actions tend to produce stationary oscillators or fixed points, not gliders (iter_021, iter_022, iter_023).
- Hand-crafted rules are brittle and lack the necessary rotational symmetry for general physics (iter_028, iter_031).
- Naive symmetrization of rule kernels creates conflicting or inert rules if the kernel states are not from disjoint rotational orbits (iter_029, iter_035).

### In Progress
- **iter_037:** Testing the dynamics of the first rule generated from a valid disjoint-orbit kernel to see if it can finally produce a symmetric 2D glider or oscillator.
