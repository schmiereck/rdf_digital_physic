# RDF Scientific Pre-Registration

*   **Iteration:** 253
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
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

## 2. Falsification Criterion
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

## 3. Proposed Method
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
*Created automatically by the RDF Orchestrator prior to iteration execution.*
