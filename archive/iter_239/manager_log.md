# Research Manager Log - Iteration 239

## Iteration 239 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
In the 2D hexagonal Cellular Automaton under the v=0.469c sub-light glider rule ('champion_rule_perfect.json'), a coherent superposition of two gliders (simulated together on a single grid) exhibits non-linear, phase-coherent interference that is fundamentally absent from the incoherent mixture of independent single-glider runs. Specifically, over an ensemble of initial configurations parametrized by transverse spatial offset \Delta y \in [-4, 4] and relative temporal phase delay \Delta t \in [0, 12] (spanning the glider's internal cycle), the system exhibits discrete, highly structured regions of perfect mutual annihilation (representing destructive interference, where N_{gliders} = 0 and final bits = 0) and phase-dependent deflection/transmission (representing constructive interference), whose boundaries vary periodically with the relative phase \Delta t.

**Proposed Falsification Criterion:**
The hypothesis will be proven false if any of the following quantitative observations are made:
1. The joint simulation is trivially linear, meaning the active state is always the bitwise OR of the independent control runs: S_{act}(T) = S_A(T) \lor S_B(T) for all configurations, showing no mutual interaction or annihilation.
2. The collision outcomes are completely phase-insensitive, meaning that changing the relative time delay \Delta t across the entire glider period has no effect on whether the gliders annihilate, transmit, or deflect (i.e., the outcome depends solely on the spatial offset \Delta y).
3. The outgoing probability distribution of the active runs is a simple spatial translation or smearing of the input distribution, showing no phase-dependent modulation, interference fringes, or splitting into new discrete scattering channels.

**Proposed Method:**
1. Locate the champion sub-light glider rule 'champion_rule_perfect.json' and its stable glider seed from 'archive/iter_222/' or 'archive/iter_223/'.
2. Implement a 2D hexagonal CA simulator with absorbing boundary conditions on a grid of size 128 x 128 to prevent wrapped gliders from re-colliding and causing boundary artifacts.
3. Define two glider sources that launch gliders towards a central intersection point (e.g., at a 120-degree or 180-degree angle to test different collision symmetries).
4. Generate a 2D ensemble of 117 configurations by sweeping the transverse spatial offset \Delta y from -4 to 4 lattice units and the relative temporal phase delay \Delta t from 0 to 12 steps.
5. For each configuration, run three simulations for T = 150 steps:
   - Active: both gliders launched together on the same grid.
   - Control A: only glider A launched.
   - Control B: only glider B launched.
6. Record the final bit count, the number of surviving gliders, and their outgoing velocities/angles for each run.
7. Classify the active outcomes into four discrete categories: Annihilation (destructive interference), Transmission (survival without path deviation), Deflection (constructive interference with scattering), and Chaos (instability).
8. Map the phase diagram of outcomes over (\Delta y, \Delta t), plot the probability of annihilation P(A) as a function of relative phase \Delta t, and compare the coherent joint distribution against the incoherent sum/mixture of the controls.

---

## Iteration 239 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance & Skeptical Critique

#### 1. The Language & Construction Warning: Soliton Scattering is not Quantum Interference
Your proposed plan to collide two deterministic gliders and sweep their relative phase ($\Delta t$) and offset ($\Delta y$) is a valuable exercise, but **you must not label this as "quantum superposition" or "destructive/constructive interference."** 

In a deterministic, local Cellular Automaton, two localized structures colliding and either annihilating, scattering, or passing through each other is the classical physics of **solitons** or discrete particles. 
*   In Conway's Game of Life, glider collisions are highly phase-sensitive (a delay of 1 tick completely changes the outcome). Nobody claims this is quantum mechanics; it is simply classical, discrete, deterministic multi-body dynamics.
*   **The Construction-vs-Empirical Test:** If you run this experiment and find that different phases yield different deterministic outcomes (annihilation vs. deflection), you have not discovered "quantum wave-particle duality"—you have merely mapped the classical scattering cross-section of your $v=0.469c$ glider.

#### 2. Strategic Pivot: Choose Your Path
You must choose one of the following two directions for this iteration, and state it clearly in your pre-registration:

*   **Path A: Classical Scattering Characterization (Highly Recommended for Consolidating Phase 5/7 Blockers)**
    Reframe the plan honestly. Do not claim quantum emergence. Instead, perform a high-resolution, systematic study of the **classical phase-dependent scattering and annihilation cross-sections** of the $v=0.469c$ glider. This provides the necessary "particle interaction" foundation for the Particle Zoo (Phase 7) or potential discrete-bit contact gravity.
    *   *Falsification Criterion:* The hypothesis (that collision outcomes are phase-dependent) is refuted if the outcome is invariant under temporal shifts $\Delta t$ mod $P$ (where $P$ is the glider's internal period), or if the interaction cross-section does not scale periodically with $\Delta t$.

*   **Path B: A Genuine Double-Slit Experiment (True Phase 6.2)**
    If you wish to remain in Phase 6 (Quantum Emergence), you must design an experiment with **statistical content** and an ensemble of trials.
    *   *Protocol:* Build a static double-slit barrier on a 2D hex or 3D grid. Launch a spatial ensemble of single gliders (e.g., varying their initial lateral position $y$ slightly to represent a beam). 
    *   *Measure:* The spatial distribution of where the gliders end up on a detector screen far behind the barrier under three conditions: (1) Left slit open, (2) Right slit open, (3) Both slits open.
    *   *Falsification Criterion:* The quantum interference hypothesis is **refuted** if the joint probability distribution is simply the sum of the individual slit distributions: $P_{\text{both}}(x) = \frac{1}{2}(P_{\text{left}}(x) + P_{\text{right}}(x))$. To prove quantum-like interference, you must show a statistically significant deviation from this classical sum (fringes) without the gliders colliding with each other.

#### 3. Pre-Registration Mandate
Before writing or executing any simulation code, you must write your final, rigorous, and mathematically precise hypothesis, protocol, and falsification criteria to `src/pre_registration.md`. Ensure that the language used is strictly disciplined: avoid words like "breakthrough" or "quantum" unless you are executing **Path B** and can mathematically justify how the lattice dynamics bypass the classical summation of probabilities.

---

