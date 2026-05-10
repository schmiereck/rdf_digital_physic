Phase: Phase 3: Die 2D-Hex-Kollision (Streuung)

## 1. Goal
Demonstrate that complex physical phenomena can emerge from minimal, local, reversible rules on a discrete, symmetric lattice.

## 2. Confirmed Findings
- **Milestone Reached (Phase 1):** A 1D lattice supports bit-conserving rules that allow for stable particle propagation at v=c (iter_009, iter_010).
- **Milestone Reached (Phase 2):** Increasing bit-depth to 2 bits/cell allows for internal oscillations (v=0) and the emergence of "massive" particles with effective velocities v < c (iter_011, iter_012, iter_013, iter_014).
- **Rule Existence (2D-Hex):** Non-trivial, reversible, bit-conserving rules exist for a 2D hexagonal, 7-cell neighborhood (iter_015).
- **Trivial Glider (2D-Hex):** A simple neighborhood bit-rotation rule produces stable v=c gliders, but this dynamic is equivalent to a trivial global grid shift (iter_016).

## 3. Current Best Result
- **2D Hex Glider:** v=(dq=0, dr=-1), but is a non-local global shift (iter_016).

## 4. In Progress
- **iter_017:** Testing if a local center-neighbor bit-swap rule produces a stable, stationary oscillator.

## 5. Open Questions
- Can a local bit-swap rule create a stable, stationary oscillator?
- How can we construct a rule for a non-trivial (localized) glider in 2D?
- How do localized 2D patterns interact?
- What initial patterns lead to complex behavior under simple local rules?
