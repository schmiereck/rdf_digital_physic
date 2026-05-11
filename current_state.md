Phase: 3 - Asynchronous Updates

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
EXPLORATION. The first attempt to use an asynchronous update model (3-phase) failed to produce motion (iter_070). This iteration tests a different, less-biased asynchronous model (2-phase checkerboard) to isolate the cause of the failure.

### Confirmed Findings
- A principled method exists for finding mathematically valid, symmetric, reversible rule kernels for various rule classes (iter_033, 061, 065).
- **Under a synchronous update model**, none of the three major rule classes tested (conserving 2-cycle, conserving 3-cycle, non-conserving 2-cycle) support gliders for monolithic 3-bit or 4-bit seeds. They only produce stationary objects. (Evidence: iter_060, 064, 069).
- The non-conserving rule (A=3↔B=14) supports stable multi-bit still lifes under a synchronous update model (iter_068).

### Refuted Hypotheses
- Gliders exist for the tested rules **under a synchronous update model** (Falsified by iter_060, 064, 069).
- A 3-phase update schedule enables glider propagation for the non-conserving rule (Falsified by iter_070).

### In Progress
- **iter_071:** Re-running the 4-bit glider search for the non-conserving rule using a 2-phase (checkerboard) update schedule.
