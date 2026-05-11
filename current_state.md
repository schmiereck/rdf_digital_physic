Phase: 3 - W=3 Rule Dynamics

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
Partially unblocked. We have a mathematically valid W=3 rule (from kernel A=7, B=14) and have confirmed it supports at least one stable, stationary 3-bit object (a "still life"). However, to study interactions, a moving object ("glider") is required. The current focus is a systematic search for such a glider.

### Confirmed Findings
- A valid, contiguous, center-flipping, conflict-free rule kernel exists at Hamming Weight 3 (A=7, B=14) (iter_049).
- The W=3 rule supports at least one stable, non-trivial, 3-bit stationary object (a straight-line "still life") (iter_051).

### Refuted Hypotheses
- The specific 3-bit seed `{E, SE, S}` is not a stable object under the W=3 rule (iter_050).
- The W=2 rule (`A=3, B=6`) is not bit-conserving during multi-particle interactions and has been abandoned (iter_048).

### In Progress
- **iter_052:** Systematically searching for a stable, bit-conserving, 3-bit glider under the W=3 rule.
