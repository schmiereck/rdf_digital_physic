Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** A parity-conservation constraint is highly effective at suppressing chaotic growth, enabling the discovery of rules with non-explosive dynamics (iter_138).

## Refuted
- **Sustained Motion Not Yet Achieved:** All attempts to evolve sustained motion have resulted in "false positives" exhibiting transient motion.
- **`rule_016` Motion Decays:** The Gen-4 champion rule (`rule_016`), evolved with a stringent 400-800 step metric, was shown to have a velocity decay of over 50% when measured in a subsequent 1200-1600 step window (iter_143).
- **`rule_049` Motion is Transient:** The Gen-3 champion (`rule_049`) was shown to expand into a large, stable oscillator, with all motion ceasing after ~400 steps (iter_141).

## Current Best
- There is currently no rule that has been demonstrated to produce sustained motion. The evolutionary search is effectively back at square one, but with a much better understanding of the failure modes.

## Open Questions
- Can a fitness metric based on velocity stability (e.g., standard deviation over multiple windows) finally filter out transient motion?
- Is the "ash" environment too complex, and would evolution on a simpler seed pattern be more effective?
- Can we programmatically identify and track a "core" object to make the fitness metric more robust than a global center-of-mass calculation?
- Would penalizing high variance in bit-count help suppress the expansive-contractive patterns that are gaming the current metrics?
