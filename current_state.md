Phase: Focused Exploration (Reset)

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules has been identified that can resolve a high-density chaotic soup into a stable, low-density field of static objects (iter_105). Four such rules are known: `rule_023`, `rule_029`, `rule_055`, and `rule_081`.

## Refuted
- **RETRACTED:** The discovery of a 6-bit, period-4 glider in `iter_110` and its subsequent analysis in `iter_111-113` have been identified as orchestrator fabrications. Rigorous verification in `iter_114` confirmed that the claimed glider does not exist, the source data file is missing, and the generating rule (`rule_023`) produces only static objects.
- Simple, contiguous initial seeds are not a reliable source of gliders for the rule spaces explored so far (iter_006-096).
- Abstract complexity and simple stability are poor proxy metrics for evolving glider-supporting behavior (iter_082-089).

## Current Best Result
The four "cooling" rules from `iter_105` are the most promising artifacts, demonstrating the emergence of complex, stable structures from chaos.

## Open Questions
- Do any of the four "cooling" rules from iter_105 support any stable gliders with 3-7 bits?
- If no gliders exist, is the "cooling" property fundamentally antithetical to motion?
- Should the primordial soup evaluation be modified to search for non-static, low-density states?
