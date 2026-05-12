Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Pattern Transformation:** The evolutionary process has found a rule (`iter_131/rule_011`) that can rapidly and reliably transform a high-density, static "ash" pattern (325 bits) into a stable, low-density field of ~37 oscillating objects (~80 bits) (iter_131, 132).
- **Optimal Rule Density:** C2-symmetric rules with medium density (8 kernel pairs) are most likely to produce viable, non-chaotic, sustained motion (iter_129).
- A "late-displacement" fitness metric (measuring motion between steps 100-200) successfully filters out rules that only produce transient, initial motion (iter_125, 127).

## Refuted
- The "evaporating remnant" from `rule_011` is **not** a glider. It is a stable field of oscillators that undergoes a one-time positional shift during its formation but has no sustained translational motion (iter_132).
- The evolutionary lineage from the flawed early-displacement metric (Gen-1 to Gen-4) is a dead end (iter_127).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process (cooling rule, then motion rule) fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- What are the specific structures and periods of the ~37 oscillating objects that form the remnant?
- Can we visualize the remnant to understand its spatial distribution and dynamics?
- Can we evolve a *new* rule that specifically animates this field of oscillators?
- What happens if two of these remnants are placed next to each other under `rule_011`?
