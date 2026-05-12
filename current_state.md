Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- A canonical "ash" pattern of 325 bits and 72 objects is a viable, reproducible environment for testing rule dynamics (`src/ash_pattern.json`) (iter_120).
- A fitness metric `displacement / (1 + |Δ_bits| + |Δ_objects|)` successfully distinguishes between inert (fitness ~0.0524), chaotic (fitness ~0.0), and motion-inducing rules (iter_120, 121).
- A random population of C2-symmetric rules contains members that can animate the ash pattern, providing a fitness signal for evolution (iter_121).

## Refuted
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Can an evolutionary search, guided by the ash-based fitness metric, produce a rule that creates clear, propagating gliders?
- Can we amplify the fitness signal through selection and breeding?
- What are the structural properties of rules that successfully animate the ash without destroying it?
- Can a rule evolved on this specific ash generalize to other initial conditions?
