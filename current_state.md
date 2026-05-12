Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Evolutionary Progress:** Breeding a second generation of medium-density rules from the two "founder" rules of iter_129 resulted in a 37.3% improvement in top fitness score (from 0.0277 to 0.0380). The number of viable rules in the population increased from 2% to 22% (iter_130).
- **Optimal Rule Density:** C2-symmetric rules with medium density (8 kernel pairs / 32 non-identity mappings) are most likely to produce viable, non-chaotic, sustained motion. Low-density rules are too static, and high-density rules are too chaotic (iter_129).
- A "late-displacement" fitness metric (measuring motion between steps 100-200) successfully filters out rules that only produce transient, initial motion (iter_125, 127).
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).

## Refuted
- The evolutionary lineage from the flawed early-displacement metric (Gen-1 to Gen-4) is a dead end (iter_127).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process (cooling rule, then motion rule) fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Can we continue to see fitness improvements in a third generation?
- What is the qualitative nature of the motion produced by the new top rule (Gen-2 rule_034)?
- Is the rate of improvement (37% per generation) sustainable?
- How does the top Gen-2 rule perform on a longer simulation run (e.g., 500 steps)?
