# Research Goal: Emergence of Digital Physics (Bit-Grid Universe)

This project explores the reduction of physical laws to fundamental, binary operations within a discrete grid. The objective is to demonstrate that complex phenomena such as mass, gravity, and time dilatation are not mathematical axioms, but rather emerge as emergent effects from a minimal set of local, reversible rules on a highly symmetric grid.

The universe is viewed here as a distributed system in which information is the sole substance. The speed of light is defined by the grid topology (1 link per tick), while gravity is interpreted as local latency (computational load delay).

---

## 1. Strategic Approach: The "Unit-Test" Workflow

The search for the "Theory of Everything" is not conducted by blind guessing in high dimensions, but through hierarchical scaling. Each lower dimension serves as a controlled unit test for the next higher level:

* **Stage 1 (1D):** Search for rules that satisfy fundamental conservation laws (energy/bit sum) and produce stable "solitons" (gliders).
* **Stage 2 (2D Hex):** Extension to hexagonal symmetry to validate angular interactions and scattering processes (elastic collisions).
* **Stage 3 (3D Cuboctahedron):** Transferring the logic to the 12-fold symmetry of the cuboctahedron. The geometry is treated here as a stack of hexagonal planes, ensuring the transferability of the 2D oscillation patterns.

---

## 2. The Experimenter Architecture (Pipeline)

To tame the exponentially exploding rule space, the framework utilizes a three-stage filter architecture:

1.  **Formal Filter (Symbolic Math):**
    * **Bijectivity:** Only permutations of the state space are permitted (guaranteeing reversibility).
    * **Linearity Check:** Exclusion of trivial rules (pure rotation/identity).
    * **Symmetry Compression:** Utilizing the $O_h$ symmetry group of the cuboctahedron to reduce the truth tables.
2.  **AI Predictor (Neural Rule Scoring):**
    * Classification of rule complexity (ice, steam, or life) based on the Lambda parameter and Langton metrics.
    * AI-assisted prediction of the stability of glider patterns.
3.  **Evolutionary Loop (Genetic Algorithm):**
    * Starting with a pool of 1000 validated rules.
    * Crossover and mutation of truth tables based on "fitness" (survival time of complex structures in mini-simulations).

---

## 3. Iterative Master Plan (Roadmap)

The project is divided into four sprints, each ending with a "savegame" of the knowledge state:

### Phase 1: The 1D Symmetry Sifter (Foundations) ✓ COMPLETED
* **Goal:** Identification of all reversible, bit-preserving rules for $n=3$ bits.
* **Milestone:** Catalog of "physical constants" (rule sets) that allow simple propagation.
* **Result (iter_001–002):** 33 non-trivial rules found; 22 of them produce v=c gliders,
  11 stable fixed points. Details: `archive/iter_001/results/valid_rules.json`.

### Phase 2: The "Wiggle" Detector (Internal Oscillation) ✓ COMPLETED
* **Goal:** Extending the bit depth (2-3 bits per cell) to enable internal oscillations.
* **Milestone:** Generation of particles with effective velocities $v < c$ (mass simulation).
* **Result (iter_003–006):** 2-bit/cell system: period-2 oscillator (v=0) and v=c/2 gliders
  (single and composite particles) proven by construction. Collision characterization
  in 1D: 8 elastic, 6 fusion, 8 chaotic (iter_007 / iter_018).

### Phase 3: The 2D Hex Collision (Scattering) ⟳ IN PROGRESS
* **Goal:** Validating interaction logic in elastic collisions within the hexagonal grid.
* **Milestone:** Observation of deterministic angle changes without loss of information.
* **Intermediate Result (iter_179, Milestone `milestone-glider-discovery`):**
  A stable v=1c glider (3-bit L-tromino, rule `g10_rule_001`) was discovered through evolutionary
  search. Perfect bit preservation, 400 cells offset in 400 steps, zero dispersion.
  Animation: `archive/iter_179/results/champion_glider.gif`.
* **Open:** Collision dynamics of two gliders; v<c glider via internal oscillation.

### Phase 4: The Cuboctahedron Universe (3D to 4D)
In this phase, the logic is transferred to the full target geometry. We distinguish between simulation in space and representation as static spacetime geometry.

#### Phase 4.1: 3D Space with Internal Time Step
* **Focus**: Classical 3D simulation where time is defined by the orchestrator's iteration loop.
* **Technique**: Full utilization of the 12 neighbors of the cuboctahedron in 3D space using 0.5-ticking (node-edge exchange).
* **Goal**: Stabilization of 3D gliders and proof of time dilation via local computational load delay (CPU throttling analogy).

