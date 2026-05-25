# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 7 (Particle Zoo) - Sub-phase 7.3 (Antiparticles & CPT Symmetries)
*   **Active Direction:** Analyzing CPT-like symmetries, specifically characterizing the structural constraints of discrete lattices on collision covariance under O_h rotations.
*   **Trajectory Update (Iteration 246):** Iteration 246 successfully tested the boundary-interference hypothesis by scaling the collision domain to an isolated $64^3$ grid. The results conclusively **refute** the hypothesis that toroidal boundary interference causes the observed O_h non-covariance in collisions. Instead, they **confirm** that the broken covariance is a fundamental coordinate-rounding and sub-lattice phase-shift artifact (definitional alignment mismatch) arising from the discrete lattice representation of non-axis-aligned gliders ($v \approx [0.25, -0.5, 1.0]$).
*   **Confidence Score:** 65% (High confidence in our understanding of the discrete grid constraints; lower confidence in the viability of non-axis-aligned gliders for covariant multi-particle physics).

## 2. Strategic Insights & Lessons Learned
*   **Broken O_h Collision Covariance:** While individual gliders propagate invariantly under O_h rotations (a constructional property of the local rule set), their mutual collision outcomes are highly non-covariant. Out of 24 proper O_h rotations on an isolated $64^3$ grid, 21 result in chaotic scattering, 1 in a partial state, and only 2 in elastic scattering (the identity and a single symmetric equivalent).
*   **The Discretization Rounding Barrier:** Non-axis-aligned gliders like LUT-08 carry fractional coordinates that must be rounded to discrete integers on the layer-stacking grid. When rotated, these rounding operations introduce lateral coordinate shifts of up to 1.0 lattice unit and alter the relative sub-lattice phase alignment of the colliding particles. On a discrete lattice, collision dynamics are extremely sensitive to these sub-pixel phase alignments.
*   **Anisotropy of Multi-Particle State Space:** This finding establishes a key limitation: discrete lattices do not automatically preserve rotational covariance for multi-body interactions unless the constituent particles are aligned with high-symmetry axes of the grid, or the system is evaluated in a limit where the glider's internal scale is much larger than the lattice spacing (coarse-grained limit).

## 3. Loop & Bottleneck Detection
*   **Active Bottleneck:** Representational asymmetry of non-axis-aligned velocities under discrete O_h rotations. Continuing to sweep parameters for LUT-08 collisions under the expectation of covariant scattering is a dead end.
*   **Mitigation Strategy:** Redirect evolutionary and systematic searches to identify stable glider species that propagate strictly along high-symmetry axes of the FCC lattice (e.g., $v \parallel [0, 0, 1]$ or similar). Such species are immune to coordinate-rounding offsets under the corresponding subgroups of O_h, which should restore exact collision covariance.

## 4. Alternate Research Paths
*   **Axis-Aligned Glider Search:** Search for simpler, axis-aligned gliders on the FCC lattice and evaluate their collision mechanics.
*   **Coarse-Grained Trajectory Ensembles:** Shift toward statistical ensembles of gliders (Phase 6.1) where sub-pixel phase mismatches are averaged out over many trials, testing if macroscopic covariance emerges statistically.