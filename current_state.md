Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- A canonical "ash" pattern is a viable, reproducible environment for testing rule dynamics (`src/ash_pattern.json`) (iter_120).
- A fitness metric `displacement / (1 + |Δ_bits| + |Δ_objects|)` successfully guides evolution (iter_120).
- An ash-based evolutionary strategy is effective, showing significant fitness improvement across generations.
  - Gen-1 mean fitness: 0.0127 (iter_121)
  - Gen-2 mean fitness: 0.0444 (+248% vs Gen-1) (iter_122)
  - Gen-3 mean fitness: 0.0630 (+41.8% vs Gen-2) (iter_123)
- The evolutionary search has converged to a top fitness score of ~0.240, which was found in Gen-2 and rediscovered but not surpassed in Gen-3 (iter_122, 123).

## Refuted
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Is the motion of the top-performing rule sustained over a longer simulation, or does it stop after an initial rearrangement?
- What is the qualitative nature of the motion? (e.g., a single object moving, or a collective drift)
- Can a different mutation operator or a larger population break the current fitness plateau?
- Are the top rules from Gen-3 structurally similar to each other?
- How does the top rule perform on a different ash pattern to test for generalization?
