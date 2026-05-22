# Research Goal: Emergence of Digital Physics (Bit-Grid Universe) — Continuation

This document defines the next research arc of the project. It extends the original master plan in [`goal_1-4.md`](goal_1-4.md), which covered Phases 1–4 (1D foundations → 2D hex collisions → 3D Cuboctahedron / D4 spacetime). As of iter_232, Phases 1–4 are fully completed and Phase 5 has been opened by the research manager (see `manager_log.md`).

The overarching research question remains unchanged: **Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.**

Phases below are executed **sequentially**. Later phases may be re-scoped based on the outcomes of earlier ones.

---

## Methodological Discipline (Falsification Protocol)

This project has a history of mistaking constructional identities for emergent physics, and of recovering "successes" through post-hoc parameter tuning (see iter_213–220, iter_233–234). To prevent this, every sub-phase below operates under the following protocol — enforced by the Research Manager (see `uroboros-rdf/rdf/core/prompts/manager_guidance_system.md`):

1.  **Pre-registration.** Before any experiment is executed, the Planner declares in writing (a) the working hypothesis, (b) the protocol (grid, parameters, control run), and (c) the observation that would *refute* the hypothesis. A sub-phase without a pre-registered falsification criterion is not ready to run.
2.  **Construction-vs-Empirical Check.** Before promoting a finding to "confirmed knowledge", show that the result is not derivable from the chosen geometry, projection, or symmetry alone. Results that hold to machine epsilon (~1e-16) are flagged as algebraic identities, not discoveries. Effect magnitudes at or below lattice resolution are flagged as inconclusive.
3.  **Parameter-Tuning Hygiene.** If a positive result only appeared after widening sweep ranges or lowering thresholds, it counts as **suggestive evidence at best** unless there is an independent physical argument for the chosen parameters, stated *before* the result is known.
4.  **Honest Null Results.** A clearly-documented refutation is a first-class outcome. Each phase below explicitly lists what a "null verdict" looks like, and a milestone report may be issued for one.
5.  **Language Discipline.** Milestone reports must avoid promotional vocabulary ("breakthrough", "monumental", "proves", "perfectly", "emerges organically" without a stated mechanism). Required vocabulary: *consistent with*, *evidence for*, *does not refute*, *refuted by*.

Every sub-phase below carries a **Falsification** field. The phase cannot be marked complete until that field has been evaluated against actual observations.

---

## Savegame — Confirmed Knowledge (as of iter_232)

Extends the table in `goal_1-4.md §4.1`. New agents must read this before planning. Entries marked **(C)** are confirmed empirical; **(D)** are definitional / constructional and should not be cited as evidence of emergent physics.

| Fact | Iterations | Type |
|------|------------|------|
| Stable v=0.469c sub-light glider on 2D hex grid (trigonometric toroidal CoM) | iter_222 | C |
| Collision regimes of v=0.469c glider: strict locality, chaotic explosion, perfect mutual annihilation | iter_223 | C (qualitative) |
| 3D FCC CA engine with 12-channel cuboctahedron neighborhood; 4 stable 3D gliders under O_h symmetry | iter_224 | C |
| Gravitational time dilation via local computational latency, factor up to 2.6 | iter_224 | C (under stated coupling) |
| 2D+1 / 3D+1 spacetime projection of (4D) FCC lattice; "speed of light" c=1 along [1,…,1] axis | iter_225, iter_226 | D (projection geometry) |
| Lorentz γ formula evaluated to ~2e-16 along chosen worldlines | iter_225, iter_226 | D (algebraic identity in float64) |
| Shapiro delay and Fermat lensing under externally-imposed latency field | iter_227, iter_229 | C (effect), D (qualitative GR analogy) |
| Frame-dragging-like deflection under a moving externally-imposed mass source | iter_231 | C (effect), D (mechanism is by construction) |
| Cavendish unit test: bidirectional gravitational deflection of LUT-08 in a static mass background, ±0.5 lattice units over 80 steps on 32³ grid | iter_232 | **C, but at lattice resolution — needs replication at finer resolution to consolidate** |

