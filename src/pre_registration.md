# RDF Scientific Pre-Registration

**FEASIBILITY BENCHMARK CLASSIFICATION:** This experiment is a non-physical topological feasibility study. It relaxes bit conservation (a core axiom of the LGCA framework) to test whether the 3D FCC lattice geometry can support cooperative-survival gliders AT ALL when conservation is relaxed. Any discovered glider will serve as a kinematic template only; the ultimate goal remains compiling these behaviors back into a reversible, bit-conserving framework (such as a multi-site block-partition CA). This is NOT a physical model.

*   **Iteration:** 253
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
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

## 2. Falsification Criterion
The hypothesis is refuted if ALL of the following hold after testing ≥10,000
totalistic B/S rules (via designed sweep + evolutionary search):
- F1: No rule produces any propagating pattern surviving ≥300 steps from any
  small (≤6 bit) seed.
- F2: Any candidate surviving ≥300 steps has at least one constituent single-bit
  seed that survives ≥50 steps alone (binding energy = 0, non-interacting
  composite).
- F3: Any candidate surviving ≥300 steps fails O_h covariance (dies under ≥1
  of 48 O_h rotations of the initial seed).
- F4: All candidates surviving ≥300 steps are stationary (net displacement < 2
  cells) or explosive (bit count > 10× initial).
- F5: Bloomer Exploit — A candidate is refuted if its bit-count increases
  monotonically or exceeds 4× the initial seed weight after step 100.
- F6: Debris Cloud — The moving pattern must remain localized within a bounding
  box of at most 10×10×10 cells after step 100. Patterns shedding static/chaotic
  debris indefinitely are not clean gliders.
A single genuine bound glider passing F1-F6 refutes the null and supports the
hypothesis.

## 3. Proposed Method
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
*Created automatically by the RDF Orchestrator prior to iteration execution.*
