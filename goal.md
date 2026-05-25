# Master Research Goal: Emergence of Digital Physics (Bit-Grid Universe)

This master document defines the strategic vision, methodology, chronological roadmap, and confirmed knowledge base of the project. 

The overarching research question is: **Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.**

The universe is modeled as a distributed information system on a highly symmetric discrete lattice. The speed of light is defined by the grid topology (1 link per tick), while gravity is modeled as local coordinate latency (computational processing latency as an analog of $T_{00}$).

---

## 1. Strategic Approach: The "Unit-Test" Workflow

The search for emergent physical laws is conducted not by blind guessing in high-dimensional spaces, but through a hierarchical scaling approach where lower-dimensional environments act as validation unit tests for higher-dimensional systems:

*   **Stage 1 (1D):** Validate core constraints (reversibility, bit conservation) and search for stable, moving solitons (gliders).
*   **Stage 2 (2D Hexagonal Grid):** Introduce angular degrees of freedom to study scattering dynamics and elastic particle collisions.
*   **Stage 3 (3D Cuboctahedron / FCC):** Port the 2D hexagonal dynamics to the 12-channel symmetry group of the Face-Centered Cubic (FCC) lattice, stacks of hex planes, and eventually to 4D ($D_4$) spacetime.

---

## 2. Methodological Discipline (Falsification Protocol)

This project has a history of mistaking constructional identities for emergent physics, and of recovering "successes" through post-hoc parameter tuning (see iter_213–220, iter_233–234, iter_247). To prevent this, every sub-phase below operates under a strict falsification protocol:

1.  **Pre-registration.** Before any experiment is executed, the Planner must declare in writing (a) the working hypothesis, (b) the protocol (grid, parameters, control run), and (c) the precise observation that would *refute* the hypothesis.
2.  **Construction-vs-Empirical Check.** Show that any finding is not derivable from the chosen geometry, projection, or symmetry alone. Results that hold to machine epsilon ($\sim 1\text{e-}16$ in float64) are flagged as algebraic identities, not discoveries.
3.  **Parameter-Tuning Hygiene.** If a positive result only appears after widening sweep ranges or lowering thresholds post-hoc, it counts as suggestive evidence at best unless supported by an independent physical argument stated *before* the run.
4.  **Honest Null Results.** A clearly-documented refutation is a first-class outcome. A milestone report may be issued to catalog a null verdict.
5.  **Language Discipline.** Avoid promotional vocabulary ("breakthrough", "monumental", "proves", "perfectly", "emerges organically"). Required terms: *consistent with*, *evidence for*, *does not refute*, *refuted by*.

---

## 3. The Experimenter Architecture (Pipeline)

To navigate the exponentially large rule space of cellular automata, the framework uses a multi-stage filter architecture:

1.  **Formal Filter (Symbolic Mathematics):**
    *   **Bijectivity Audit:** Guarantees reversibility by validating that the rule is a strict bijection (permutation) of the local state space.
    *   **Bit Conservation Check:** Ensures that the Hamming weight of the input state exactly equals the Hamming weight of the output state.
    *   **Symmetry Compression:** Compresses the truth tables using the $O_h$ symmetry group of the cuboctahedron.
2.  **AI Predictor (Neural Rule Scoring):**
    *   Predicts candidate rules using Langton's Lambda parameter and complexity metrics to target the phase boundary between stagnation ("ice") and chaos ("steam").
3.  **Evolutionary Breeding Loop (Genetic Algorithm):**
    *   Sifts through candidate pools using selection pressure based on the survival time and coherence of complex structures.

---

## 4. Chronological Master Roadmap (Phases 1 to 8)

### Phase 1: The 1D Symmetry Sifter (Foundations) ✓ COMPLETED
*   **Goal:** Identification of all reversible, bit-preserving rules for a 1D grid with a 3-bit neighborhood.
*   **Milestone:** Catalog of rules that allow stable, non-dispersive propagation.
*   **Verdict/Result (iter_001–002):** Confirmed. 33 non-trivial rules identified; 22 produce $v=c$ gliders and 11 produce stable fixed points.

### Phase 2: The "Wiggle" Detector (Internal Oscillation) ✓ COMPLETED
*   **Goal:** Extend 1D systems to multiple bits per cell to enable internal degree of freedom oscillations.
*   **Milestone:** Generation of particles with effective velocities $v < c$ (mass simulation).
*   **Verdict/Result (iter_003–006, iter_018):** Confirmed. Proven by construction: period-2 oscillators ($v=0$) and $v=c/2$ composite gliders. 1D collision catalog: 8 elastic, 6 fusion, and 8 chaotic collisions.