Stable building blocks now available for downstream work:
- **2D hex:** v=1c glider `g10_rule_001`; v=0.469c sub-light glider (Rule A, `champion_rule_perfect.json`).
- **3D FCC:** 4-bit sub-light glider `LUT-08` (`archive/iter_224/results/glider_00_lut08_sub03.json`).
- **3D+1 D4:** coupled LGCA engine with local latching/trapping; dynamic latency field as $T_{00}$ analog.

---

## Phase 5: Discrete General Relativity ⟳ IN PROGRESS

**Hypothesis:** Mass-energy density acts as a self-generated local source of coordinate latency. When two or more mass packets are present, their latency fields couple through the lattice and produce mutual gravitational dynamics that go beyond what the construction trivially implies.

### Phase 5.1 — Cavendish Unit Test ✓ COMPLETED (iter_232)
A propagating 3D sub-light glider is deflected by a static externally-imposed mass background through coordinate latency only. **Open concern:** the observed deflection (±0.5 lattice units) is at lattice resolution and shows a 2:1 asymmetry. Before this is consolidated into Phase 5 foundations, a re-run on a ≥64³ grid is required to confirm the effect is not a discretisation artefact (carried into Phase 5.2 as a side task).

### Phase 5.2 — Self-Consistent Mutual Two-Body Attraction ⟳ ACTIVE
* **Goal:** Establish whether two LUT-08 sub-light gliders, each acting as a local source of dynamic coordinate latency, bias each other's trajectories beyond what is reproducible by the vacuum control or by free parameter tuning.
* **Sub-goal A (the current blocker): resolve the σ-dilution problem honestly.** The pheromone scheme (deposition + temporal decay γ + spatial Gaussian smoothing σ=2.5) used in iter_233/234 dilutes the locally-deposited latency below the trapping threshold. *Acceptable outcomes:*
  - Find a strictly-local mechanism (gradient-based trapping, anisotropic smoothing, direct bit-contact latching, factorised tensor field) that produces mutual deflection from parameters declared *before* the run — and demonstrate it.
  - Or: conclude that the simple pheromone $T_{00}$-analog cannot produce mutual gravity at this lattice scale, document the negative result, and either move to a redesigned mechanism or to Phase 5.3 with the caveat noted.
  Threshold-tuning until "something" appears is **not** an acceptable outcome.
* **Falsification:**
  - Refuted if, under any mechanism declared in advance, the mutual approach over ≥80 steps is not larger than the vacuum control by at least 2× the lattice resolution.
  - Refuted if the effect disappears when initial conditions are rotated through one O_h symmetry element (i.e. the "attraction" is in fact a lattice-axis artefact).
  - Refuted if the only way to obtain the effect is to widen the parameter sweep envelope after seeing the result.
* **Milestone:** Either a confirmed mutual approach satisfying the falsification protocol, or a documented null result with a clear statement of which mechanisms have been ruled out.

### Phase 5.3 — Orbital Dynamics
* **Goal:** Demonstrate a sustained bound state (closed or quasi-closed orbit) of two mass packets on the lattice, assuming Phase 5.2 yields a usable attraction mechanism.
* **Falsification:**
  - Refuted if the apparent "orbit" is a lattice-anisotropy drift: test by rotating initial conditions through the O_h group; orbital plane and period must transform covariantly.
  - Refuted if the observed period differs from the Keplerian prediction (computed from the measured Phase 5.2 coupling strength) by more than 30 % at the start, or shows monotonic drift inconsistent with radiation reaction.
* **Milestone:** Trajectory data exhibiting ≥1 full periapsis return with O_h-covariant transformation properties.

