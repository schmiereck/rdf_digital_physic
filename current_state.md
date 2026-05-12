Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Evolutionary Breakthrough:** Breeding a third generation of rules with a new fitness metric that rewards bit-reduction produced a rule (`iter_131/rule_011`) with a fitness score of 1.33, a ~3400% improvement over the previous generation's champion (iter_131).
- **New Behavior:** The top rule appears to "evaporate" the static ash field into a much smaller (78-bit), mobile remnant (iter_131).
- **Optimal Rule Density:** C2-symmetric rules with medium density (8 kernel pairs) are most likely to produce viable, non-chaotic, sustained motion (iter_129).
- A "late-displacement" fitness metric (measuring motion between steps 100-200) successfully filters out rules that only produce transient, initial motion (iter_125, 127).
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).

## Refuted
- The evolutionary lineage from the flawed early-displacement metric (Gen-1 to Gen-4) is a dead end (iter_127).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process (cooling rule, then motion rule) fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- What is the structure of the 78-bit mobile remnant produced by rule_011?
- Is the motion of the remnant sustained over a longer simulation (e.g., 1000 steps)?
- Can we visualize the 'evaporation' process to understand how rule_011 works?
- Now that we have a rule that creates a mobile object, can we isolate that object and study it in a clean environment?
