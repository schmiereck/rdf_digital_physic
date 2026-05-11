Phase: 3 - Non-Contiguous Seeds

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
FUNDAMENTALLY BLOCKED. All prior paradigms have failed to produce a moving particle ("glider"). A campaign is underway to test if gliders can be formed from non-contiguous initial seed patterns.

### Confirmed Findings
- **Paradigm Failure (Contiguous Seeds):** Exhaustive searches proved that no elemental or composite gliders can be formed from small (3- or 4-bit) contiguous seeds for any tested rule class or update model. (iter_052, 054, 059, 060, 063, 064, 069, 074-078)
- **Paradigm Failure (Simple Non-Contiguous Seeds):** A search of 2-bit non-contiguous seeds failed because the bits were too far apart to interact meaningfully under the rule's local influence. (iter_079)

### Refuted Hypotheses
- `noncontiguous-glider`: A 2-bit non-contiguous seed does not form a stable, moving object under the non-conserving rule (A=3,B=14). (iter_079)

### In Progress
- **iter_080:** Systematically searching for gliders from 3-bit non-contiguous seeds, the minimal complexity that allows for both non-contiguity and dense local neighborhoods.
