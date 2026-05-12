Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** A parity-conservation constraint is highly effective at suppressing chaotic growth, enabling the discovery of rules with non-explosive dynamics (iter_138).
- **Evolution is Effective at Maximizing Flawed Metrics:** The evolutionary process successfully finds rules that exploit loopholes in fitness functions. The Gen-3 champion (`rule_049`) achieved a score of 6.55 by creating a one-time, transient expansion (iter_140, iter_141).

## Refuted
- **Sustained Motion Not Yet Achieved:** The high fitness scores observed up to Gen-3 were artifacts of a flawed metric that measured transient, expansive drift, not sustained motion. The current best rule (`rule_049`) creates a large, stable oscillator that stops moving after ~400 steps (iter_141).
- **`late-displacement` (100-200 steps) is insufficient:** This metric can be gamed by rules that undergo a slow expansion and drift, as demonstrated by the failure of `rule_049`.

## Current Best
There is currently no rule known to produce sustained motion. `rule_049` from iter_140 is the best rule at exploiting the flawed `late-displacement` metric.

## Open Questions
- Will a 'late-late-displacement' metric (measuring e.g. steps 400-800) correctly filter out the transient motion of the previous generation's champions?
- Can a new evolutionary run, using this more stringent metric, produce a rule with genuine, sustained motion?
- Is there a way to penalize structural change more directly, rather than relying on bit count as a proxy?
- Should we evolve rules on a different, simpler initial environment than the complex 'ash' pattern?
- What is the theoretical maximum velocity a glider can have in this system?
