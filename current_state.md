Phase: 3 - Non-Contiguous Seeds

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
FUNDAMENTALLY BLOCKED. All prior paradigms have failed to produce a moving particle ("glider"). A new campaign has been initiated to test the hypothesis that gliders can only be formed from non-contiguous initial seed patterns.

### Confirmed Findings
- **Paradigm Failure (Elemental Gliders):** Exhaustive searches proved that no elemental gliders from small (3- or 4-bit) contiguous seeds exist for any tested rule class (conserving 2-cycle, conserving 3-cycle, non-conserving 2-cycle) or update model. (iter_052, 054, 059, 060, 063, 064, 069, 074)
- **Paradigm Failure (Emergent Gliders):** Exhaustive searches proved that interactions between known-stable, contiguous still-life patterns do not produce motion. All tested symmetric and asymmetric arrangements resulted in static fusion, no interaction, or decay. (iter_075, 076, 077, 078)
- **Key Insight:** The only remaining promising avenue is that gliders in this ruleset require non-compact or non-contiguous initial conditions.

### In Progress
- **iter_079:** Systematically searching for gliders from simple, 2-bit non-contiguous seeds under the C6 non-conserving rule (A=3↔B=14).