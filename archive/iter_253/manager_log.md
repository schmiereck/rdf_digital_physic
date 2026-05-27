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

## Iteration 253 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
A totalistic synchronous CA on the 3D FCC lattice (13-neighbor input → 1-bit center
output, NO bit conservation constraint) can produce at least one genuine multi-bit
bound glider with binding energy > 0. Specifically: there exists a totalistic rule
R: {0,...,13} → {0,1} such that a small multi-bit seed (3–6 bits) on the FCC grid
evolves into a stable, propagating structure where (a) the structure survives ≥200
steps, (b) no individual constituent bit survives alone (Single-Bit Decomposition
Test fails for each bit, proving cooperative survival / binding energy > 0), and
(c) the structure propagates with a well-defined sub-light velocity (net displacement
> 0 per period). This is motivated by the 2D hex precedent where cooperative survival
via weight-1→0 transitions is the proven binding mechanism, and the 13-neighbor FCC
totalistic CA directly generalizes this architecture to 3D.

**Proposed Falsification Criterion:**
The hypothesis is REFUTED if any one of the following holds:
F1: No totalistic rule in the GA search produces a propagating structure surviving
    ≥200 steps from any seed of size 3–6 bits. (If all rules produce only static
    oscillators, chaotic explosions, or rapidly dispersing patterns.)
F2: The best surviving structure passes the Single-Bit Decomposition Test — i.e.,
    at least one constituent bit of the seed survives and propagates independently
    when run in isolation — proving it is a non-interacting composite with binding
    energy = 0.
F3: The totalistic rule space is shown to be too coarse (only 2^14 = 16,384 rules)
    to encode the anisotropic propagation directions needed for directed glider
    motion on the FCC lattice, making any surviving structure necessarily isotropic
    (expanding blob) or stationary (oscillator).

**Proposed Method:**
RE-RUN of iteration 253 with optimized totalistic_ga.py code.

Step 1: Verify and re-run the existing totalistic_ga.py infrastructure.
  - Confirm the totalistic CA engine on 3D FCC lattice is functional:
    13 neighbors per cell, totalistic rule R: {0,...,13} → {0,1}.
  - Confirm O_h symmetry enforcement: totalistic rules are automatically O_h-symmetric
    by construction (depend only on Hamming weight, not neighbor identity).
  - Confirm bit conservation is NOT enforced (matching 2D hex precedent).
  - File: src/totalistic_ga.py (already exists and optimized)

Step 2: Execute the GA search (sub-task 253.2.3 re-run).
  - Search space: 2^14 = 16,384 totalistic rules (compact enough for exhaustive
    evaluation if needed, but GA preferred for fitness-guided exploration).
  - Seed library: small multi-bit seeds (3–6 bit L-tromino-like patterns on FCC
    [111] plane and other high-symmetry planes).
  - Fitness function: checkpoint-based, combining:
    (a) Late-window net displacement (steps 150–200) > 0
    (b) Bit count bounded (penalize explosions: max_bit_count / initial_bit_count < 3.0)
    (c) Velocity stability (low std dev of displacement across windows)
    (d) Anti-settler: must have net displacement > 0
  - GA parameters: population=100, generations=20, tournament selection, point
    mutation on rule bits, crossover.
  - Timeout safeguards: per-rule simulation capped at 200 steps; per-generation
    evaluation capped with early termination for chaotic rules (bit count > 3× initial).

Step 3: Post-filter champion rules with Three-Test Coherence Protocol.
  - Single-Bit Decomposition Test: remove each constituent bit of the seed and
    re-run. ALL bits must fail to survive alone for the glider to be genuine.
  - Collision Coherence Test: check if glider maintains structure under small
    perturbations (1-bit latency field).
  - O_h Covariance Test: rotate the glider seed by all 48 O_h elements and verify
    survival (automatic for totalistic rules — only seed geometry matters).

