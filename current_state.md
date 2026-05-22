# Current Research State
Phase: Phase 5.4 — N-Body Stability completed (first-class null result).

## Goal
Characterize three-body and many-body configurations: stability regimes, hierarchical groupings, escape velocities.

## Confirmed
- **No Active N-Body Binding:** The self-generated latency field ($\eta = 2.0$) is dispersive rather than binding for $N \ge 3$, yielding mean max pair distances that are systematically $+2.67$ to $+6.75$ lattice units larger than vacuum controls across 3-body and 4-body configurations (iter_236.1).
- **Ballistic Recurrence:** The apparent 2-body "bound state" observed in iter_235 is most parsimoniously re-interpreted as a ballistic recurrence artifact of rotated gliders on the discrete torus. In 3-body configurations, the Permutation 10 vacuum control ($\eta = 0.0$) was captured (mean max pair distance $7.73 \le L/3$) due to lattice-direction velocity alignment alone (iter_236.1).
- **Perfect Bit Conservation:** Perfect bit and structural conservation ($4 \times N$ bits) was maintained across all N-body runs (iter_236.1).
- **Escape Velocity Monotonicity:** The escape velocity probe shows a monotonically growing max pair distance with launch offset, failing to isolate a sharp, physical binding energy threshold (iter_236.1).

## Refuted
- The hypothesis that the Phase 5.3 coordinate latency field can sustain stable hierarchical 3-body or 4-body bound states. The field is dispersive for $N \ge 3$ at the current envelope (iter_236.1).
- The claim that the iter_235 bound state was a pure gravitational-like attraction effect; the occurrence of torus capture in the matched vacuum control indicates it is an orientation-dependent ballistic alignment effect (iter_236.1).

## Best Result
- Perfect bit-conservation maintained over 160 steps across all 3-body and 4-body configurations; however, all active coupling runs dispersed faster than matched vacuum controls, establishing a clean null result (iter_236.1).

## In Progress
- Re-evaluating attraction mechanisms to isolate true, isotropic coordinate-latency attraction from ballistic lattice-axis recurrence.

## Open Questions
- Can we formulate a latency potential mapping that produces isotropic, field-driven gravity without ballistic lattice artifacts?
- Does a larger grid (e.g. $L \ge 64$) or finer discretization reduce ballistic recurrence alignment?
