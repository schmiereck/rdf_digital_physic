# Research Goal: Emergence of Digital Physics (Bit-Grid Universe) — Continuation

This document defines the next research arc of the project. It extends the original master plan in [`goal.md`](goal.md), which covered Phases 1–4 (1D foundations → 2D hex collisions → 3D Cuboctahedron / D4 spacetime). As of iter_232, Phases 1–4 are fully completed and Phase 5 has been opened by the research manager (see `manager_log.md`).

The overarching research question remains unchanged: **Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.**

Phases below are executed **sequentially**. Later phases may be re-scoped based on the outcomes of earlier ones.

---

## Savegame — Confirmed Knowledge (as of iter_232)

Extends the table in `goal.md §4.1`. New agents must read this before planning.

| Fact | Iterations |
|------|------------|
| Stable v=0.469c sub-light glider on 2D hex grid (trigonometric toroidal CoM) | iter_222 |
| Collision regimes of v=0.469c glider: strict locality, chaotic explosion, perfect mutual annihilation | iter_223 |
| 3D FCC CA engine with 12-channel cuboctahedron neighborhood; 4 stable 3D gliders under O_h symmetry | iter_224 |
| Gravitational time dilation via local computational latency, factor up to 2.6 | iter_224 |
| 2D+1 / 3D+1 spacetime projection of (4D) FCC lattice; emergent speed of light c=1; Lorentz γ validated at 2.22e-16 | iter_225, iter_226 |
| Emergent Shapiro delay and Fermat gravitational lensing on 3D+1 D4 spacetime | iter_227 |
| Coupled 3D+1 LGCA with local latching: perfect bit conservation, Shapiro delay, Fermat lensing characterized | iter_229 |
| Dynamic frame-dragging and Doppler-like Shapiro asymmetry from a moving mass source | iter_231 |
| **Cavendish unit test:** bidirectional gravitational deflection of a 3D sub-light glider (LUT-08) in a static mass background — *Asymmetric Zitterbewegung* mechanism validated | iter_232 |

Stable building blocks now available for downstream work:
- **2D hex:** v=1c glider `g10_rule_001`; v=0.469c sub-light glider (Rule A, `champion_rule_perfect.json`).
- **3D FCC:** 4-bit sub-light glider `LUT-08` (`archive/iter_224/results/glider_00_lut08_sub03.json`).
- **3D+1 D4:** coupled LGCA engine with local latching/trapping; dynamic latency field as $T_{00}$ analog.

---

## Phase 5: Discrete General Relativity ⟳ IN PROGRESS

**Hypothesis:** Mass-energy density acts as a self-generated local source of coordinate latency. When two or more mass packets are present, their latency fields couple through the lattice and produce mutual gravitational dynamics indistinguishable in qualitative behavior from continuum GR.

### Phase 5.1 — Cavendish Unit Test ✓ COMPLETED (iter_232)
A propagating 3D sub-light glider is deflected by a static mass background through coordinate latency only.

### Phase 5.2 — Self-Consistent Mutual Two-Body Attraction ⟳ ACTIVE
* **Goal:** Two LUT-08 sub-light gliders, each acting as a local source of dynamic coordinate latency (pheromone-like $T_{00}$ analog: deposition + temporal decay $\gamma$ + spatial smoothing $\sigma$), bias each other's trajectories and show mutual deflection while maintaining perfect bit conservation.
* **Open issue:** Spatial Gaussian smoothing dilutes the locally-deposited latency below the trapping threshold (iter_233/234). Acceptable resolutions include adaptive thresholding, gradient-based trapping rules, anisotropic smoothing, or any strictly local alternative to the pheromone scheme — provided bit conservation and O_h symmetry are preserved.
* **Milestone:** Two-body unit test on a $32^3$ toroidal grid showing growing (non-transient) mutual approach over ≥80 steps; vacuum control (no latency deposition) shows zero deflection.

### Phase 5.3 — Orbital Dynamics
* **Goal:** Demonstrate a sustained bound state (closed or quasi-closed orbit) of two mass packets on the lattice.
* **Milestone:** Trajectory data exhibiting ≥1 full periapsis return without dispersion.

### Phase 5.4 — N-Body Stability
* **Goal:** Characterize three- and many-body configurations: stability regimes, hierarchical groupings, escape velocities.
* **Milestone:** Phase diagram of bound vs. unbound regimes for N = 3 … 8 mass packets.