### Phase 3: The 2D Hex Collision (Scattering) ✓ COMPLETED
*   **Goal:** Port reversibility and bit conservation to 2D hexagonal grids and characterize glider collisions.
*   **Milestone:** Discovery of a stable, moving 2D glider and validation of elastic scattering.
*   **Verdict/Result (iter_179, iter_222-223):** Confirmed.
    *   *Iteration 179:* Evolutionarily discovered the 3-bit $v=1c$ L-Tromino glider (`g10_rule_001`) with perfect bit conservation and zero dispersion.
    *   *Iteration 222:* Discovered the stable sub-light $v=0.469c$ glider (`champion_rule_perfect.json`) through advanced fitness tuning.
    *   *Iteration 223:* Collision regimes of the $v=0.469c$ glider characterized, showing strict locality, chaotic explosions, and perfect mutual annihilation.

### Phase 4: The Cuboctahedron / FCC Universe (3D to 4D Space & Spacetime) ✓ COMPLETED
*   **Goal:** Transition to the target 3D Face-Centered Cubic (FCC) lattice (12-channel neighborhood) and represent static spacetime geometries.
*   **Phases:**
    *   **Phase 4.1 (3D space with coordinate time):** 3D LGCA engine utilizing the 12 neighbors of the cuboctahedron under $O_h$ symmetry.
    *   **Phase 4.2 (2D+1 FCC Spacetime):** Treating the third dimension as a time axis; representing the speed of light as a fixed angle of inclination.
    *   **Phase 4.3 (3D+1 spacetime / D4 lattice):** Mapping the Minkowski metric to the 24-channel neighborhood of the 4D sphere packing.
*   **Verdict/Result (iter_224–226):** Confirmed. Developed the 3D FCC CA engine. Discovered the "4-bit glider" `LUT-08`. Verified Lorentz $\gamma$ formulas (algebraic identity of projection). Demonstrated gravitational time dilation (latency factor up to 2.6).

---

### Phase 5: Discrete General Relativity ⟳ IN PROGRESS

**Hypothesis:** Mass-energy density acts as a local source of coordinate latency. When multiple mass packets are present, their latency fields couple through the lattice, producing mutual gravitational attraction that goes beyond what the coordinate projection trivially implies.

*   **Phase 5.1 — Cavendish Unit Test ✓ COMPLETED (iter_232)**
    *   A propagating 3D sub-light glider composite is deflected by a static externally-imposed mass background through coordinate latency. Deflection was $\pm 0.5$ lattice units over 80 steps.
*   **Phase 5.2 — Self-Consistent Mutual Two-Body Attraction ⟳ ACTIVE**
    *   **Goal:** Establish whether two sub-light gliders, each acting as a source of dynamic latency, bias each other's trajectories.
    *   **The Block (The $\sigma$-Dilution Problem):** Pheromone-like smoothing ($\sigma=2.5$) dilutes the coordinate latency field below the trapping threshold. Furthermore, non-interacting composite gliders do not possess internal binding energy, preventing stable mutual trapping.
    *   **Action:** This phase is currently **blocked** until Phase 7.1 yields genuine, dynamically-bound gliders that can withstand localized latency perturbations.
    *   **Falsification:**
        *   Refuted if the mutual approach is not larger than the vacuum control by at least $2\times$ the lattice resolution.
        *   Refuted if the effect is a lattice-axis artifact (fails to transform covariantly under $O_h$ rotations).
*   **Phase 5.3 — Orbital Dynamics**
    *   **Goal:** Demonstrate a sustained bound state (closed orbit) of two mass packets.
    *   **Falsification:** Refuted if the orbit is a lattice-anisotropy drift (fails $O_h$ covariance) or if the period differs from the Keplerian prediction by $>30\%$.
*   **Phase 5.4 — N-Body Stability**
    *   **Goal:** Characterize stability regimes for $N = 3 \dots 8$ mass packets.
*   **Phase 5.5 — Gravitational Radiation**
    *   **Goal:** Detect wave-like emission from accelerated binaries in the latency field and verify orbit decay.

---

### Phase 6: Quantum Emergence

