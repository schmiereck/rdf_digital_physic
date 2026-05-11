Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**MAJOR PIVOT.** The project is pursuing a bottom-up, evolutionary approach. The core evolutionary loop (generate, evaluate, select, breed) has been validated, successfully breeding rules with high abstract "complexity" scores. However, the strategy of selecting the *highest-fitness* rule failed, as it produced chaotic, space-filling dynamics unsuitable for localized particles (iter_085). The current hypothesis is that the "sweet spot" for glider-supporting rules is in the medium-complexity range.

### Confirmed
- **Evolutionary Process Works (iter_084):** The evolutionary algorithm is effective at breeding populations with higher average fitness scores.
- **Fitness Metric is Flawed for Goal (iter_085):** The current fitness metric (`mean_bit_count * stddev`) selects for chaotic rules, not rules that support stable particles.
- **Formal Search Failure (iter_049-081):** A comprehensive search of formally designed rules failed to produce any moving particles. This paradigm is abandoned.

### In Progress
- **iter_086:** Analyzing a *medium-fitness* rule from the evolved Gen-2 population to test the hypothesis that the ideal rules for gliders exist at the "edge of chaos," not at maximum complexity.
