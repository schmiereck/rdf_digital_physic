Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** A parity-conservation constraint is highly effective at suppressing chaotic growth, enabling the discovery of rules with non-explosive dynamics (iter_138).
- **New Fitness Metric Validated:** A new metric, `velocity_stability_fitness`, has been implemented and validated. It correctly identifies and penalizes the decaying motion of previous champion rules by measuring velocity variance over multiple time windows (iter_145).

## Refuted
- **Sustained Motion Not Yet Achieved:** All evolved "champion" rules so far have exhibited transient or decaying motion, not sustained locomotion.
- **`rule_016` Motion Decays:** The Gen-4 champion rule (`rule_016`) has decaying velocity. Its displacement drops from 40.4 units (steps 400-800) to 17.0 units (steps 1200-1600) (iter_143, iter_145).
- **`rule_049` Motion is Transient:** The Gen-3 champion (`rule_049`) expands into a large, stable oscillator, with all motion ceasing after ~400 steps (iter_141).

## Current Best
- There is currently no rule that produces sustained motion. The best-validated fitness score under the new `velocity_stability_fitness` metric is 2.187 for the unstable `rule_016`.

## Open Questions
- Will a new generation (Gen-5), evolved with the velocity-stability metric, produce a rule with a fitness > 2.2 and a velocity standard deviation < 5.0?
- Can the new champion from Gen-5 maintain at least 90% of its velocity over a 4000-step run?
- Is the "ash" environment itself contributing to the decay, and should we evolve on a single, isolated object pair instead?
- Would penalizing high variance in bit-count help suppress the expansive-contractive patterns that are gaming the current metrics?
