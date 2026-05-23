# RDF Scientific Pre-Registration

*   **Iteration:** 243
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
Under the reversible, bit-conserving LUT-08 rule on the 3D FCC grid, there exists a unique time-reversed, parity-symmetric counterpart of the LUT-08 sub-light glider (the antiparticle). When this antiparticle and the original particle collide head-on with perfectly matched spatial alignment and opposite phase-periodic chiralities, they undergo clean annihilation. In this annihilation process, 100% of their localized rest-mass (sub-light gliders) is converted into massless radiation (comprising 8 individual 1-bit gliders propagating outward at the speed of light v = 1c), leaving the collision center completely empty of any stationary remnants, sub-light gliders, or bound states after 80 steps, while perfectly conserving total bit count (exactly 8 bits), total momentum (0), and global sub-lattice parities.

## 2. Falsification Criterion
The hypothesis will be refuted if any of the following occur:
1. The constructed antiparticle state is unstable in vacuum, failing to propagate with a constant velocity -v and period 2.
2. The head-on collision of the matched particle-antiparticle pair does not result in clean annihilation, leaving any localized bit remnants (non-zero bit count) within a 10^3 bounding box centered at the collision point after 80 steps.
3. The outgoing particles do not all propagate at the speed of light (v = 1c), or the total bit count deviates from exactly 8 at any step of the simulation.
4. The CPT-symmetry is violated, meaning that reversing the velocities of the outgoing radiation states and running the simulation forward fails to reconstruct the initial head-on gliders to bit-level precision.

## 3. Proposed Method
1. Construct the antiparticle state of the LUT-08 sub-light glider on the 3D FCC grid by applying spatial reflection (Parity P, x -> -x) and velocity reversal (Time reversal T, reversing channel directions) to the standard 4-bit glider state.
2. Verify the stability of the antiparticle in vacuum by simulating it for 100 steps on a 64^3 grid and confirming it moves with velocity -v and period 2.
3. Set up a phase-swept, head-on collision experiment between the particle and its antiparticle on a 64^3 grid. Sweep the relative phase difference Delta phi in {0, 1} and impact offsets to find the precise alignment for clean annihilation.
4. Analyze the collision products after 80 steps. Quantify the remaining local bits at the collision center and the velocity of all outgoing bits.
5. Perform a CPT-reversibility test: reverse the velocity channels of the final outgoing state at step 80 and run the simulation forward for 80 steps to verify that the initial state is perfectly reconstructed.
6. Create `src/glider_annihilation_analysis.py` to execute this protocol and generate `src/pre_registration.md` to document the pre-registered experiment.

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
