Phase: 3 - W=3 Rule Dynamics

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**BLOCKED.** The first empirical test of the W=3 rule (from kernel A=7, B=14) failed because the chosen 3-bit seed was not stable (iter_050). The rule itself remains a valid candidate. We are now pivoting to a systematic search to determine if this rule supports *any* stable 3-bit objects.

### Confirmed Findings
- A valid, contiguous, center-flipping, conflict-free rule kernel exists at Hamming Weight 3 (A=7, B=14) (iter_049).
- The previous W=2 rule (`A=3, B=6`) is not bit-conserving during multi-particle interactions and has been abandoned (iter_048).

### Refuted Hypotheses
- The specific 3-bit seed `{E, SE, S}` is not a stable object under the W=3 rule (iter_050).

### In Progress
- **iter_051:** Systematically searching for all stable, non-trivial, 3-bit objects (still lifes or oscillators) supported by the W=3 rule.