### Phase 5.4 — N-Body Stability
* **Goal:** Characterize three- and many-body configurations: stability regimes, hierarchical groupings, escape velocities.
* **Falsification:**
  - Refuted (as "stability") if extending the simulation by 5× turns the supposed bound state into dispersion — i.e. the stability was just slow drift.
  - Refuted (as physics) if the phase diagram of bound vs unbound regions is not invariant under O_h rotations of the initial configuration.
* **Milestone:** Phase diagram of bound vs. unbound regimes for N = 3 … 8 mass packets, with O_h-invariance check.

### Phase 5.5 — Gravitational Radiation
* **Goal:** Detect wave-like emission from accelerated or orbiting binaries in the latency field; verify that radiation carries away coordinate energy (orbit decay).
* **Falsification:**
  - Refuted if the supposed "wave" wavelength changes when the binary is translated by a fraction of a lattice cell (numerical artefact).
  - Refuted if the angular emission pattern is not at least approximately quadrupolar.
  - Refuted if orbit decay does not correlate with integrated far-field latency perturbation.
* **Milestone:** Measurable far-field latency perturbation correlated with binary orbital frequency, exhibiting the expected angular pattern.

---

## Phase 6: Quantum Emergence

**Hypothesis:** Quantum-mechanical phenomena (probability, interference, entanglement) emerge from ensemble statistics over deterministic glider trajectories in a discrete configuration space, without adding any probabilistic primitive to the underlying rules. *Caution: a single deterministic glider tracing a curved path is not "interference"; quantum emergence requires statistical content.*

### Phase 6.1 — Statistical Superposition
* **Goal:** Construct ensembles of glider initial conditions (or rule-equivalent symmetric setups) whose aggregate behavior reproduces a probability distribution over paths.
* **Falsification:** Refuted if the "distribution" is a single deterministic trajectory smeared by the choice of initial condition — i.e. removing the ensemble removes the effect but does not change a single-trial outcome.

### Phase 6.2 — Interference Patterns
* **Goal:** Build a discrete double-slit analog. Demonstrate constructive/destructive interference fringes in arrival statistics over many trials.
* **Falsification:**
  - Refuted if a single-glider run already shows a "fringe pattern" — that would be geometric, not quantum.
  - Refuted if the fringe spacing does not scale with the slit-detector geometry as predicted by a path-length-difference argument stated in advance.

### Phase 6.3 — Entanglement Analog
* **Goal:** Produce correlated glider pairs from a common-origin event. Test for Bell-type correlation statistics on the (hidden-variable) lattice.
* **Falsification:**
  - Refuted if the correlation can be reproduced by a trivial common-cause classical model with no measurement-context dependence.
  - The expected positive outcome is that the lattice yields *classical* Bell-bound-respecting correlations: a "quantum" violation would itself need explanation and should not be claimed without scrutiny.

### Phase 6.4 — Wavefunction Analog
* **Goal:** Derive a continuum probability density from many-trial glider statistics. Test whether the resulting density satisfies a discrete Schrödinger-like evolution.
* **Falsification:** Refuted if the recovered evolution equation is just the diffusion equation (no phase / interference content), or if the recovered "Planck-like constant" varies with the choice of binning rather than being a property of the lattice.

---

## Phase 7: Particle Zoo

**Hypothesis:** Beyond the LUT-08 glider, the lattice admits a discrete spectrum of stable propagating patterns that can be classified by conserved quantities, forming an emergent particle taxonomy with mass, charge, and chirality analogs.

### Phase 7.1 — Glider Taxonomy
* **Goal:** Systematic search and classification of sub-light glider species on the 3D FCC and 3D+1 D4 lattices. Catalogue by bit-count, period, velocity, internal symmetry.
* **Falsification:** Refuted as "taxonomy" if all discovered species are O_h-orbit-equivalent to one or two underlying patterns. Only count species in distinct O_h orbits.

### Phase 7.2 — Charge & Chirality Analogs
* **Goal:** Identify conserved quantities beyond total bit-count (e.g. handedness, parity, internal phase) that survive propagation and collision. Test for additive conservation across interactions.
* **Falsification:** Refuted if the "charge" is not additive across ≥10 independent collision events, or if it is not invariant under propagation in vacuum.

