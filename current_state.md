# Current Research State
Phase: Dynamic Spacetime and Frame Dragging on 3D+1 D4 Spacetime CA (Phase 4.5) successfully completed.

## Goal
Establish a fully coupled 3D+1 Spacetime LGCA on the D4 lattice, demonstrating perfect bit-conservation, coordinate time dilation (Shapiro delay), and coordinate light deflection (Fermat lensing) emerging from localized mass-energy densities.

## Confirmed
- A coupled 3D+1 D4 Spacetime LGCA with a local "latching/trapping" rule has been successfully established and validated (iter_229.1).
- Total bit count is perfectly conserved across 50+ steps under the complex latching-unlatching-collision cycle on a toroidal grid (iter_229.1, iter_231.3).
- Microscopic LGCA simulations of a single-bit light pulse passing through a moving mass well demonstrate a dynamic Shapiro delay that peaks at exactly 20 steps (51 vs. 31 steps vacuum) under perfect spatial synchronization (iter_231.3).
- Time-dependent Dijkstra pathfinding on the D4 lattice with a moving Gaussian potential well successfully simulates dynamic gravitational lensing and Shapiro delay (iter_231.4).
- A dynamic Doppler-like asymmetry is observed in lensing: co-moving photons (b > 0) experience a larger delay (+1.46 steps) than counter-moving photons, as they spend more time near the moving well (iter_231.4).
- Discrete gravitational frame dragging (light dragging) is demonstrated: photons passing close to the moving mass are laterally dragged by up to +16.97 lattice units in the direction of the mass's motion (iter_231.4).

## Refuted
- The assumption that time-dependent Dijkstra pathfinding in moving potentials is computationally intractable; a simple, 3-step fixed-point iteration solves the implicit coordinate arrival-time equation with high accuracy (residual < 1e-9) (iter_231.4).

## Best Result
- A moving mass with A_grav = 5.0, v_y = 0.2, and sigma = 4.0 on a 3D+1 D4 lattice produces a peak Shapiro delay of 1.46 steps and a maximum frame-dragging lateral deflection of 16.97 units.

## In Progress
- Preparing for Phase 5 to study multi-body dynamic mass interactions and mutual gravitational attraction.

## Open Questions
- Can we simulate multi-body dynamic mass systems and observe dynamic gravitational attraction?
- How do we represent discrete spatial curvature as a dynamical update on the lattice topological link lengths?
- Can we define an emergent discrete equivalent of the Schwarzschild radius where the coordinate speed of light reaches 0 (infinite latching)?
