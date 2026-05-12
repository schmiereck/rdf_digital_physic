Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- A canonical "ash" pattern of 325 bits and 72 objects is a viable, reproducible environment for testing rule dynamics (`src/ash_pattern.json`) (iter_120).
- A fitness metric `displacement / (1 + |Δ_bits| + |Δ_objects|)` successfully distinguishes between inert, chaotic, and motion-inducing rules (iter_120).
- An ash-based evolutionary strategy is effective. Selection and crossover significantly improve the population's mean fitness for animating the ash (Gen-1 mean: 0.0127, Gen-2 mean: 0.0444, +248%) (iter_122).

## Refuted
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Can we push the top fitness score above 0.5 by breeding a third generation?
- What do the dynamics of the top-performing Gen-2 rules look like visually?
- Is the fitness improvement starting to plateau?
- What structural properties do the high-fitness rules share?
- Can a rule evolved on this specific ash generalize to other initial conditions?
