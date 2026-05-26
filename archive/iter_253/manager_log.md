# Research Manager Log - Iteration 253

## Iteration 253 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
A 3D synchronous cellular automaton on the Face-Centered Cubic (FCC) lattice
with O_h-symmetric totalistic (Life-like B/S) rules and cooperative survival
(S does not contain 0 — bits with zero neighbors die) can produce genuine
multi-bit bound gliders with positive binding energy. Specifically: (a) at least
one such rule, when initialized with a multi-bit seed of ≤6 bits, produces a
propagating pattern that survives ≥300 CA steps with net displacement ≥5 FCC
lattice units; and (b) each constituent single-bit seed of the same rule, placed
in isolation, dies within ≤50 steps — proving binding energy > 0 via the
cooperative survival mechanism (the only mechanism proven to produce genuine
multi-bit binding in any dimension, per iter_250-252).

**Proposed Falsification Criterion:**
The hypothesis is refuted if ALL of the following hold after testing ≥10,000
totalistic B/S rules (via designed sweep + evolutionary search):
- F1: No rule produces any propagating pattern surviving ≥300 steps from any
  small (≤6 bit) seed.
- F2: Any candidate surviving ≥300 steps has at least one constituent single-bit
  seed that survives ≥100 steps alone (binding energy = 0, non-interacting
  composite).
- F3: Any candidate surviving ≥300 steps fails O_h covariance (dies under ≥1
  of 48 O_h rotations of the initial seed).
- F4: All candidates surviving ≥300 steps are stationary (net displacement < 2
  cells) or explosive (bit count > 10× initial).
A single genuine bound glider passing F1-F4 refutes the null and supports the
hypothesis.

**Proposed Method:**
Step 1 — Build 3D Synchronous CA Engine (src/synchronous_ca_fcc.py):
  - FCC lattice with toroidal boundaries, 13-bit neighborhood (center + 12
    cuboctahedron neighbors at offsets (±1,±1,0), (±1,0,±1), (0,±1,±1))
  - Totalistic B/S update rule: new_center = f(center_bit, neighbor_count)
  - Diagnostics: center-of-mass, bit count, net displacement, survival time
  - Validate with trivial rules (all-die, all-live, known 2D hex analog on [111])

Step 2 — Designed Rule Sweep (src/totalistic_rule_search.py):
  - Generate ~200 B/S rules: S ⊆ {1,...,12}, B ⊆ {1,...,11}, λ ∈ [0.20, 0.50]
  - Standard seeds: single bits (6), bit pairs (12), L-tromino analogs (8),
    small random clusters (20)
  - Run 500 steps per rule×seed; filter for survival ≥ 300, displacement ≥ 5,
    bit count ≤ 10× initial

Step 3 — Evolutionary GA (if Step 2 yields no candidates):
  - 26-bit genome (B+S sets), population 500, 20 generations
  - Fitness: survival × displacement / (1 + |bit_ratio - 1|)
  - Tournament selection, uniform crossover, bit-flip mutation
  - Multi-seed evaluation (5 seeds per rule)

Step 4 — Coherence Testing (src/glider_coherence_test.py):
  - Single-Bit Decomposition Test: each constituent bit dies in ≤50 steps alone
  - O_h Covariance Test: all 48 rotations of seed produce same survival outcome
  - Bit Count Stability: no explosion (>10× initial) or annihilation

Step 5 — Documentation: positive result (genuine glider) or first-class null
  result with totalistic phase diagram characterization on FCC lattice.

Justification for relaxing bit conservation: The 2D hex system (the ONLY
confirmed system with genuine binding) is a synchronous CA that violates bit
conservation. LGCA bit conservation is PROVEN incompatible with cooperative
survival (F3, iter_252). This is the minimal architectural change needed.

---

## Iteration 253 -> Planner [Strategic Guidance]

# Manager's Note: Strategic Guidance

## 1. The Conservation & Reversibility Ultimatum (Scientific Discipline)
The proposal to transition to a synchronous, totalistic (Life-like) CA on the FCC lattice represents a significant departure from our core Master Goal constraints: **reversibility** and **bit conservation**. 

While your mathematical proof in Iteration 252 demonstrated that a single-cell LGCA collision operator is fundamentally incompatible with cooperative survival, abandoning conservation laws entirely cannot be our end-state. 

Therefore, you are authorized to proceed with this 3D synchronous totalistic CA search **strictly as a Feasibility Benchmark**. The strategic value of this iteration is to establish whether the 3D FCC lattice geometry can support cooperative-survival gliders *at all* when conservation is relaxed. If successful, any discovered glider will serve as a kinematic template. The ultimate goal must remain compiling these behaviors back into a reversible, bit-conserving framework (such as a multi-site block-partition CA). 

**Your pre-registration and final report must explicitly frame this run as a non-physical topological feasibility study, not a physical model.**

## 2. Pre-Registration Mandate & Rigorous Falsification
The Orchestrator will automatically write and commit your hypothesis and falsification criteria to `src/pre_registration.md` before execution. Your sub-agents must read and strictly adhere to this file. 

To ensure the utmost rigor, your falsification criteria must address the following totalistic CA exploits:
*   **The Bloomer Exploit:** Totalistic rules frequently exhibit explosive, infinite growth (e.g., "Seeds"-like rules). A candidate is refuted if its bit-count increases monotonically or exceeds $4\times$ the initial seed weight after step 100.
*   **The Debris Cloud:** Patterns that shed static or chaotic pixels indefinitely while a small core moves are not clean gliders. The moving pattern must remain localized within a bounding box of at most $10\times10\times10$ cells.
*   **Single-Bit Isolation:** The single-bit decomposition test must be absolute. If *any* single-bit constituent of the seed survives past 50 steps, the candidate is a non-interacting composite, triggering immediate falsification.

## 3. Exploit-Resistant Search Strategy
Since the totalistic B/S rule space on a 13-bit neighborhood contains $2^{26}$ ($\approx 6.7 \times 10^7$) rules, a blind evolutionary search can easily get trapped in "blooming" or "freezing" local maxima. 
*   **Symmetry Advantage:** Because the rule is totalistic, it depends only on the neighbor count, meaning the rule itself is $O_h$-equivariant by construction. This is a massive mathematical advantage!
*   **Phase Boundary targeting:** Initialize your sweeps targeting the chaotic/complex phase boundary (estimating $\lambda$ parameter or utilizing sparse B/S sets where $S$ does not contain 0, and $B$ is highly constrained). Do not waste compute on rules where $0 \in B$ (which causes vacuum fluctuations) or $0 \in S$ (which prevents isolated bit decay).

---

