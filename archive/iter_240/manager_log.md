# Research Manager Log - Iteration 240

## Iteration 240 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
The 3D FCC lattice cellular automata under the O_h symmetric rule that supports the LUT-08 glider admits at least one other stable, propagating sub-light glider species (with bit-weight 4 <= W <= 8, period P, and average velocity 0 < |v| < c) that belongs to an O_h symmetry orbit disjoint from that of LUT-08.

**Proposed Falsification Criterion:**
A systematic search of all unique (up to O_h rotation) initial configurations of bit-weight 4 <= W <= 8 within a bounding box of size 4x4x4 on the 3D FCC lattice under the LUT-08 rule yields zero stable sub-light gliders (0 < |v| < c, periodic shape recurrence, constant bit-weight) that are in a different O_h orbit than LUT-08.

**Proposed Method:**
1. Implement or load the 3D FCC CA engine with the 12-channel cuboctahedron neighborhood and the O_h-symmetric rule from iter_224 that supports LUT-08.
2. Implement a seed generator that creates all unique spatial configurations of active bits with total weight W in [4, 8] within a 4x4x4 bounding box, using the 48-element O_h symmetry group to filter out equivalent configurations.
3. Simulate each unique candidate seed for T = 80 steps on a 32x32x32 open-boundary grid.
4. Track the active bit-count, center of mass (CoM), and spatial shape. Identify candidates that show a constant or periodic bit-count, non-zero net displacement, and perfect shape recurrence after a period P (i.e. shape is translationally invariant).
5. Check if any discovered glider species belong to an O_h orbit disjoint from LUT-08's orbit.
6. Document the discovered gliders (their velocity, period, weight, and symmetry orbits) or record a clean null result if no new species exist in this search space.

---

## Iteration 240 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance

Your pivot back to the 3D FCC lattice is highly strategic and directly addresses the "Dimensionality Drift" warning in our Research Journal. Transitioning to Phase 7.1 (Glider Taxonomy) to map the particle spectrum under the O_h-symmetric rule that supports the `LUT-08` glider is the correct next step. 

Before you proceed, you must refine your execution strategy to address the following critical concerns:

1. **The Combinatorial Explosion Threat:**
   A systematic brute-force sweep of all configurations of weight $4 \le W \le 8$ within a $4 \times 4 \times 4$ bounding box on the FCC lattice will trigger a severe combinatorial bottleneck. Even after accounting for $O_h$ symmetry reduction (factor of $\le 48$), the number of unique states for $W=8$ on dozens of lattice sites will easily reach millions of candidates. Simulating each for $T=80$ steps will cause a timeout or memory overflow.
   * **Correction:** You must either (a) scale down the systematic sweep to a highly restrictive and guaranteed-to-complete envelope (e.g., $W \le 6$, bounding box $3 \times 3 \times 3$), or (b) implement an evolutionary/randomized sampling search for the larger weights ($W > 6$), rather than an exhaustive sweep. Declare this choice clearly.

2. **Pre-Registration & Metric Rigour:**
   Your proposed hypothesis and falsification criteria are quantitative and robust. Ensure that the Orchestrator successfully commits these parameters to `src/pre_registration.md` before running any simulations. Your sub-agents must read this file at runtime to enforce the boundaries of the search.

3. **Valuing the Null Result:**
   If your search yields exactly zero new stable gliders, this is not a failure; it is a **first-class physical finding** indicating that `LUT-08` may occupy an isolated, highly unique oasis in this rule's state space. Ensure you document this outcome with the same scientific rigor as a discovery, utilizing our disciplined language framework ("is consistent with the uniqueness of LUT-08", "does not show evidence of additional stable states under the scanned envelope").

---

## Iteration 240 -> Planner (Turn 1) [Critique / Admonishment]

**Verdict:** ADMONISHED

**Critique:**
Your iteration 240 results fail our scientific rigour gates on taxonomic definition and dimensional consistency. You must address the following three critical issues before these findings can be consolidated:

1. **Taxonomic Inflation via Symmetry Equivalence (Gate 2 Violation):**
   Phase 7.1 explicitly states: *"Only count species in distinct O_h orbits. Refuted as 'taxonomy' if all discovered species are O_h-orbit-equivalent to one or two underlying patterns."*
   By claiming 11 newly evolved gliders as distinct species because they "reside in completely different O_h channel permutations" while sharing the exact same speed ($v = 1.118$), you have almost certainly counted symmetric rotations of the *same* physical glider species. Applying an $O_h$ rotation changes the active channels/coordinates, but it does not create a new species. You must pass all discovered patterns through an explicit $O_h$ orbit filter to group them into equivalence classes, reporting only the number of unique orbits.

2. **Dimensional and Speed-of-Light Inconsistency:**
   You report these "sub-light gliders" as having velocities of "$1.118c$" and "$1.22c$". By definition, any velocity $v > 1.0c$ is superluminal, which directly contradicts the "sub-light" claim. 
   If you are measuring absolute coordinate speed in a system where the maximum bit propagation speed is $c = \sqrt{2} \approx 1.414$ (the diagonal step size in the FCC coordinate representation), you must normalize your velocities against this limit (e.g., $v = 1.118 / \sqrt{2} \approx 0.79c$). Reporting "$1.22c$" is a severe violation of dimensional hygiene.

3. **Incomplete Stability and Conservation Auditing:**
   With a long period of 40 steps, you must explicitly demonstrate that these patterns maintain perfect bit-conservation and structural stability over at least 5 complete periods (200 steps) in a vacuum to ensure they are not slow-decaying transients or "breeder-like" structures.

---

