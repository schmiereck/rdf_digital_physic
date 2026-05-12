Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a high-density chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- A canonical "ash" pattern of 325 bits and 72 objects has been generated and stored at `src/ash_pattern.json` (iter_120).
- A fitness metric `displacement / (1 + |Δ_bits| + |Δ_objects|)` successfully distinguishes between structure-preserving and structure-destroying rules when applied to the ash environment (iter_120).
- Motion requires rules that contain "birth" mappings (iter_115).

## Refuted
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos (iter_117).
- A two-stage simulation process using pre-existing stable or chaotic rules fails to animate the ash (iter_118, 119).
- Exhaustive searches of C6 and C2 symmetric rule spaces for simple gliders from small contiguous seeds have failed (iter_006-096).

## Open Questions
- Can an evolutionary search, guided by the new ash-based fitness metric, produce a rule that animates the ash objects?
- What is the simplest rule that achieves a fitness score significantly higher than the inert baseline of 0.0524?
- Do all 72 ash objects respond similarly to an evolved rule?
- Can a rule evolved to animate this specific ash also animate ash from other 'cooling' rules?