**Hypothesis:** Quantum-mechanical phenomena (probability, interference, entanglement) emerge from ensemble statistics over deterministic glider trajectories in a discrete configuration space, without adding any probabilistic primitives.

*   **Phase 6.1 — Statistical Superposition:** Construct ensembles of glider initial conditions that reproduce probability distributions over paths.
*   **Phase 6.2 — Interference Patterns:** Build a double-slit analog and demonstrate constructive/destructive fringes in arrival statistics.
*   **Phase 6.3 — Entanglement Analog:** Produce correlated glider pairs from a common origin and evaluate Bell-type correlation statistics.
*   **Phase 6.4 — Wavefunction Analog:** Derive a continuum probability density and test if it satisfies a discrete Schrödinger-like evolution.

---

### Phase 7: Particle Zoo & Interacting Field Theory ⟳ ACTIVE

**Hypothesis (Pivoted to Option A - Iteration 249):** The strictly local, single-cell additive collision operator $C$ physically prohibits any multi-bit binding in vacuum because it maps weight-1 states to weight-1 states. To support a diverse particle taxonomy, the LUT construction must be redesigned to allow bits to act as fields that interact. By introducing **non-additive collision LUT mutations** (where weight-$\ge 2$ configurations trigger non-linear transitions rather than independent transpositions), the lattice can support stable, dynamically-bound multi-bit gliders with non-zero binding energy.

*   **Phase 7.1 — Glider Taxonomy & Non-Additive LUT Search ⟳ ACTIVE**
    *   **Goal (Option A Precision):** Redesign the 3D FCC collision LUT to introduce non-additive transitions (specifically for weight-2 sharing and contact boundaries) while strictly maintaining bijectivity and bit conservation. Run systematic sweeps to discover genuine, dynamically-bound multi-bit gliders.
    *   **The Three-Test Coherence Verification Protocol:**
        1.  *Single-Bit Decomposition Test:* Isolating any single constituent bit of a glider must alter its propagation trajectory or speed, proving binding energy $> 0.0$.
        2.  *Interaction/Collision Coherence Test:* Glider boundaries must cohere during localized latency perturbations.
        3.  *Bit-Removal Stability Test:* Standard and rotated forms must be structurally dependent.
    *   **Falsification:**
        *   Refuted if no multi-bit configurations survive $\ge 200$ steps post-collision under any non-additive LUT variant.
        *   Refuted if any surviving states fail the Single-Bit Decomposition Test (proving they are still non-interacting composites).
        *   Refuted if the glider fails to transform covariantly under all 48 elements of the $O_h$ group.
        *   Refuted if the LUT modifications violate reversibility (bijectivity) or bit conservation.
*   **Phase 7.2 — Charge & Chirality Analogs:** Identify conserved quantities (handedness, parity, phase) that survive collisions.
*   **Phase 7.3 — Antiparticles:** Construct time-reversed counterparts of gliders; verify CPT-like clean annihilation.
*   **Phase 7.4 — Pair Production:** Demonstrate high-energy collisions producing new glider pairs from kinetic bit-energy.

---

### Phase 8: Anchoring to Measurable Physics

**Hypothesis:** Dimensionless physical constants ($G$, $\alpha$, mass ratios) are determined by pure lattice geometry. The model must produce at least one falsifiable, quantitative prediction that distinguishes it from continuum GR/QM.

*   **Phase 8.1 — Dimensionless Constants from Geometry:** Express lattice analogs of $G$, $\alpha$, and mass ratios in closed form using only integers, $\pi$, and lattice-geometric quantities (no free parameters fitted to real data).
*   **Phase 8.2 — Unit Calibration:** Establish a mapping from lattice units to SI units via at most two anchor constants.
*   **Phase 8.3 — Falsifiable Predictions:** Identify a quantitative prediction (discreteness signatures, modified dispersion, extreme curvature deviation, grid anisotropy) that is experimentally testable.
*   **Phase 8.4 — Cross-Check Against Experiment:** Compare predictions against published experimental bounds (cosmic-ray dispersion, atomic clocks, CMB anisotropies).

---

## 5. Savegame — Confirmed Knowledge (As of Iteration 248)

The table below catalogs confirmed facts. Entries marked **(C)** are confirmed empirical discoveries; entries marked **(D)** are definitional or constructional algebraic identities.

