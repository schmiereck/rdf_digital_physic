Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**MAJOR PIVOT.** All prior research based on top-down, formal rule design has failed to produce motion (iter_049-081). This includes exhaustive searches of multiple rule classes (conserving/non-conserving), update models (sync/async), and initial conditions (contiguous/non-contiguous).

The project has successfully pivoted to a bottom-up, **evolutionary approach**. A dynamic fitness metric capable of quantitatively distinguishing between trivial (frozen/dead) and complex (dynamic, bounded) rules was validated in iter_082. This provides the core tool for a new search paradigm.

### Confirmed
- **Fitness Metric Validated (iter_082):** A metric based on the mean and standard deviation of grid population over time is effective at identifying rules that support sustained, complex dynamics from a random initial state.

### Refuted
- **Formal Search Paradigms (iter_049-081):** A comprehensive series of experiments has proven that top-down design based on simple structural properties like symmetry and conservation is insufficient for finding rules that produce motion.
- **Simple Initial Conditions (iter_052-081):** Exhaustive searches have shown that for the rules tested, no elemental or simple composite gliders emerge from small (<= 4 bits) initial patterns.

### In Progress
- **iter_083:** Implementing the first full generation of an evolutionary algorithm. This involves generating a large population of random rules, evaluating them with the validated fitness metric, and selecting the top-performing "elites" for the next generation.
