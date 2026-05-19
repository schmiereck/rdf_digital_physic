# Current Research State
Phase: Methodological Correction Complete

## Goal
Discover a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- **A stable, bit-conserving `v=1c` glider was discovered** via warm-start evolution (iter_215.2) and its properties were confirmed (iter_216.2). It moves at exactly 1.0 cell/step.
- The **"warm-start" evolutionary strategy** is effective for finding `v=1c` gliders (iter_215.2).
- The `LateWindowDisplacementFitness` is structurally biased towards `v=1c` particles and unsuitable for `v<c` search (iter_216.3).
- A new, more robust `SubLightFitness` function with velocity and period gates has been implemented (iter_216.4).
- The execution platform is currently stable (iter_216.2).

## Refuted
- The particle discovered in iter_215 is NOT a `v<c` glider.

## In Progress
- The search for a true `v<c` glider is being reset, now using the new `SubLightFitness` function.

## Open Questions
- Can the new `SubLightFitness` function guide a 'warm-start' evolution to find a true `v<c` glider?
- What is the fitness landscape like under the new `SubLightFitness`?
- Does the period-detection mechanism correctly identify and reward complex internal oscillators?
