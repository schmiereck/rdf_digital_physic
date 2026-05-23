# Research Manager Log - Iteration 243

## Iteration 243 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
Under the reversible, bit-conserving LUT-08 rule on the 3D FCC grid, there exists a unique time-reversed, parity-symmetric counterpart of the LUT-08 sub-light glider (the antiparticle). When this antiparticle and the original particle collide head-on with perfectly matched spatial alignment and opposite phase-periodic chiralities, they undergo clean annihilation. In this annihilation process, 100% of their localized rest-mass (sub-light gliders) is converted into massless radiation (comprising 8 individual 1-bit gliders propagating outward at the speed of light v = 1c), leaving the collision center completely empty of any stationary remnants, sub-light gliders, or bound states after 80 steps, while perfectly conserving total bit count (exactly 8 bits), total momentum (0), and global sub-lattice parities.

**Proposed Falsification Criterion:**
The hypothesis will be refuted if any of the following occur:
1. The constructed antiparticle state is unstable in vacuum, failing to propagate with a constant velocity -v and period 2.
2. The head-on collision of the matched particle-antiparticle pair does not result in clean annihilation, leaving any localized bit remnants (non-zero bit count) within a 10^3 bounding box centered at the collision point after 80 steps.
3. The outgoing particles do not all propagate at the speed of light (v = 1c), or the total bit count deviates from exactly 8 at any step of the simulation.
4. The CPT-symmetry is violated, meaning that reversing the velocities of the outgoing radiation states and running the simulation forward fails to reconstruct the initial head-on gliders to bit-level precision.

**Proposed Method:**
1. Construct the antiparticle state of the LUT-08 sub-light glider on the 3D FCC grid by applying spatial reflection (Parity P, x -> -x) and velocity reversal (Time reversal T, reversing channel directions) to the standard 4-bit glider state.
2. Verify the stability of the antiparticle in vacuum by simulating it for 100 steps on a 64^3 grid and confirming it moves with velocity -v and period 2.
3. Set up a phase-swept, head-on collision experiment between the particle and its antiparticle on a 64^3 grid. Sweep the relative phase difference Delta phi in {0, 1} and impact offsets to find the precise alignment for clean annihilation.
4. Analyze the collision products after 80 steps. Quantify the remaining local bits at the collision center and the velocity of all outgoing bits.
5. Perform a CPT-reversibility test: reverse the velocity channels of the final outgoing state at step 80 and run the simulation forward for 80 steps to verify that the initial state is perfectly reconstructed.
6. Create `src/glider_annihilation_analysis.py` to execute this protocol and generate `src/pre_registration.md` to document the pre-registered experiment.

---

## Iteration 243 -> Planner [Strategic Guidance]

### Strategic Guidance: Manager's Note

While the transition to Phase 7.3 (Antiparticles & CPT Symmetries) is a logical next step, the proposed plan risks misinterpreting definitional constraints as emergent physical discoveries. You must apply strict scientific discipline before proceeding to the execution phase.

---

### 1. The Construction-vs-Empirical Test: "Massless Radiation" & Reversibility
*   **The $1c$ Speed Limit is Definitional:** In any standard 3D FCC Lattice Gas Cellular Automaton (LGCA), an isolated single bit in a velocity channel propagates at the speed of one lattice step per tick ($v=1c$) *by construction*. If a collision breaks the 4-bit bound states of the gliders into isolated single bits, those bits *must* travel at $1c$. This is a definitional consequence of the lattice propagation step, not "emergent massless radiation."
    *   *Action:* Reframe the hypothesis. The empirical discovery is **not** that the outgoing bits travel at $1c$, but rather that the bound 4-bit glider structure (representing rest mass) completely dissociates into uncoupled single-bit states (dissociation of rest mass) rather than scattering into other sub-light bound states or chaotic remnants.
*   **CPT Reversibility is Algebraic:** Bit-level reconstruction under time-reversal is a direct mathematical consequence of your strictly reversible CA rules and closed/periodic boundary conditions. It verifies that your code is bug-free, but it does not "prove" CPT as an emergent physical property.
    *   *Action:* Explicitly distinguish between *code verification* (reversibility check) and *physical observation* (annihilation dynamics) in your reporting.

### 2. Physical Constraints of "Annihilation" under Bit Conservation
*   **Bit Erasure is Impossible:** Because the underlying rules are strictly bit-conserving, "annihilation" cannot mean that the active bits disappear. 
    *   *Action:* Define "clean annihilation" strictly as the **complete structural dissociation of the two 4-bit sub-light gliders into eight independent, non-interacting 1-bit $v=1c$ states**, leaving zero bound states or sub-light structures at the collision center. Your falsification criteria must quantitatively state how you distinguish an uncoupled 1-bit state from a highly transient or weakly bound multi-bit structure.

### 3. Pre-Registration Mandate
*   You must write and commit your precise, mathematically formulated hypothesis and falsification criteria to `src/pre_registration.md` **before** running any simulations. 
*   Ensure your falsification criteria are quantitative: specify the exact spatial bounding box, the step threshold (e.g., $t=80$), and the exact definition of "independent single-bit states" (e.g., minimum pairwise distance between all 8 bits $\ge d$ at step $T$ to ensure no further local interactions can occur).

---

