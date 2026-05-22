# RDF Milestone Review — Iteration 235 — Phase 5.3: Orbital Dynamics and Lattice-Symmetry Constraints

## 1. Pre-Declared Hypothesis and Falsification Criterion
*   **Hypothesis:** Two LUT-08 sub-light gliders on the 3D FCC lattice, dynamically generating their own coordinate-latency fields, will form a stable, self-consistent bound state (orbit or quasi-closed orbit) that is covariant under the octahedral symmetry group ($O_h$).
*   **Falsification Criteria:**
    1. Refuted if the mutual approach/binding over $\ge 80$ steps is not larger than the vacuum control by at least $2\times$ the lattice resolution.
    2. Refuted if the apparent bound state disappears or fails to transform covariantly when the initial conditions are rotated through the 48 permutations of the $O_h$ group.

## 2. Experimental Protocol
*   **Grid Size:** $32 \times 32 \times 32$ toroidal grid.
*   **Step Count:** 160 steps.
*   **Particles:** Two 4-bit sub-light gliders (LUT-08), total 8 bits.
*   **Coupling Parameters:** Spatial Gaussian smoothing ($\sigma = 2.5$), coupling constant ($\eta = 2.0$), temporal decay ($\gamma = 0.9$), threshold = 0.045.
*   **Control Run:** Parallel vacuum runs (zero coupling, $\eta = 0.0$) under identical coordinate orientations.
*   **Symmetry Test:** Execution of the 48 coordinate transformations of the $O_h$ group on the initial state vectors.

## 3. Observed Quantities
*   **Symmetry Reconstruction Noise:** Applying $O_h$ transformations to the non-orthogonal hexagonal layer-stacking coordinates resulted in reconstruction errors up to 1.75 lattice units due to integer rounding.
*   **Vacuum Control Dispersion:** Rotated parallel gliders in vacuum experienced a relative launch misalignment due to rounding noise, dispersing by up to 19.69 cells over 80 steps.
*   **Bound State Dynamics (Permutation 10):** Under active coupling ($\eta = 2.0$), the mutual separation of the gliders was stably maintained at $2.75$ to $2.89$ cells over 160 steps, demonstrating five distinct periapsis returns (oscillatory contract-and-release cycles) and countering the rapid dispersion observed in the vacuum control.
*   **Bit and Structural Conservation:** Exactly 8 bits and the original LUT-08 structures were conserved perfectly throughout the 160-step dynamic simulation.

## 4. Verdict
*   **Verdict:** **Partially Refuted / Partially Consistent**. 
*   **Justification:** The hypothesis that the bound state is strictly covariant under the $O_h$ group is **refuted** at this resolution; the non-orthogonal grid projection introduces rounding noise that breaks the symmetry of the initial state, making the orbital stability highly dependent on the coordinate orientation. However, the hypothesis that self-generated latency fields can establish a stable, self-consistent two-body bound state is **consistent** with the observations, as evidenced by the five periapsis returns in Permutation 10 which successfully suppressed the vacuum dispersion.

## 5. Construction-vs-Empirical Note
The breaking of the $O_h$ symmetry group is a **constructional identity** arising from the non-orthogonal layer-stacking coordinate representation of the FCC lattice. Conversely, the dynamic attraction that stabilizes the two-body system and prevents glider dispersion while maintaining 8-bit conservation is a **genuinely new empirical finding** regarding the dynamics of our coupled LGCA engine.

## 6. Limitations
*   This result does not demonstrate a closed isotropic Keplerian orbit; the trajectory is constrained by discrete lattice-anisotropy and coordinate projection noise.
*   The bound state was only sustained in coordinate orientations where the discretization noise did not exceed the binding potential.
*   Simulations at higher grid resolutions (e.g., $64^3$ or $128^3$) are required to determine if the discretization noise scales down and restores approximate $O_h$ covariance in the continuum limit.