#### Phase 4.2: 2D+1 (3D FCC Spacetime)
* **Focus**: Treating the third dimension of the FCC grid as the time axis.
* **Technique**: Definition of "straight" axes (pure flow of time in place) and "tilted" axes (movement through 2D space over time). A time step corresponds to a jump along a grid edge in spacetime.
* **Goal**: Geometric representation of the speed of light as a fixed angle of inclination in the grid. Investigation of how bits "wiggle" along spacetime paths.

#### Phase 4.3: 3D+1 (4D FCC Spacetime)
* **Focus**: Full scaling to a 4-dimensional FCC grid (D4 grid), where time represents the fourth dimension.
* **Technique**: Modeling world lines as paths in the 4D grid. Time steps occur along the 4D vectors to the nearest neighbors (corresponding to the 24 neighbors of the 4D sphere packing).
* **Milestone**: Complete mapping of the Minkowski metric to a discrete bit grid. Proof that time dilation is geometrically represented by the path length in the 4D grid (proper time).
---

## 4. Confirmed Knowledge and Methodological Lessons (As of: iter_179)

This section is the "savegame" of the knowledge gained so far. New agents must read it
before planning experiments in order to avoid already known dead ends.

### 4.1 Confirmed Facts

| Fact | Iterations |
|------|------------|
| 33 reversible, bit-preserving 1D rules exist (3-bit neighborhood) | iter_001 |
| 22 of these produce v=c gliders; 11 stable fixed points | iter_002 |
| 2-bit/cell: v=c/2 gliders possible via internal oscillation (mass emergence) | iter_003–006 |
| Stable v=1c glider evolutionarily developed in 2D hex grid (`g10_rule_001`) | iter_179 |
| Fitness score 56.0 corresponds to a real glider (visually verified, no exploit) | iter_179.4 |
| All "champion" rules from iter_174 and iter_176 are unstable under `CheckpointFitness` (Score 0.0) | iter_179.1 |

### 4.2 Known Exploits of the Fitness Function

Each of these exploits invalidated previous evolutionary runs. They must be explicitly excluded
in new fitness functions:

| Exploit | Symptom | Solution |
|---------|---------|--------|
| **Settler** | Stationary rule scores high because std_dev = 0 | Enforce displacement term |
| **Annihilator** | All bits deleted → CoM movement relatively large | `final_bits / initial_bits` term |
| **Transient Buffer** | High initial movement, then stasis | Late-window or checkpoint measurement |
| **Explosive Bloomer** | Bit count explodes, CoM drifts only briefly | `max_bit_count` penalty |
| **C2 Symmetry Bug** | C2 rule + C2-symmetric seed → CoM invariance (always 0) | Use asymmetric seed (L-tromino) |

### 4.3 Robust Fitness Function: `CheckpointFitness`

The only fitness function so far that rejects all known exploits.
Implementation: `src/run_iter_179_evolution.py` (iter_179).

**Principle:** The particle is measured at multiple points in time (checkpoints).
Fitness = Net displacement × number of checkpoints where the bit count is exactly stable.
A rule that has the wrong bit count at even one checkpoint receives a fitness of 0.

**To be used by default** for all future evolutionary runs, until a better metric is
introduced with explicit justification.

### 4.4 Standard Configuration for Evolutionary Search (2D Hex)

Distilled from iter_170–179; directly transferable to new campaigns in the 2D hex grid:

* **Seed Particle:** 3-bit L-tromino (asymmetric, C2-symmetric seeds are useless)
* **Grid Size:** 128×128 torus
* **Checkpoint Intervals:** 4 uniform points across the simulation horizon
* **Population Size:** 100 rules; elite ratio 10%
* **Expected Behavior:** Phase transition (sudden fitness increase) can occur in Gen 5–10;
  do not abort if early generations stagnate (iter_174: plateau until Gen 6, then jump)

### 4.5 Warning: Trivial 2D Rules

Simple local rules in the 2D hex grid (bit rotation, neighbor swap) are typically
equivalent to a global grid shift and do not produce real local particles
(iter_016–017). Evolutionary search is necessary for non-trivial dynamics.

---

## 6. Success Criteria

* **Deterministic Gliders:** Stable bit patterns that propagate over long distances without decay.
* **Quantized Intermediate Values:** Emergence of continuously acting velocities through statistical directional changes (duty cycles).
* **Physical Equivalence:** Consistent handling of collisions independent of topological distance (Case 1 vs. Case 2 solution via 0.5-ticking).
* **E=mc² Analogy:** Rules where kinetic bit energy can be converted into internal state energy (rest mass).

---

## 7. Technical Constraints

* **Strict Locality:** No access to non-neighboring nodes (Exception: Explicit entanglement pointers to source events).
* **Binary Purity:** No use of float values within the physics engine.
* **Hardware Symmetry:** All rules must be invariant under rotations of the cuboctahedron.
* **Resource Control:** Each iteration requires a manual release [y] after reviewing the strategy report.
