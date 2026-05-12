Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Optimal Rule Density:** There is a "sweet spot" for rule density. C2-symmetric rules with medium density (8 kernel pairs / 32 non-identity mappings) are most likely to produce viable, non-chaotic, sustained motion. Low-density rules are too static, and high-density rules are too chaotic (iter_129).
- A "late-displacement" fitness metric (measuring motion between steps 100-200) successfully filters out rules that only produce transient, initial motion (iter_125, 127).
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).

## Refuted
- The evolutionary lineage from Gen-1 to Gen-4 is a dead end. It optimized for a flawed early-displacement metric and its gene pool is devoid of rules that produce sustained motion (iter_127).
- Generating random rules with a "low" density (4 kernel pairs) is ineffective, producing a near-zero hit rate of viable individuals (iter_127, 129).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process (cooling rule, then motion rule) fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Can we evolve a new generation from the two viable medium-density rules that surpasses their top fitness of 0.0277?
- What is the qualitative nature of the motion produced by the top medium-density rules?
- Is the 2% viability rate at medium density high enough for reliable evolutionary runs?
- How does the performance of the top medium-density rule change on a longer simulation run?
