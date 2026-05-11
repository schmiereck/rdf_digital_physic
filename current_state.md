Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
The evolutionary search paradigm has been corrected. The previous fitness metric, which rewarded chaos, was discarded. A new fitness metric that rewards the formation of stable, localized structures was designed and successfully validated in iter_087. The research is now focused on applying this corrected metric to drive the evolutionary search toward the desired class of rules.

### Confirmed
- **New Fitness Metric Validated (iter_087):** The `1 / (1 + final_bit_count)` metric effectively separates stabilizing rules from chaotic ones, with a discrimination ratio >1000x.
- **Evolutionary Process Works (iter_084):** The G1->G2 breeding process successfully increases population fitness based on a given metric. The machinery for selection, crossover, and mutation is sound.
- **Formal Search Failure (iter_049-081):** All top-down, principled searches for rules have failed to produce motion. This paradigm is considered exhausted.

### In Progress
- **iter_088:** Running the first full evolutionary cycle with the new, validated stability-rewarding fitness metric to breed a generation of stabilizing rules.
