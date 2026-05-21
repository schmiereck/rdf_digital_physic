# Current Research State
Phase: Coupled 3D+1 D4 Spacetime LGCA with Local Latching (Phase 4.4) successfully completed.

## Goal
Establish a fully coupled 3D+1 Spacetime LGCA on the D4 lattice, demonstrating perfect bit-conservation, coordinate time dilation (Shapiro delay), and coordinate light deflection (Fermat lensing) emerging from localized mass-energy densities.

## Confirmed
- A coupled 3D+1 D4 Spacetime LGCA with a local "latching/trapping" rule has been successfully established and validated (iter_229.1).
- Total bit count is perfectly conserved across 50+ steps under the complex latching-unlatching-collision cycle on a toroidal grid (iter_229.1).
- Microscopic LGCA simulations of single-bit light pulses pass through the smoothed central mass well, demonstrating a positive, perfectly linear Shapiro time delay (up to +45 steps at tau=15) that decays to 0 outside the mass core (b >= 2) (iter_229.4).
- Dijkstra Fermat pathfinding on the emergent latency field successfully demonstrates spatial light deflection (gravitational lensing). For strong gravity wells (tau=15), the optimal path bends around the mass core, trading a 2-step spatial detour for a 43-step coordinate time saving (iter_229.4).

## Refuted
- The assumption that high-dimensional 3D+1 D4 LGCA simulations require massive, unfeasible 18-channel or 24-channel lookup tables; a 6-channel temporal model coupled with a procedural local latching buffer is mathematically equivalent, highly efficient, and avoids state-space explosion (iter_229.1).

## Best Result
- A 32x32x32 toroidal grid with a central mass of value 10.0 and threshold 3.0/5.0 exhibits a perfectly linear Shapiro delay of exactly 3 * tau steps for direct hits (b=0), and 1 * tau steps for grazing hits (b=1), while Dijkstra Fermat pathfinding yields a maximum spatial deflection of 1 lattice unit.

## In Progress
- Preparing for Phase 5 to study multi-body dynamic mass interactions and mutual gravitational attraction.

## Open Questions
- Can we simulate multi-body dynamic mass systems and observe dynamic gravitational attraction?
- How do we represent discrete spatial curvature as a dynamical update on the lattice topological link lengths?
- Can we define an emergent discrete equivalent of the Schwarzschild radius where the coordinate speed of light reaches 0 (infinite latching)?
