Phase: 3 - Non-conserving Rules

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. All attempts to find a moving particle ("glider") using symmetric, reversible, and **strictly bit-conserving** rules have failed after exhaustive searches. This entire paradigm appears to be a dead end, producing only stationary objects. The current hypothesis is that the strict conservation constraint is too strong, preventing motion. We are now pivoting to investigate rules that are reversible but not strictly bit-conserving at the local level.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels based on n-cycles (iter_061).
- Both 2-cycle (involution) and 3-cycle rules can be constructed, but all examples tested only produce stationary objects (still lifes and oscillators) up to 4-bit complexity (iter_050-064).

### Refuted Hypotheses
- Monolithic gliders of 3 or 4 bits exist for any of the tested symmetric, bit-conserving rules (Falsified by iter_052, 054, 059, 060, 063, 064).
- Composite gliders can be formed from stationary components under tested rules (Falsified by iter_055, 056, 057).

### In Progress
- **iter_065:** Searching for the existence of a valid, reversible, but non-bit-conserving rule kernel (popcount 2 <-> 3).