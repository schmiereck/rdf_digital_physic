Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- A canonical "ash" pattern is a viable, reproducible environment for testing rule dynamics (`src/ash_pattern.json`) (iter_120).
- An evolutionary algorithm can successfully optimize rules to maximize a displacement-based fitness metric on this "ash" (iter_121-123).

## Refuted
- The motion optimized by the evolutionary algorithm is not sustained. It is a transient, one-time rearrangement that completes within 10 steps. The algorithm found a loophole in the fitness function (iter_125).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Can the fitness metric be modified to reward sustained motion over transient rearrangement?
- Is there a different initial state (other than the ash) that would lead to sustained motion with the current top rules?
- Can we evolve rules specifically on a metric of 'sustained displacement' (e.g., displacement from steps 100-200)?
- Is the C2 symmetry class fundamentally too stable, preventing sustained motion?
- What if we increase the mutation rate dramatically to escape the current local optimum?
