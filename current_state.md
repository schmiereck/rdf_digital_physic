Phase: 3 - Non-conserving Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
EXPLORATION. The current paradigm uses rules that are reversible but locally non-bit-conserving. The first such rule (kernel A=3↔B=14) is being characterized. Exhaustive search at the 3-bit level found stable still-lifes but no gliders.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels for both conserving and non-conserving rules (iter_033, 061, 065).
- The non-conserving rule (A=3↔B=14) supports stable 1-bit and 3-bit still lifes, but no 3-bit oscillators or gliders (iter_067, iter_068).

### Refuted Hypotheses
- Monolithic or composite gliders exist for any of the tested symmetric, **strictly bit-conserving** rules (Falsified by iter_052, 054, 059, 060, 063, 064).
- All 2-bit contiguous seeds are stable under the non-conserving rule (Falsified by iter_067; they all decay to zero).
- The non-conserving rule (A=3↔B=14) supports stable multi-bit objects from *all* 3-bit seeds (Falsified by iter_068, which found 6 of 11 seeds decay to zero).

### In Progress
- **iter_069:** Exhaustively searching all 10 contiguous 4-bit seeds under the non-conserving rule to find a glider.
