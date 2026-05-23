# RDF Scientific Pre-Registration

*   **Iteration:** 239
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
In the 2D hexagonal Cellular Automaton under the v=0.469c sub-light glider rule ('champion_rule_perfect.json'), a coherent superposition of two gliders (simulated together on a single grid) exhibits non-linear, phase-coherent interference that is fundamentally absent from the incoherent mixture of independent single-glider runs. Specifically, over an ensemble of initial configurations parametrized by transverse spatial offset \Delta y \in [-4, 4] and relative temporal phase delay \Delta t \in [0, 12] (spanning the glider's internal cycle), the system exhibits discrete, highly structured regions of perfect mutual annihilation (representing destructive interference, where N_{gliders} = 0 and final bits = 0) and phase-dependent deflection/transmission (representing constructive interference), whose boundaries vary periodically with the relative phase \Delta t.

## 2. Falsification Criterion
The hypothesis will be proven false if any of the following quantitative observations are made:
1. The joint simulation is trivially linear, meaning the active state is always the bitwise OR of the independent control runs: S_{act}(T) = S_A(T) \lor S_B(T) for all configurations, showing no mutual interaction or annihilation.
2. The collision outcomes are completely phase-insensitive, meaning that changing the relative time delay \Delta t across the entire glider period has no effect on whether the gliders annihilate, transmit, or deflect (i.e., the outcome depends solely on the spatial offset \Delta y).
3. The outgoing probability distribution of the active runs is a simple spatial translation or smearing of the input distribution, showing no phase-dependent modulation, interference fringes, or splitting into new discrete scattering channels.

## 3. Proposed Method
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
*Created automatically by the RDF Orchestrator prior to iteration execution.*
