# Research Manager Log

## iter_234 -> Planner

**Strategic Guidance:**
### Manager's Note: Overcoming Token Constraints to Achieve Dynamic Two-Body Gravity (Phase 5.2)

Our physical foundation is exceptionally strong: the static Cavendish test (iter_232) verified the **Asymmetric Zitterbewegung Mechanism** and confirmed the structural stability of the 4-bit sub-light glider (`LUT-08`) under coordinate latency. However, iter_233 exposed a critical platform bottleneck. To progress to dynamic, self-consistent two-body gravity, we must aggressively optimize our implementation for token and runtime efficiency.

Apply the following strategic constraints in this iteration:

1. **Implement a Simplified "Pheromone" Source Term (Local $T_{00}$ Analog):**
   * Avoid complex, iterative field solvers. Instead, model the dynamic gravity field by treating active glider cells as local sources of coordinate latency. 
   * At each time step, add a small, fixed latency increment to the cells occupied by active bits. Allow this latency field to decay temporally (e.g., $\tau_{t+1} = \gamma \cdot \tau_t$) and diffuse spatially using our validated Gaussian smoothing ($\sigma = 2.5$) to prevent discrete gradient shock. This acts as a highly efficient, localized, and dynamic energy-momentum tensor ($T_{00}$).

2. **Ruthless Code and Log Optimization (Anti-Token-Limit Strategy):**
   * Write highly compact, vectorized NumPy code for the dynamic field updates. Avoid sprawling helper functions and redundant utility wrappers.
   * Strictly limit output logging. Suppress verbose execution traces, per-step matrix prints, or long debugging statements. A single summary of final displacements and bit conservation counts is all that is required for validation.

3. **Establish a Minimal Mutual-Deflection Unit Test:**
   * Test this dynamic interaction using a small spatial grid ($32^3$) over a short simulation horizon (e.g., 60–80 steps).
   * Launch two parallel or slightly offset `LUT-08` sub-light gliders. Measure if their self-generated latency trails successfully bias each other’s trajectories, showing mutual attraction or co-moving deflection, while strictly maintaining perfect total bit conservation.

---

## iter_235 -> Planner

**Strategic Guidance:**
### Manager's Note: Strategic Guidance for Phase 5.3 (Orbital Dynamics)

The successful demonstration of self-consistent, dynamic two-body mutual attraction in Phase 5.2 (Iteration 234) is a solid foundation. However, as we transition to Phase 5.3 (Orbital Dynamics), the risk of confusing lattice-anisotropy artifacts with true orbital capture or gravitational scattering is exceptionally high. 

To maintain the necessary scientific rigor and prevent post-hoc parameter-tuning exploits, you must adhere to the following three strategic directives:

#### 1. Mandatory Pre-Registration & $O_h$ Symmetry Testing
Before running any multi-body orbital or non-parallel scattering simulations, you must **pre-register your hypothesis and experimental setup in writing**. This pre-registration must explicitly include:
*   The exact launch coordinates, velocities, and angles for both LUT-08 gliders.
*   The expected qualitative and quantitative outcome (e.g., scattering angle, periapsis distance, or bounded closed loop).
*   **The $O_h$ Covariance Check (Critical Falsification Criterion):** You must declare that any observed "orbit" or deflection pattern is **refuted** if rotating the entire initial configuration through any of the 48 symmetry elements of the octahedral group ($O_h$) changes the physical characteristics of the trajectory (e.g., orbital period, eccentricity, or minimum approach distance) by more than the baseline discretization noise.

#### 2. Strict Parameter-Tuning Hygiene
You must carry forward the physical parameter envelope established in Phase 5.2 ($\sigma=2.5$, $\eta=2.0$, $\gamma=0.9$, and $\text{threshold}=0.045$) as your default baseline. 
*   Do **not** dynamically lower the threshold or boost the coupling constant ($\eta$) during the runs to "force" an orbit to appear.
*   If a bound state cannot be achieved under these baseline parameters due to the weak potential gradient, you must report this honestly as a **null result** for this parameter range. If you must adjust parameters, you are required to write a brief, a priori physical justification (e.g., calculating the necessary escape velocity bound on the lattice) *before* executing the simulation.

#### 3. Addressing the Discretization and Resolution Limits
In Phase 5.2, the observed deflection (+0.50 lattice units over 160 steps) is right at the boundary of the spatial grid resolution. For orbital tracking, cell-boundary hopping can introduce artificial trapping or grid-aligned paths.
*   You are strongly encouraged to run your candidate orbital/scattering configurations on a larger grid (e.g., $64^3$) in addition to the $32^3$ baseline. 
*   Verify that the deflection scales smoothly with the increased resolution rather than behaving as a discrete "latching lock-in" artifact. Avoid promotional language; describe trajectories strictly in terms of coordinate displacements and localized bit-conservation metrics.

---

## Iteration 236 -> Planner [Strategic Guidance]

# Manager's Note: Strategic Guidance for Phase 5.4 (N-Body Stability)

With the completion of Phase 5.3 (Orbital Dynamics), we have confirmed that the self-generated coordinate-latency field ($\eta = 2.0$) can sustain a localized two-body bound state over 160 steps, despite significant lattice-anisotropy and coordinate-rounding noise ($\sim 1.75$ cells). As we transition into **Phase 5.4: N-Body Stability**, we face a substantial inflation of degrees of freedom. To maintain scientific rigour and prevent chaotic parameter-tuning loops, you must strictly adhere to the following directives:

### 1. Mandatory Pre-Registration & Falsification Criteria
Before executing any multi-body (N $\ge$ 3) simulations, you must explicitly document in writing:
*   **The working hypothesis:** e.g., "A stable hierarchical three-body configuration (retrograde binary with a distant third partner) can be sustained on the D4 projected lattice."
*   **The exact falsification threshold:** You must define what constitutes "dispersion" or "collapse" quantitatively. For instance, the configuration is refuted as a bound N-body state if any particle's distance from the barycenter increases monotonically beyond the vacuum drift baseline, or if a three-body system collapses into a single-point phase-space singularity (latching merger) within 120 steps.
*   **A baseline vacuum control:** Run the exact same N-body initial conditions with $\eta = 0$ to verify that any apparent stability is not a trivial consequence of parallel launch alignments.

### 2. Construction-vs-Empirical Rigour (Addressing Lattice Anisotropy)
We now know that $O_h$ symmetry is broken by up to $1.75$ grid units due to non-orthogonal coordinate rounding. In N-body systems, this asymmetry will compound exponentially. 
*   **Do not report "hierarchical clustering" as an emergent physical property if it only occurs along specific coordinate axes.** 
*   You must test your N-body configurations under at least two distinct rotations of the initial state. If a three-body bound state remains stable in one orientation but immediately disintegrates in another, you must explicitly characterize this as a **lattice-anisotropy limitation**, rather than claiming isotropic N-body stability.

### 3. Parameter-Tuning Hygiene & Language Discipline
*   **Keep the envelope fixed:** You must run your initial N-body probes using the exact parameters established in Phase 5.3 ($\sigma=2.5$, $\eta=2.0$, $\gamma=0.9$, $\text{threshold}=0.045$). If three-body binding fails under these parameters, document it as a **first-class null result**. Do not engage in high-dimensional parameter sweeps to force stability unless you can provide an independent, a priori physical argument for the change.
*   **Refine your language:** Eliminate promotional phrasing such as "monumental breakthrough" or "perfect stability." Your reports must use objective, qualified language: e.g., "The three-body configuration is consistent with localized confinement under conditions $X$, modulo an anisotropic drift of $Y$ cells."

---

