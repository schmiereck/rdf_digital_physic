# RDF Scientific Pre-Registration

*   **Iteration:** 242
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
The LUT-08 sub-light glider on the 3D Face-Centered Cubic (FCC) lattice possesses two independent, discrete conserved physical quantities:
1. A chiral charge \(\chi \in \mathbb{R}\), defined by the signed volume of the tetrahedron formed by its 4-bit coordinate vectors relative to its center of mass:
   \(\chi = (\mathbf{r}_2 - \mathbf{r}_1) \cdot [(\mathbf{r}_3 - \mathbf{r}_1) \times (\mathbf{r}_4 - \mathbf{r}_1)]\),
   which is invariant under vacuum propagation (modulo periodic phase translation), swaps sign under spatial reflection, and is conserved in all elastic interactions.
2. A sub-lattice charge vector \(\mathbf{q} = (q_0, q_1, q_2, q_3) \in \mathbb{Z}^4\) representing bit-occupancy on the four independent simple cubic sub-lattices of the FCC grid, which transforms via a fixed permutation matrix \(M\) during each propagation step and is additively conserved under all local collisions.

## 2. Falsification Criterion
The hypothesis will be refuted if any of the following occur:
1. The tetrahedral signed volume \(\chi(t)\) of the LUT-08 glider is identically zero at all steps of its periodic propagation cycle (proving it is achiral).
2. A spatially reflected configuration of the glider (enantiomer) fails to propagate stably under the same rules, or fails to exhibit the exact opposite sign of chirality (\(-\chi\)).
3. The sub-lattice charge vector \(\mathbf{q}(t)\) does not follow a strict cyclic permutation relation \(\mathbf{q}(t+1) = M \mathbf{q}(t)\) in vacuum.
4. In any of 10 independent, distinct elastic collision runs of two gliders, the sum of incoming chiralities or sub-lattice charge vectors does not equal the sum of outgoing chiralities or sub-lattice charge vectors (violating additive conservation).

## 3. Proposed Method
1. Write a pre-registration file `src/pre_registration.md` outlining the mathematical definitions, the 10 planned test collision configurations, and the exact code implementations.
2. Create `src/glider_charge_analysis.py` to load the canonical LUT-08 glider and track its coordinates, center of mass, and sub-lattice occupancy over 100 steps of vacuum propagation.
3. Compute and analyze \(\chi(t)\) and \(\mathbf{q}(t)\) to determine if they satisfy the symmetry and permutation criteria.
4. Apply a spatial reflection transformation to the LUT-08 glider, run it in vacuum, and verify its stability and inverted chiral charge.
5. Setup a collision sweep on the 3D FCC engine to identify at least 10 independent, non-trivial elastic collision events.
6. Compute the incoming and outgoing sum of chiral charges and sub-lattice parities for each collision to verify additive conservation.
7. Compile the results in `RESEARCH-RESULT-242.md` and update `current_state.md`.

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