Step 4: Positive control — verify the 2D hex glider rule maps correctly into the
  totalistic framework on a 2D hex lattice slice, confirming the GA can in principle
  discover cooperative survival binding.

Step 5: If F2 is triggered (composite), analyze whether the totalistic constraint
  (ignoring neighbor identity) is the root cause by testing semi-totalistic rules
  that distinguish center-bit state.

Files to create/modify:
  - src/totalistic_ga.py (already exists, optimized — verify and execute)
  - src/totalistic_fcc_engine.py (may already exist as part of totalistic_ga.py)
  - src/pre_registration.md (auto-generated from this plan)

---

## Iteration 253 -> Planner [Strategic Guidance]

### Strategic Guidance Note: Re-evaluating 3D Cooperative Survival via Totalistic CA (Iter 253 Re-run)

While the previous iteration suffered an abrupt termination due to a runtime timeout, the pivot to a **totalistic synchronous CA** (non-LGCA, relaxing local bit conservation) is a logically sound step to resolve the single-cell LGCA impossibility proof established in Iteration 252. However, relaxing core physical invariants (reversibility, bit conservation) requires rigorous methodological guardrails to ensure we do not drift into trivial cellular automata toy models.

---

### 1. Pre-Registration Mandate & Physical Relevance Disclaimer
Since this iteration relaxes both **reversibility** and **local/global bit conservation**, the Planner must explicitly state in `src/pre_registration.md` that this search is a **topological proof-of-concept unit test**. 
* **The Constraint:** We are searching for the *minimal neighborhood logic* required to support 3D cooperative survival. 
* **The Transition Path:** The pre-registration must explicitly note that any discovered totalistic glider is a "proto-particle" and is *not* a final physical solution. To satisfy the Master Goal, any successful rule from this phase must eventually be mapped back onto a reversible, bit-conserving framework (such as a multi-site block/partitioning CA).

---

### 2. Hardening Falsification Criteria: The "Bloomer" and "Melter" Boundaries
The current proposed falsification criteria must be made quantitatively tighter to prevent the genetic algorithm from reporting trivial or chaotic wave fronts as "discoveries."
* **Strict Boundedness (No Bloomer Exploit):** A propagating glider must have a localized envelope. If a rule produces an expanding, chaotic, or solid growing sphere where the bit count grows without bound, it is **refuted**. Specify a strict upper bound: the total active bit count at $t=200$ must not exceed a small multiple of the seed (e.g., $N(200) \le 4 \times N(0)$), and the spatial envelope must remain localized.
* **Strict Directed Propagation (No Settlers):** The center of mass of the active configuration must translate along a stable directional vector with a net displacement $\ge 10$ lattice units over 200 steps, without the structure melting into independent dispersing single bits (which would trigger the Single-Bit Decomposition Test anyway).

Ensure your `src/pre_registration.md` explicitly lists these quantitative boundaries as part of $F_1$, $F_2$, and $F_3$.

---

### 3. Resource & Timeout Hygiene (Addressing the Crash)
The crash in the previous run of `totalistic_ga.py` points to a lack of aggressive early-stopping conditions.
* **Early Death/Explosion Capping:** If a rule's bit count drops to 0 (annihilation) or exceeds $4 \times$ the seed size (explosion) at step $t$, the simulation for that rule must terminate *immediately* at step $t$, returning a minimum fitness score. Do not waste CPU cycles running exploded or dead states up to 200 steps.
* **Generation Scaling:** Keep the population size ($N=100$) and generations ($G=20$) but enforce strict evaluation timeouts per generation to guarantee the script finishes well within the environment limits.

### 4. Language Discipline
In all generated documentation and analysis, maintain a highly objective, skeptical tone:
* Use: *"is consistent with 3D propagation," "provides evidence of localized cooperative survival," "does not refute the existence of totalistic gliders."*
* Avoid: *"organically emerges," "revolutionary," "perfectly resolves," "proves 3D physics."*

---

