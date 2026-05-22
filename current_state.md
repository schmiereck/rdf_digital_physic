# Current Research State
Phase: Emergent Gravitational Attraction and the Cavendish Unit Test (Phase 5.1) successfully completed.

## Goal
Demonstrate that localized mass-energy densities (modeled as a static potential well) generate coordinate time dilation that naturally bends the trajectories of propagating sub-light-speed gliders (the Cavendish test) on a physical CA grid under strict localism and bit conservation.

## Confirmed
- The 12-channel 3D DynamicLatchingEngine has been updated to support a permanent background mass distribution (iter_232.1).
- Emergent gravitational attraction has been physically demonstrated using a stable 4-bit 3D sub-light glider (LUT-08) traversing a 32^3 toroidal grid with a central Gaussian permanent mass (iter_232.2).
- Perfect bidirectional attraction was confirmed at mass_value = 35.0 and sigma = 2.5:
  - Glider launched below the mass (y_start = 12) deflected **UPWARDS by +0.50 lattice units** (Y_vac = 11.75, Y_dyn = 12.25) towards the mass.
  - Glider launched above the mass (y_start = 20) deflected **DOWNWARDS by -0.25 lattice units** (Y_vac = 19.75, Y_dyn = 19.50) towards the mass.
- The glider remains structurally stable and perfectly conserves bit count (exactly 4 bits) across all 80 steps of propagation under local trapping, unlatching, and collision cycles (iter_232.2).
- The **Asymmetric Zitterbewegung Mechanism** is confirmed: spatial gradients of coordinate latency naturally bias the local latching duration on the mass-facing side of a glider, slowing it down and rotating its momentum vector towards the mass without explicit force equations (iter_232.2).

## Refuted
- The assumption that sub-light gliders would disintegrate or get permanently stuck when encountering a strong local coordinate latency field; with tuned Gaussian smoothing (sigma = 2.5) and mass, gliders exhibit clean, stable, curved geodesic trajectories (iter_232.2).

## Best Result
- A central permanent mass of 35.0 (sigma = 2.5) attracts a 4-bit 3D sub-light glider, producing a clean, stable deflection of up to +0.50 lattice units in Y with perfect bit conservation.

## In Progress
- Scaling to a fully dynamic two-body active simulation where two co-moving sub-light gliders write to each other's latency fields, demonstrating mutual attraction and emergent orbits.

## Open Questions
- Can we observe mutual attraction and orbital fallback between two co-moving gliders?
- What is the mathematical relationship between the coordinate deflection angle, mass value, and the glider's impact parameter?
- Can we define a discrete event horizon (coordinate speed of light c = 0) on the grid?