| Fact / Finding | Iterations | Type | Status / Notes |
| :--- | :---: | :---: | :--- |
| 33 reversible, bit-preserving 1D rules exist | iter_001 | C | 1D Foundations |
| 22 rules produce $v=c$ gliders; 11 stable fixed points | iter_002 | C | 1D Foundations |
| $v=c/2$ gliders possible via internal oscillation | iter_003–006 | C | Mass Emergence in 1D |
| Stable $v=1c$ 3-bit L-Tromino glider on 2D hex grid (`g10_rule_001`) | iter_179 | C | First evolutionary 2D glider |
| Stable $v=0.469c$ sub-light glider on 2D hex grid | iter_222 | C | `champion_rule_perfect.json` |
| Collision regimes of $v=0.469c$ glider: local, chaotic, annihilation | iter_223 | C | 2D hex scattering |
| 3D FCC CA engine with 12-channel cuboctahedron neighborhood | iter_224 | C | 3D Engine works flawlessly |
| Gravitational time dilation via local coordinate latency field | iter_224 | C | Valid GR mechanism |
| $3\text{D}+1$ D4 spacetime projection; $c=1$ along $[1,\dots,1]$ axis | iter_225-226 | D | Coordinate geometry |
| Lorentz $\gamma$ formula evaluates to $\sim 2\text{e-}16$ along worldlines | iter_225-226 | D | Algebraic identity in float64 |
| Shapiro delay and Fermat lensing under coordinate latency field | iter_227, 229 | C/D | Confirmed qualitative GR analogy |
| Frame-dragging deflection under moving mass source | iter_231 | C/D | Mechanism is by construction |
| Cavendish Unit Test: Bidirectional deflection of $\pm 0.5$ units | iter_232 | C | Deflection confirmed, but of a composite |
| **LUT-08 is a non-interacting composite of 4 independent bits** | iter_248 | C | **Shattered assumption.** Bits travel on parallel paths without sharing cells; binding energy is $0.0$ |
| **All O_h-symmetric, single-cell additive rules are monospecific** | iter_248 | C | **Shattered assumption.** No genuine bound multi-bit gliders exist in this space due to einzell-additivity |
| **Complete fundamental 6-cycle single-bit spectrum** | iter_248 | C | Includes 5 moving velocities and 1 stationary oscillator |

---

## 6. Fitness Function History & Known Exploits

Genetic algorithms are prone to finding exploits rather than physical gliders. The following exploits have been identified and must be actively avoided:

| Exploit | Symptom | Solution |
| :--- | :--- | :--- |
| **Settler** | A stationary rule scores highly because standard deviation of movement is zero. | Enforce a net displacement term in the fitness metric. |
| **Annihilator** | The rule deletes all bits; Center of Mass calculation yields a large false displacement. | Multiply fitness by a `final_bits / initial_bits` preservation term. |
| **Transient Buffer** | A rule exhibits a brief burst of movement before dispersing or freezing. | Measure fitness at a late window or at multiple checkpoints. |
| **Explosive Bloomer** | Bit count explodes exponentially, causing the Center of Mass to drift temporarily. | Apply a heavy penalty for exceeding the initial bit count. |
| **C2 Symmetry Bug** | A C2-symmetric rule paired with a C2-symmetric seed locks Center of Mass to 0. | Use an asymmetric seed (e.g., L-Tromino). |
| **Composite Exploit** | A rule passes checkpoint tests by streaming non-interacting bits in parallel. | Apply the **Three-Test Coherence Protocol** as a secondary filter. |

---

## 7. Success Criteria & Constraints

### General Success Criteria
*   **Verification:** Every milestone must be validated using the three-test coherence protocol (proving binding energy $>0$) and checked against grid-axis anisotropy controls.
*   **Rule Invariants:** Unless explicitly justified in pre-registration, all rules must preserve:
    1.  *Strict Locality:* Operations only access adjacent grid channels.
    2.  *Binary Purity:* Complete integer-based CA logic.
    3.  *Reversibility:* Strict bijective mapping of states.
    4.  *Bit Conservation:* Hamming weight of states is invariant.
    5.  *Hardware Symmetry:* Group invariance under cuboctahedron rotations ($O_h$).

### Technical Constraints
*   **No Floats in Physics:** Floating-point values are strictly banned in the core CA rules (they may be used for auxiliary reporting, coordinate projection, or the external latency field, but must not influence discrete state transitions).
*   **Resource Control:** Every genetic sweep or large-scale collision simulation requires strict pre-registration of parameters to prevent post-hoc tuning.
