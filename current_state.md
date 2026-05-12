Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** A parity-conservation constraint (`HW(A)%2 == HW(B)%2`) on rule generation is highly effective at suppressing chaotic growth, enabling the discovery of "viable founder" rules with sustained, non-explosive motion (iter_138).
- **Evolution is Highly Effective (Peak Fitness):** The evolutionary process is successfully producing rules with dramatically improved peak performance. Gen-2 fitness (0.73) was 2x Gen-1 (0.36) (iter_139). Gen-3 fitness (6.55) is 9x Gen-2 (iter_140).
- **Local Fitness Metric Works:** A fitness metric focused on a local subset of objects correctly identifies and rewards sustained displacement (iter_135).

## Refuted
- **Mean Fitness as a Progress Metric:** In this rugged fitness landscape, mean population fitness is not a reliable indicator of progress. Destructive crossover makes the mean fitness of offspring lower than that of pre-selected parents (iter_139).
- **Viable Founders in Unconstrained Random Populations:** Randomly generated populations without the parity constraint do not contain viable founders (iter_136, 137).

## Current Best
The top parity-conserving rule (`rule_049` from iter_140) achieves a fitness of 6.55, representing the best candidate for sustained, non-chaotic motion found so far.

## Open Questions
- What is the qualitative nature of the motion produced by the new Gen-3 champion, rule_049?
- Can the Gen-3 champion sustain its motion over a longer run (e.g., 1000 steps)?
- Is there a relationship between high fitness and high bit ratio in the Gen-3 population?
- Can we modify the breeding process to reduce the number of inviable (zero-fitness) offspring?
