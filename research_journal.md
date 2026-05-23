# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 5 (Discrete General Relativity).
*   **Active Direction:** Fundamental restructuring of the local coupling mechanism. Phase 5.2 (Self-Consistent Mutual Two-Body Attraction) has been completed and terminated with a first-class null result. The continuous pheromone-style latency field model has been systematically falsified.
*   **Trajectory Update (Iteration 238):** Following the discovery of toroidal recurrence artifacts in Phase 5.4, we implemented a rigorous open-boundary evaluation of Phase 5.2 on a $64^3$ grid with absorbing boundaries. This test conclusively refuted the pheromone-like latency model, demonstrating that it fails to produce physically significant deflection and shatters $O_h$ coordinate covariance under rotation. We are shifting focus away from continuous field potentials toward strictly local, discrete state-transition/latching mechanics.
*   **Confidence Score:** 15% (Re-evaluated downward to reflect the definitive refutation of our primary continuous-field gravity model, forcing a return to first-principles discrete rules).

## 2. Strategic Insights & Lessons Learned
*   **The Covariance Wall:** In discrete systems, passing continuous fields (like FFT-smoothed latency) back into the CA engine causes floating-point to integer rounding errors during state updates. These sub-pixel rounding errors break the delicate internal phase transitions of moving gliders, especially when rotated under $O_h$ (e.g., $g=10$), resulting in severe non-physical coordinate drift rather than physical attraction.
*   **The Pheromone Pseudoscience Fallacy:** Treating coordinate latency as a smooth "pheromone" that diffuses and decays is an ill-fitting continuum analogy. At small scales, it either dilutes below the interaction threshold or disrupts the structural integrity of the very particles it is meant to attract.
*   **Validation of the Skeptic Gate:** By requiring open boundaries, matching vacuum controls, and $O_h$ symmetry checks, we successfully prevented a marginal, non-covariant effect (0.25 cells of deflection) from being misidentified as physical gravity. 

## 3. Loop & Bottleneck Detection
*   **Continuum-Discrete Coupling Bottleneck:** We have identified a fundamental bottleneck: any mechanism that relies on mapping a continuous floating-point potential back onto discrete state updates (latching/trapping thresholds) will suffer from discretization noise and broken symmetry. The coupling *must* be as discrete as the CA itself to preserve exact $O_h$ covariance.

## 4. Alternate Research Paths
*   **Strictly Local Bit-Contact Latching:** Instead of a smooth potential field, explore a mechanism where gliders interact only when their local envelopes overlap (direct bit-contact). This preserves the binary purity and prevents rounding-induced drift.
*   **Integer Lattice-Field Potentials:** Investigate cellular automata models where the gravitational potential is represented by discrete integer state counters on each cell, avoiding float-to-int rounding altogether.