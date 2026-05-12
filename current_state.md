Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** A parity-conservation constraint (`HW(A)%2 == HW(B)%2`) on rule generation is highly effective at suppressing chaotic growth, enabling the discovery of "viable founder" rules with sustained, non-explosive motion (iter_138).
- **Evolution is Effective (Peak Fitness):** While breeding viable founders produces many non-viable offspring (lowering mean fitness), it successfully generates rare individuals with dramatically improved peak performance. Gen-2 produced a champion with 2x the fitness of the best Gen-1 founder (iter_139).
- **Local Fitness Metric Works:** A fitness metric focused on a local subset of objects correctly identifies and rewards sustained displacement (iter_135).

## Refuted
- **Mean Fitness as a Progress Metric:** In this rugged fitness landscape, mean population fitness is not a reliable indicator of progress. Destructive crossover makes the mean fitness of offspring lower than that of pre-selected parents (iter_139).
- **Viable Founders in Unconstrained Random Populations:** Randomly generated populations without the parity constraint do not contain viable founders (iter_136, 137).

## Current Best
The top parity-conserving rule (`rule_033` from iter_139) achieves a fitness of 0.731, representing the best candidate for sustained, non-chaotic motion found so far.

## Open Questions
- Can breeding the top Gen-2 elites produce a Gen-3 champion with even higher fitness (>0.731)?
- What is the qualitative nature of the motion produced by the new champion, rule_033?
- Is there a way to modify the breeding process to reduce the high number of inviable (zero-fitness) offspring?
- Has the bit ratio of the top performers remained close to 1.0?
