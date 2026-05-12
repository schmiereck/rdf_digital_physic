Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- An evolutionary algorithm using a "late-displacement" fitness metric (measuring motion between steps 100-200) can successfully select for rules that produce sustained motion (iter_126).
- The top rule from this process (iter_126/rule_048) produces a slow, chaotic drift, not a simple glider.

## Refuted
- A simple displacement fitness metric is flawed, rewarding transient, one-time rearrangement instead of sustained motion (iter_125).
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process fails to animate the ash (iter_118, 119).
- Direct searches for simple gliders from small seeds in C6/C2 rule spaces are ineffective (iter_006-096).

## Open Questions
- Can we breed a more performant generation (Gen-5) from the new top rule (rule_048)?
- Is the motion of rule_048 linear over long time scales, or is it a random walk with zero net displacement?
- Can we increase the magnitude of the sustained motion through further evolution?
- What are the specific mappings in rule_048 that enable sustained motion?
- Is there a simpler initial state than the full "ash" that also exhibits sustained motion under rule_048?