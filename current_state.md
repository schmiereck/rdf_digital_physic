Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- A "late-displacement" fitness metric (measuring motion between steps 100-200) successfully filters out rules that only produce transient, initial motion (iter_125, 127).
- A random population of C2-symmetric rules is almost entirely barren of sustained motion; the single exception found was pathologically chaotic (iter_127).
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).

## Refuted
- The evolutionary lineage from Gen-1 to Gen-4 is a dead end. It optimized for a flawed early-displacement metric and its gene pool is devoid of rules that produce sustained motion (iter_127).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process (cooling rule, then motion rule) fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Is there an optimal rule density (number of non-identity mappings) for producing sustained, non-chaotic motion?
- What is the distribution of behaviors (static, chaotic, sustained motion) as rule density changes?
- Can we find a rule density that produces at least a 5% 'hit rate' of viable rules for Gen-1?
- How does the magnitude of displacement correlate with rule density?
