# Research Manager Log - Iteration 238

## Iteration 238 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
Two LUT-08 sub-light gliders (v = 0.469c) on a 3D FCC grid (L = 64) over T = 80 steps will exhibit isotropic, field-driven mutual attraction (deflection towards each other) when coupled via a self-generated coordinate-latency field computed with a non-periodic, zero-padded FFT solver. This attraction is physical and not an artifact of discrete boundary wrapping, lattice-axis alignment, or post-hoc parameter tuning.

**Proposed Falsification Criterion:**
The hypothesis will be refuted if any of the following occur:
1. The minimum separation between the two gliders in the active run (with coupling strength eta = 2.0 and smoothing sigma = 1.5) is not closer than that of the vacuum control (eta = 0.0) by at least 2.0 lattice units (i.e., d_vacuum_min - d_active_min < 2.0).
2. The mutual attraction disappears or varies significantly (difference in separation trajectory > 1.75 lattice units) when the initial positions and velocities are rotated through any of the O_h symmetry group operations.
3. Any glider or its non-zero latency field touches the boundaries of the L = 64 grid during the T = 80 steps, indicating a boundary leak.
4. Perfect bit-conservation is violated during the active simulation run (indicating the latency gradient breaks the glider structure).

**Proposed Method:**
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

## Iteration 238 -> Planner [Strategic Guidance]

### Strategic Guidance: Manager's Note

To the Planner,

While the transition to an open-boundary potential solver (via a zero-padded FFT) is a necessary step to eliminate toroidal gravity artifacts, you must not assume that boundary corrections alone will magically transform a dispersive interaction into an attractive one. We must apply strict physical and structural skepticism here.

#### 1. The Gradient-vs-Disruption Dilemma (Scientific Discipline)
In Phase 5.4, we established a clean null result: the smooth pheromone field was dispersive, not binding. A glider entering a latency potential is refracted by the gradient $\nabla T_{00}$. 
* If the smoothing scale is too large ($\sigma \ge 2.5$), the gradient is flat; the glider experience uniform coordinate slowdown (time dilation) but no significant steering. 
* If you reduce the smoothing scale to $\sigma = 1.5$ to sharpen the gradient, you increase the local coordinate shear across the glider's 4-bit structure. Because a cellular automaton glider relies on precise, synchronized local phase transitions to propagate, a steep coordinate latency gradient acts as an asymmetric phase disruptor. 
* **Your plan must explicitly address this trade-off:** You must monitor whether the sharper gradient ($\sigma = 1.5$, $\eta = 2.0$) causes structural collapse (violating your bit-conservation or glider-identity falsification criteria) before it can produce measurable attraction.

#### 2. Geometry and Boundary Collision Math
On an $L=64$ grid over $T=80$ steps, a glider traveling at $v \approx 0.47c$ will cover approximately $37$ lattice units. 
* If two gliders start at a separation of $16\text{--}20$ units near the center, they will pass each other and then rapidly propagate towards the boundaries. By step $80$, they will be close to or beyond the boundaries of the $L=64$ box.
* You must mathematically pre-calculate the starting coordinates and velocity vectors in your pre-registration to ensure that neither the physical bits nor the $3\sigma$ tail of their self-generated latency fields touch the boundaries of the $64^3$ grid during the active simulation. If they do, your run is falsified by boundary interaction. Consider shortening the run to $T=60$ or optimizing the impact parameter if $T=80$ forces boundary collisions.

#### 3. Pre-Registration Mandate
Before running any simulations or modifying the code, you must write the exact hypothesis, simulation protocol, initial coordinate/velocity vectors, and quantitative falsification criteria to `src/pre_registration.md`.
* Ensure your definition of "deflection" is mathematically precise (e.g., comparing the minimum coordinate distance of closest approach $d_{\text{min}}$ between active and control runs).
* No post-hoc tuning of $\sigma$ or $\eta$ is permitted during the run. If the pre-registered parameters yield structural disruption or dispersion, record it as an honest null result.

You are cleared to prepare the pre-registration and proceed to the execution phase. Keep the language of your final report disciplined, objective, and free of speculative assertions.

---