### Phase 5.5 — Gravitational Radiation
* **Goal:** Detect wave-like emission from accelerated or orbiting binaries in the latency field; verify that radiation carries away coordinate energy (orbit decay).
* **Milestone:** Measurable far-field latency perturbation correlated with binary orbital frequency.

---

## Phase 6: Quantum Emergence

**Hypothesis:** Quantum-mechanical phenomena (probability, interference, entanglement) emerge from ensemble statistics over deterministic glider trajectories in a discrete configuration space, without adding any probabilistic primitive to the underlying rules.

### Phase 6.1 — Statistical Superposition
* **Goal:** Construct ensembles of glider initial conditions (or rule-equivalent symmetric setups) whose aggregate behavior reproduces a probability distribution over paths.

### Phase 6.2 — Interference Patterns
* **Goal:** Build a discrete double-slit analog: a glider source, two lattice "slits," a downstream detector array. Demonstrate constructive/destructive interference fringes in arrival statistics.

### Phase 6.3 — Entanglement Analog
* **Goal:** Produce correlated glider pairs from a common-origin event. Verify that measurement-like operations on one member impose deterministic constraints on the other consistent with Bell-type statistics on a hidden-variable lattice.

### Phase 6.4 — Wavefunction Analog
* **Goal:** Derive a continuum probability density (or amplitude) from many-trial glider statistics. Test whether the resulting density satisfies a discrete Schrödinger-like evolution.

---

## Phase 7: Particle Zoo

**Hypothesis:** Beyond the LUT-08 glider, the lattice admits a discrete spectrum of stable propagating patterns that can be classified by conserved quantities, forming an emergent particle taxonomy with mass, charge, and chirality analogs.

### Phase 7.1 — Glider Taxonomy
* **Goal:** Systematic search for and classification of sub-light glider species on the 3D FCC and 3D+1 D4 lattices. Catalogue by bit-count, period, velocity, internal symmetry.

### Phase 7.2 — Charge & Chirality Analogs
* **Goal:** Identify conserved quantities beyond total bit-count (e.g. handedness, parity, internal phase) that survive propagation and collision. Test for additive conservation across interactions.

### Phase 7.3 — Antiparticles
* **Goal:** Construct time-reversed counterparts of known gliders. Verify CPT-like symmetries and that particle/antiparticle pairs annihilate cleanly back to vacuum-like states.

### Phase 7.4 — Pair Production & Annihilation
* **Goal:** Demonstrate high-energy glider collisions that produce new particle pairs from kinetic bit-energy, and the reverse process (annihilation into propagating radiation).

---

## Phase 8: Anchoring to Measurable Physics

**Hypothesis:** Dimensionless physical constants (gravitational coupling, fine-structure constant, mass ratios) are determined by pure lattice geometry. The lattice model must produce at least one falsifiable, quantitative prediction that distinguishes it from continuum GR/QM.

### Phase 8.1 — Dimensionless Constants from Geometry
* **Goal:** Compute lattice analogs of $G$, $\alpha$, and mass ratios from the geometry of the D4 lattice and the discovered particle spectrum (Phase 7), without free parameters.

### Phase 8.2 — Unit Calibration
* **Goal:** Establish a mapping from lattice units (cell, tick) to SI units (m, s, kg) via one or more known constants ($c$, $\hbar$, $G$).

### Phase 8.3 — Falsifiable Predictions
* **Goal:** Identify at least one quantitative prediction (e.g. discreteness signature, deviation at extreme curvature, modified dispersion relation, lattice-scale anisotropy) where the bit-grid model differs measurably from continuum physics.

### Phase 8.4 — Cross-Check Against Experiment
* **Goal:** Compare Phase 8.3 predictions against published experimental bounds (cosmic-ray dispersion, gravitational-wave timing, atomic-clock comparisons, etc.). Report agreement or refutation.

---

## Success Criteria

* **Each phase** terminates with a milestone artifact (`RESEARCH-RESULT-<iter>.md`), a reproducible code path, and an updated Confirmed Knowledge entry.
* **Each sub-phase** must preserve the project-wide invariants: strict locality, binary purity, O_h-symmetry of the underlying rules, reversibility, bit conservation. Violations require explicit justification and a discussion of how the broken invariant might be re-established at a later stage.

## Technical Constraints

Inherited unchanged from `goal.md §7`: strict locality, binary purity (no floats in the physics engine), hardware symmetry (O_h-invariance of rules), per-iteration manual release.
