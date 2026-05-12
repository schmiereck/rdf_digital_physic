Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** A parity-conservation constraint is highly effective at suppressing chaotic growth, enabling the discovery of rules with non-explosive dynamics (iter_138).
- **'Late-Late-Displacement' Metric is Effective:** An evolutionary fitness metric calculated between steps 400-800 successfully filters out rules with transient motion and selects for rules exhibiting sustained motion (iter_142).

## Refuted
- **Sustained Motion Not Yet Confirmed:** The high fitness scores observed up to Gen-3 were artifacts of a flawed metric that measured transient, expansive drift, not sustained motion. The `rule_049` from iter_140 creates a large, stable oscillator that stops moving after ~400 steps (iter_141).

## Current Best
- `rule_016` from the Gen-4 population (iter_142) is the current champion. It achieves a fitness of 6.48 on the stringent 400-800 step metric, demonstrating motion that persists far longer than any previous rule. The nature and true persistence of this motion are now the primary subject of investigation.

## Open Questions
- Is the motion of the new champion (rule_016) truly sustained, or will it also decay over a longer timescale (e.g., 2000 steps)?
- What is the qualitative nature of the motion? Is it a coherent, glider-like object, or a more complex, amorphous 'cloud'?
- Can we isolate the moving components from the stationary background in the `rule_016` dynamics?
- How does the velocity of the moving object scale with simulation time?
