# Current Research State
Phase: v<c Glider Fitness Function Developed

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid to enable the study of emergent mass and interactions.

## Confirmed
- A stable, bit-conserving `v=1c` glider exists (iter_179).
- A rule supporting perfectly elastic `v=1c` glider collisions exists (iter_193).
- The `v<c` glider from iter_218 was an exploit of the `LeakyCheckpointFitness` function, which incorrectly rewards slow, persistent drift (iter_220.4).

## Refuted
- The `v<c` glider (`g4_rule_083`) from iter_218 is a stationary object, not a glider (iter_219.7).

## In Progress
- A new, exploit-resistant fitness function, `DisplacementConsistencyFitness`, has been developed but is **pending empirical validation** (iter_220.5). The validation attempts (iter_220.6, 220.7) were blocked by platform errors.

## Open Questions
- Is the new `DisplacementConsistencyFitness` function effective in practice at distinguishing gliders from drifters?
- Can a full evolutionary search using `DisplacementConsistencyFitness` successfully discover a true `v<c` glider?
- Is the 'leaky' conservation principle still a valuable component for `v<c` glider fitness?
- What is causing the `token_limit` errors that are blocking validation?
