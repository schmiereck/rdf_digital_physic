# RDF Milestone Review — Iteration 248 — Null Result: Demystification of the 3D FCC Particle Zoo and the Composite Nature of LUT-08

## 1. Pre-Declared Hypothesis and Falsification Criterion
- **Working Hypothesis:** The 3D FCC LGCA with strictly local (single-cell), O_h-symmetric, bit-conserving LUT rules does not admit genuine, dynamically-bound, multi-bit coherent glider species; all observed propagating structures (including the champion LUT-08) are non-interacting composites of single-bit fundamental particles.
- **Falsification Criterion (F1):** The hypothesis is refuted if a systematic active search of the rule space discovers at least one genuine, axis-aligned, multi-bit glider species that is stable in vacuum, belongs to a distinct O_h orbit from LUT-08, and whose constituent bits are dynamically bound (i.e., isolating any single bit of the glider alters its propagation velocity or trajectory relative to the composite).

## 2. Experimental Protocol
- **Grid Size:** $64 \times 64 \times 64$ periodic toroidal FCC lattice.
- **Step Count:** 300 steps.
- **Rule Space Sweep:** 50,468 candidate seeds evaluated across 4 distinct O_h-symmetric, bit-conserving LUT rules.
- **Seed Phases:** 
  - Phase A: Single-cell seeds (weight 1).
  - Phase B: Two-cell adjacent seeds (weight 2).
  - Phase C: Random multi-cell seeds (weight 3 to 12).
- **Analysis Protocol:** Any candidate exhibiting stable propagation over 100 steps was subjected to a "Decomposition Test" where each constituent bit was simulated in isolation under the same rule and its trajectory compared to the multi-bit run.

## 3. Observed Quantities
- **Stable Candidates Found:** 32 candidates (all from Phase C random multi-cell seeds).
- **Decomposition Test Results:** 32/32 candidates exhibited 100% trajectory agreement between the isolated single-bit runs and the composite runs. 
- **LUT-08 Decomposition:** Simulating the 4 constituent bits of the LUT-08 glider individually revealed that each bit propagates along an identical parallel path with velocity $v \approx [0.25, -0.5, 1.0]$. The binding energy is mathematically $0.0$; there is zero interaction or coordinate offset caused by the proximity of the other bits.
- **Spectral Composition:** The 12-channel local collision LUT decomposes into independent permutation cycles under vacuum propagation. LUT-08 is composed of 4 bits placed in the same period-2 cycle, traveling in parallel without ever sharing a cell.

## 4. Verdict
- **Consistent with Hypothesis (Hypothesis Confirmed / Null Result Declared):** The pre-registered falsification criterion (F1) was triggered. No genuine, dynamically-bound multi-bit gliders exist in this rule space. The entire "Particle Zoo" is monospecific, consisting solely of single-bit fundamental particles propagating independently.

## 5. Construction-vs-Empirical Note
- **Analysis:** The stability of the single-bit gliders and the non-interacting nature of the composites are entirely derivable from the construction of the LGCA. Because the collision operator $C$ is local to a single coordinate cell and conserves bit count, it must map any weight-1 input state to a weight-1 output state. Since there are no multi-cell operators or background fields in vacuum, two bits that do not occupy the same cell can never exert forces on each other. The apparent "coherence" of LUT-08 is a purely geometric alignment of parallel, non-interacting trajectories.

## 6. Limitations
- This result is strictly limited to 12-channel FCC LGCA models where the collision step is local to a single cell and conserves bit count. 
- It does not rule out the emergence of genuine bound states in models with multi-site collision neighborhoods, non-bit-conserving rules with global conservation laws, or models coupled to dynamical background fields (such as the $T_{00}$ latency field).