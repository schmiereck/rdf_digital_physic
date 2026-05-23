# RDF Scientific Pre-Registration

*   **Iteration:** 238
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
Two LUT-08 sub-light gliders (v = 0.469c) on a 3D FCC grid (L = 64) over T = 80 steps will exhibit isotropic, field-driven mutual attraction (deflection towards each other) when coupled via a self-generated coordinate-latency field computed with a non-periodic, zero-padded FFT solver. This attraction is physical and not an artifact of discrete boundary wrapping, lattice-axis alignment, or post-hoc parameter tuning.

## 2. Falsification Criterion
The hypothesis will be refuted if any of the following occur:
1. The minimum separation between the two gliders in the active run (with coupling strength eta = 2.0 and smoothing sigma = 1.5) is not closer than that of the vacuum control (eta = 0.0) by at least 2.0 lattice units (i.e., d_vacuum_min - d_active_min < 2.0).
2. The mutual attraction disappears or varies significantly (difference in separation trajectory > 1.75 lattice units) when the initial positions and velocities are rotated through any of the O_h symmetry group operations.
3. Any glider or its non-zero latency field touches the boundaries of the L = 64 grid during the T = 80 steps, indicating a boundary leak.
4. Perfect bit-conservation is violated during the active simulation run (indicating the latency gradient breaks the glider structure).

## 3. Proposed Method
1. Modify or create a simulation script (e.g., `src/non_periodic_attraction.py` or modify the existing physics runner) to support an L = 64 grid and a zero-padded FFT solver for the latency field:
   - Pad the L x L x L density grid to 2L x 2L x 2L with zeros before performing FFT.
   - Convolve with a Gaussian kernel (sigma = 1.5) and crop the resulting latency field back to L x L x L.
2. Set up the initial conditions:
   - Two LUT-08 sub-light gliders placed at a separation of 16-20 lattice units in the central region of the 64^3 grid.
   - Set their initial velocities such that they would pass each other at a closest distance of 6-8 lattice units in the vacuum control.
3. Run the following simulation groups:
   - Active Run (eta = 2.0, non-periodic FFT).
   - Vacuum Control (eta = 0.0).
   - Rotated Active & Vacuum Runs: Apply O_h rotations to the initial state to verify isotropy.
4. Measure and save the separation distance d(t) as a function of step t, verify bit conservation, and confirm that the latency/density at the boundaries remains exactly zero.

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
