# RDF Scientific Pre-Registration

*   **Iteration:** 244
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
Under the O_h-symmetric, reversible, bit-conserving LUT-08 CA rule on the 3D FCC grid, a CPT-conjugate state of the LUT-08 glider (obtained by time-reversal and spatial reflection) acts as a stable physical antiparticle that propagates in the opposite direction (-v). In a head-on collision with the original glider, they undergo clean mutual annihilation where 100% of the combined 8 bits scatter into independent, non-interacting single-bit states propagating at the vacuum speed of light (v=1c), leaving exactly zero bound states or stationary debris.

## 2. Falsification Criterion
The hypothesis will be refuted if:
1. The constructed antiparticle state is unstable in vacuum (i.e. disperses, alters its bit count, or deviates from constant velocity -v over 100 steps).
2. The chirality and sub-lattice parities of the antiparticle do not satisfy the CPT transformation laws (i.e. the chirality sequence is not the negated and time-reversed sequence of the original glider).
3. The head-on collision leaves any stationary bits (v=0), any bound states of size >= 2 bits, or any particles traveling at sub-light speed (v < 1c) after the interaction region has cleared (t = 80 steps).

## 3. Proposed Method
1. Implement a Python script `src/fcc_antiparticle_annihilation.py` to construct the CPT-conjugate (antiparticle) of the LUT-08 glider.
2. Simulate the antiparticle in vacuum for 100 steps on a 64^3 FCC grid to confirm stability, constant velocity, and bit conservation.
3. Compute and track the chirality and sub-lattice parities of the antiparticle to verify CPT symmetry.
4. Set up a head-on collision between the LUT-08 glider and its antiparticle, simulating for 100 steps.
5. Analyze the asymptotic state (t = 80 to 100) to verify that all 8 bits are in independent, non-interacting single-bit channels propagating at v=1c, and that zero stationary or bound-state remnants remain.

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
