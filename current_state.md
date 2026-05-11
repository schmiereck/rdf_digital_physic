Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**MAJOR PIVOT.** All previous rule-finding paradigms, based on a top-down formal search for kernels with specific properties (conservation, symmetry, contiguity), have failed. Exhaustive searches across multiple rule classes, update models, and initial condition types (contiguous and non-contiguous) have yielded no moving particles ("gliders").

The project is now pivoting to a bottom-up, **evolutionary approach**. The new strategy is to evolve rules towards a desired *behavior* (e.g., complexity, motion) as measured by a fitness function, rather than designing them based on static structural properties.

### Confirmed Failures of Prior Paradigms
- **Formal Search (iter_049-081):** A systematic, top-down search for rules based on pre-defined constraints (conservation, symmetry, contiguity, 2-cycles, 3-cycles) has proven insufficient for finding rules that produce motion.
- **Update Models (iter_070-071):** Asynchronous update models act as strong damping mechanisms and are less likely to produce motion than synchronous updates for the tested rules.
- **Initial Conditions (iter_052-081):** Exhaustive searches using contiguous elemental seeds, composite contiguous objects, and non-contiguous elemental seeds (up to 4 bits) have all failed to produce gliders. The theoretical analysis in iter_081 proved the futility of the non-contiguous approach for the C6 non-conserving rule.

### In Progress
- **iter_082:** The first step of the evolutionary approach: designing and validating a dynamic "fitness metric" capable of distinguishing between trivial (dead/frozen) and complex (potentially interesting) CA rules.