### Phase 7.3 — Antiparticles
* **Goal:** Construct time-reversed counterparts of known gliders. Verify CPT-like symmetries and that particle/antiparticle pairs annihilate cleanly back to vacuum-like states.
* **Falsification:** Refuted if "annihilation" leaves residual bits beyond a stated threshold, or if the time-reversed glider is not bit-conserving.

### Phase 7.4 — Pair Production & Annihilation
* **Goal:** Demonstrate high-energy glider collisions that produce new particle pairs from kinetic bit-energy, and the reverse.
* **Falsification:**
  - Refuted if the "produced pair" is just two halves of the input gliders with no quantitative threshold relation to input energy.
  - Refuted if the production threshold does not scale predictably with the rest-energy of the produced species (as measured in Phase 7.1).

---

## Phase 8: Anchoring to Measurable Physics

**Hypothesis:** Dimensionless physical constants (gravitational coupling, fine-structure constant, mass ratios) are determined by pure lattice geometry. The lattice model must produce at least one falsifiable, quantitative prediction that distinguishes it from continuum GR/QM. *This phase is the highest-risk and is the place where this project earns or loses the right to call itself physics.*

### Phase 8.1 — Dimensionless Constants from Geometry
* **Goal:** Express lattice analogs of $G$, $\alpha$, and at least one mass ratio in closed form, using only integers, π, and lattice-geometric quantities (no free parameters fitted to the desired output).
* **Falsification:** Refuted if the resulting expressions disagree with the real values by more than 2 orders of magnitude, **or** if any expression requires a free parameter chosen after viewing real-world data.

### Phase 8.2 — Unit Calibration
* **Goal:** Establish a mapping from lattice units (cell, tick) to SI units (m, s, kg) via at most two anchor constants. All other physical predictions must use this same mapping.
* **Falsification:** Refuted if the calibration requires being re-fit for each downstream prediction.

### Phase 8.3 — Falsifiable Predictions
* **Goal:** Identify at least one quantitative prediction (discreteness signature, deviation at extreme curvature, modified dispersion relation, lattice-scale anisotropy) whose value distinguishes the bit-grid model from continuum physics by a measurable amount.
* **Falsification:** Refuted if every proposed prediction is either (a) outside the precision of any conceivable experiment, or (b) numerically identical to continuum physics.

### Phase 8.4 — Cross-Check Against Experiment
* **Goal:** Compare Phase 8.3 predictions against published experimental bounds (cosmic-ray dispersion, gravitational-wave timing, atomic-clock comparisons, CMB anisotropy bounds, etc.).
* **Falsification:** The prediction is either compatible with current bounds (positive: still alive), or it is excluded (negative: the lattice model is ruled out in its current form). Either outcome is a publishable result.

---

## Success Criteria

* **Each sub-phase** terminates with a milestone artifact (`RESEARCH-RESULT-<iter>.md`) that follows the structure mandated by `manager_review_system.md` (Pre-Declared Hypothesis & Falsification → Protocol → Observations → Verdict → Construction-vs-Empirical Note → Limitations).
* A **null result** terminating a sub-phase is a valid success of the method and must be recorded as such, not re-framed.
* **Each sub-phase** must preserve the project-wide invariants: strict locality, binary purity, O_h-symmetry of the underlying rules, reversibility, bit conservation. Violations require explicit justification.

## Technical Constraints

Inherited from `goal_1-4.md §7`:

* **Strict Locality:** No access to non-neighboring nodes (Exception: explicit entanglement pointers to source events).
* **Binary Purity:** No use of float values within the physics engine itself (auxiliary fields like the dynamic latency $T_{00}$-analog may use floats but must be documented as such; they are not part of "the physics").
* **Hardware Symmetry:** All rules must be invariant under rotations of the cuboctahedron (O_h).
* **Resource Control:** Each iteration requires a manual release [y] after reviewing the strategy report.
