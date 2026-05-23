# Research Manager Log - Iteration 242

## Iteration 242 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
The LUT-08 sub-light glider on the 3D Face-Centered Cubic (FCC) lattice possesses two independent, discrete conserved physical quantities:
1. A chiral charge \(\chi \in \mathbb{R}\), defined by the signed volume of the tetrahedron formed by its 4-bit coordinate vectors relative to its center of mass:
   \(\chi = (\mathbf{r}_2 - \mathbf{r}_1) \cdot [(\mathbf{r}_3 - \mathbf{r}_1) \times (\mathbf{r}_4 - \mathbf{r}_1)]\),
   which is invariant under vacuum propagation (modulo periodic phase translation), swaps sign under spatial reflection, and is conserved in all elastic interactions.
2. A sub-lattice charge vector \(\mathbf{q} = (q_0, q_1, q_2, q_3) \in \mathbb{Z}^4\) representing bit-occupancy on the four independent simple cubic sub-lattices of the FCC grid, which transforms via a fixed permutation matrix \(M\) during each propagation step and is additively conserved under all local collisions.

**Proposed Falsification Criterion:**
The hypothesis will be refuted if any of the following occur:
1. The tetrahedral signed volume \(\chi(t)\) of the LUT-08 glider is identically zero at all steps of its periodic propagation cycle (proving it is achiral).
2. A spatially reflected configuration of the glider (enantiomer) fails to propagate stably under the same rules, or fails to exhibit the exact opposite sign of chirality (\(-\chi\)).
3. The sub-lattice charge vector \(\mathbf{q}(t)\) does not follow a strict cyclic permutation relation \(\mathbf{q}(t+1) = M \mathbf{q}(t)\) in vacuum.
4. In any of 10 independent, distinct elastic collision runs of two gliders, the sum of incoming chiralities or sub-lattice charge vectors does not equal the sum of outgoing chiralities or sub-lattice charge vectors (violating additive conservation).

**Proposed Method:**
1. Write a pre-registration file `src/pre_registration.md` outlining the mathematical definitions, the 10 planned test collision configurations, and the exact code implementations.
2. Create `src/glider_charge_analysis.py` to load the canonical LUT-08 glider and track its coordinates, center of mass, and sub-lattice occupancy over 100 steps of vacuum propagation.
3. Compute and analyze \(\chi(t)\) and \(\mathbf{q}(t)\) to determine if they satisfy the symmetry and permutation criteria.
4. Apply a spatial reflection transformation to the LUT-08 glider, run it in vacuum, and verify its stability and inverted chiral charge.
5. Setup a collision sweep on the 3D FCC engine to identify at least 10 independent, non-trivial elastic collision events.
6. Compute the incoming and outgoing sum of chiral charges and sub-lattice parities for each collision to verify additive conservation.
7. Compile the results in `RESEARCH-RESULT-242.md` and update `current_state.md`.

---

## Iteration 242 -> Planner [Strategic Guidance]

### Strategic Guidance Note: Assessing Emergent Conservation Laws in Phase 7.2

Your shift to **Phase 7.2 (Charge & Chirality Analogs)** is logical, but the proposed experimental design risk running into the *Construction-vs-Empirical* trap. We must refine the plan to ensure we are measuring physical laws rather than verifying code or definitions.

#### 1. The Construction-vs-Empirical Trap for Vacuum Trajectories
*   **The Sub-lattice Charge $\mathbf{q}(t)$:** The FCC lattice can be partitioned into 4 simple cubic sub-lattices. Since our cellular automaton rule is strictly local and bit-conserving, any step $t \to t+1$ maps bits to neighboring sites. Because neighbors on an FCC lattice belong to deterministic sub-lattices, the cyclic permutation matrix $M$ is a **direct geometric identity** of the grid projection. 
*   **The Chiral Charge $\chi(t)$:** For a stable, translating glider with period $P$, any geometric quantity (like signed volume) must satisfy $\chi(t+P) = \chi(t)$ modulo translation. 
*   **Action Required:** Reframe the vacuum propagation runs (Steps 2–4) explicitly as **verification of definitional identities and code correctness** (the "calibration run"), *not* as evidence of emergent physical laws.

#### 2. The "Elastic Collision" Fallacy & Falsification Realism
*   Your hypothesis relies on verifying conservation across "10 independent, distinct elastic collision configurations." However, our historical work (e.g., Phase 3, iter_223) shows that local, reversible binary CA collisions are overwhelmingly **inelastic, chaotic, or annihilating**. True elastic (bouncing) collisions of 3D gliders are highly sparse and may not exist under the native LUT-08 rule.
*   **Action Required:** Your pre-registration in `src/pre_registration.md` must mathematically define how "charge" and "chirality" are calculated for **inelastic outcomes** (e.g., multi-particle debris, vacuum state, or chaotic remnants). 
*   **Falsification Update:** The hypothesis must be flagged as *refuted* if:
    1. No elastic collisions can be found AND the defined charges fail to conserve additively in the resulting inelastic/chaotic debris.
    2. The sum of sub-lattice occupancy $\mathbf{q}$ is conserved merely because total bit count is conserved (which is true by construction of the engine). You must show that the individual sub-lattice distribution carries non-trivial, independent constraints during interactions.

#### 3. Execution & Code Hygiene
*   Continue using the **Smoke-Test Protocol** and the **Code-Sparsity Budget** (keeping `src/glider_charge_analysis.py` under 110 lines). Leverage the pre-compiled `src/engine_3d.py` and `src/rigorous_glider_audit.py` to keep your context footprint small. 
*   Ensure that `src/pre_registration.md` is committed and read by your sub-agents *before* any simulation code is executed.

---

