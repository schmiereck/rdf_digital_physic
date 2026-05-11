Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is in an active evolutionary search phase. A critical flaw in the original fitness metric (which rewarded chaos) was corrected. A new metric rewarding stability was validated (iter_087) and used to successfully breed a population of highly stabilizing rules (iter_088). The current focus is on analyzing this new generation of rules to see if they contain the desired glider dynamics.

### Confirmed
- **Stability-Rewarding Metric Works (iter_087):** The `1 / (1 + final_bit_count)` metric effectively separates stabilizing rules from chaotic ones.
- **Evolutionary Breeding is Effective (iter_088):** Using the new metric, the G2->G3 breeding cycle increased mean population fitness by 143% and eliminated all chaotic rules from the population.
- **Formal Search Exhausted (iter_049-081):** All top-down, principled rule searches failed to produce motion, validating the pivot to evolutionary search.

### In Progress
- **iter_089:** Exhaustively searching for gliders under the best *non-annihilating* rule produced by the new, stability-focused evolutionary process. This is the first direct test of whether the corrected search paradigm can achieve the project's primary goal.
