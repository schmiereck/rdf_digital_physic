# Current Research State
Phase: Phase 6.1 — Statistical Superposition completed / Path A: Classical Soliton Scattering Characterization completed.

## Goal
Characterize the phase-dependent collision dynamics of the v=0.469c sub-light speed glider on the 2D hexagonal lattice under Rule A (champion_rule_perfect.json), establishing classical soliton scattering and annihilation cross-sections.

## Confirmed
- **Non-linear Soliton Interactions (iter_239.1):** Swept 117 configurations over transverse spatial offsets $\Delta y \in [-4, 4]$ and relative temporal phase delays $\Delta t \in [0, 12]$ using a non-periodic $256 \times 256$ grid. The active joint state is a highly non-linear interaction, rather than a trivial bitwise OR of independent controls.
- **Period-6 Phase Periodicity (iter_239.2):** Across all 9 transverse spatial offsets, the collision outcomes exhibit perfect period-6 periodicity for phase delays $\Delta t \ge 1$ (e.g., $\Delta t$ and $\Delta t + 6$ yield identical classifications). This temporal period of 6 steps perfectly matches the 6-step internal state cycle of the sub-light speed glider.
- **Discrete Annihilation Channels (iter_239.1):** Perfect mutual annihilation (total bit count = 0, representing complete destructive interference/scattering) occurs periodically at $\Delta y = 1$ for $\Delta t \in \{1, 7\}$ and at $\Delta y = 3$ for $\Delta t \in \{4, 10\}$.
- **Discrete Deflection Channels (iter_239.1):** Stable scattering and deflection (soliton deflection) occurs at periodic intervals, specifically at $\Delta y = 1$ for $\Delta t \in \{3, 5, 9, 11\}$ and at $\Delta y \in \{0, 2\}$ for $\Delta t \in \{4, 10\}$.
- **Publication-quality Visualization (iter_239.2):** Generated a high-resolution 2D outcome phase diagram (`scattering_phase_diagram.png`) displaying the structural boundaries between Annihilation, Transmission, Scattering/Deflection, and Chaos.

## Refuted
- **Phase Insensitivity:** The hypothesis that glider collisions are phase-insensitive is refuted. Changing the relative temporal delay $\Delta t$ by a single step completely alters the collision dynamics (toggling between annihilation, chaotic explosion, and stable deflection).
- **Linear Superposition:** The hypothesis that the combined simulation of two gliders is a trivial linear superposition of independent gliders is refuted for all interacting configurations ($\Delta y \in [-2, 2]$ and $\Delta y = 3$ at even delays).

## Best Result
- Complete, rigorous 2D phase diagram (`scattering_phase_diagram.png`) of 117 collision configurations, demonstrating perfect period-6 phase-coherent soliton scattering and periodic mutual annihilation.

## In Progress
- Pivot to Phase 7: Particle Zoo (cataloging other stable propagating patterns, conserved quantities, and pair production).

## Open Questions
- Do other discovered glider species (e.g., LUT-08 on 3D FCC) exhibit similar phase-coherent, period-matched classical soliton scattering?
- Can we define and measure additive charges or conserved quantities that are invariant across these discrete deflection events?
- Can we simulate high-energy collisions of gliders that lead to clean pair production of new stable glider species?
