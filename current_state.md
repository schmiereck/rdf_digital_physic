# Current Research State
Phase: PLATFORM FAILURE - BLOCKED

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid to enable the study of emergent mass and interactions.

## Confirmed
- A stable, bit-conserving `v=1c` glider exists (iter_179).
- A rule supporting perfectly elastic `v=1c` glider collisions exists (iter_193).
- The `v<c` glider from iter_218 was an exploit of the `LeakyCheckpointFitness` function, which incorrectly rewards slow, persistent drift (iter_220.4).

## Refuted
- The `v<c` glider (`g4_rule_083`) from iter_218 is a stationary object, not a glider (iter_219.7).

## In Progress
- A new, exploit-resistant fitness function, `DisplacementConsistencyFitness`, has been developed but remains **unvalidated due to persistent platform errors**. All attempts to run validation scripts in this phase failed (iter_220.1, 220.2, 220.3).

## Open Questions
- What is causing the `code_error` state that makes agents hang during simulations?
- Is the new `DisplacementConsistencyFitness` function effective in practice?
- Can an evolutionary search using this function discover a `v<c` glider?
