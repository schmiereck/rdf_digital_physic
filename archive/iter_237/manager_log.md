# Research Manager Log - Iteration 237

## Iteration 237 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Redirection & Methodological Rigour

**To:** The Planner Agent  
**From:** Research Manager  
**Subject:** Procedural Victory on N-Body Null Result & Redesign Constraints for Phase 5.2/5.3

I want to formally commend the scientific integrity demonstrated in **iter_236**. By implementing identical vacuum controls ($\eta=0.0$), you successfully exposed the "orbital bound states" from iter_235 as an artifact of toroidal ballistic recurrence and lattice-axis velocity alignment. This is an exemplary application of our Falsification Protocol. Purging this major false positive is a triumph of our method. 

Now, we must systematically remediate the local coupling mechanism to see if a genuine, isotropic, non-ballistic attraction can be realized. You are directed to proceed under the following three strategic constraints:

---

### 1. Defeating the Toroidal Boundary Illusion (Boundary Hygiene)
To prevent wrap-around recurrence from ever simulating a "bound state" again, **you are barred from conducting future orbital or two-body attraction tests on small, wrapping tori without a direct control.** For your next experimental design, you must implement one of the following two boundary protocols:
*   **Absorbing/Open Boundary Conditions:** Any glider or bit that touches the boundary of the grid must be cleanly deleted. Under this protocol, a true bound state will remain in the grid, while any dispersive or unbound state will naturally vanish.
*   **Sub-Light Horizon Limit ($T < L/c$):** If using a torus, the grid size $L$ and simulation steps $T$ must be configured such that no glider can cross its own light-cone or wrap around the boundary to interact with its image or the other body via the torus. For a $32^3$ grid and a $v \approx 0.5c$ glider, this restricts your run-time to $T < 32$ steps—which is likely too short to observe orbits. Therefore, you must scale to a larger grid (e.g., $\ge 64^3$ or $128^3$) if you choose this path.

### 2. Coupling Redesign: Avoiding "Construction by Hand"
The current isotropic pheromone field ($\eta=2.0, \sigma=2.5, \gamma=0.9$) is confirmed to be dispersive. If you propose a new coupling mechanism (such as gradient-based trapping, anisotropic smoothing, or direct bit-contact latching), you must pass the **Construction-vs-Empirical Test**:
*   The mechanism must not "hardcode" an attractive vector. It must operate purely by modifying local computational latency (coordinate time) or local bit states, and the resulting attraction must *emerge* from the gliders' internal propagation rules interacting with that latency field.
*   If the coupling requires a highly specific, narrow parameter range to show *any* effect, you must report this honestly as a highly fine-tuned (and thus physically fragile) mechanism, rather than a robust emergent gravity.

### 3. Pre-Registration Mandate
Before running any code or simulations for the redesigned coupling:
1.  **Write down your exact mathematical/algorithmic hypothesis.**
2.  **Define the matched vacuum control protocol.**
3.  **State your explicit Falsification Criterion.** (e.g., *"The hypothesis of emergent attraction is refuted if the mean pair distance under active coupling is not at least $2\times$ lattice resolution closer than the vacuum control over $T$ steps, or if rotating the initial conditions by $90^\circ$ around the Z-axis changes the attraction magnitude by more than $15\%$"*).

We have established a clean, honest floor. Let us build the next step with the same exceptional rigor. I await your pre-registered proposal.

---

## Iteration 237 -> Planner (Turn 1) [Approval]

**Verdict:** APPROVED

**Journal Update:**
# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 5 (Discrete General Relativity).
*   **Active Direction:** Remediation of Phase 5.2 / 5.3 / 5.4 (Self-consistent attraction, orbits, and stability).
*   **Trajectory Update (Iteration 237):** Phase 5.4 has successfully refuted the gravitational origin of our Phase 5.3 "bound states" via a first-class null result. Matching-paired control runs demonstrated that the apparent 2-body orbit was a **ballistic recurrence** on the toroidal grid, and that the active latency field is actually dispersive for $N \ge 3$. We have paused Phase 5.4/5.5 progression and are redirecting to a fundamental redesign of the local coupling and boundary conditions.
*   **Confidence Score:** 30% (Re-evaluated downward because our primary attraction/orbital mechanism has been shown to be an artifact of toroidal geometry and discrete velocity alignment).

## 2. Strategic Insights & Lessons Learned
*   **The Ballistic Recurrence Illusion:** On a finite $32^3$ torus, discrete velocity alignments cause gliders to repeatedly cross paths or remain within a small spatial volume, mimicking a "bound state." Without a matching vacuum control ($\eta=0.0$), this kinematics is easily mistaken for dynamic gravitational binding.
*   **Dispersive Latency Fields:** The current pheromone latency scheme ($\eta=2.0$, $\sigma=2.5$, $\gamma=0.9$) acts as a dispersive barrier rather than an attractive potential well for multi-body systems, accelerating dispersion relative to the vacuum control.
*   **Skepticism Validation:** This iteration demonstrates the absolute necessity of Gate 2 (Falsification Audit) and running identical vacuum controls. A major false positive has been successfully purged.

## 3. Loop & Bottleneck Detection
*   **Toroidal Boundary Bottleneck:** Simulating on small tori ($32^3$) makes it virtually impossible to distinguish long-term orbits from toroidal wrap-around recurrence. Future orbital tests *must* use either absorbing boundary conditions (where dispersing gliders escape the grid) or vastly larger grids ($128^3+$) where the recurrence time is orders of magnitude longer than the orbital period.

## 4. Alternate Research Paths
*   **Absorbing/Infinite Boundaries:** Port the simulation to an open boundary grid where gliders that escape the central region are deleted or allowed to propagate infinitely without wrap-around.
*   **Gradient-Based Gravitational Latching:** Redesign the latency deposition to create a sharp local gradient that actively traps glider bits, rather than a smooth isotropic pheromone field which dilutes and scatters.

---

## Iteration 237 -> Project Archive [Milestone Report]

# RDF Milestone Review — Iteration 236 — Null Result: N-Body Gravitational Binding

## 1. Pre-Declared Hypothesis and Falsification Criterion
- **Working Hypothesis:** Mass-energy density acting as a dynamic local source of coordinate latency generates mutual gravitational-like attraction sufficient to form stable, hierarchical 3-body or 4-body bound states.
- **Falsification Criterion:** The hypothesis is refuted if, under the declared latency-coupling mechanism, the mutual separation of N gliders over >=160 steps is not smaller than that of the vacuum control ($\eta=0.0$) by at least 2x the lattice resolution (i.e., >=1.0 lattice units), or if the active coupling accelerates dispersion.

## 2. Experimental Protocol
- **Grid:** $32^3$ toroidal lattice.
- **Steps:** 160 steps.
- **Particles:** 3-body and 4-body configurations of LUT-08 sub-light gliders.
- **Parameters:** Coupling strength $\eta = 2.0$, smoothing scale $\sigma = 2.5$, decay rate $\gamma = 0.9$.
- **Control Run:** Identical initial coordinates and glider orientations on an identical grid with active coupling disabled ($\eta = 0.0$, pure vacuum propagation).

## 3. Observed Quantities
- **Bit-conservation:** Exact conservation of $4 \times N$ bits (12 bits for 3-body, 16 bits for 4-body) across all 160 steps.
- **Trajectory Dispersion:**
  - Active coupling runs ($\eta = 2.0$) demonstrated systematic repulsion/dispersion. Mean max pair distances were $+2.67$ to $+6.75$ lattice units larger than matched vacuum controls.
  - In Permutation 10 of the 3-body configuration, the vacuum control ($\eta = 0.0$) exhibited a pseudo-bound state with a mean max pair distance of $7.73 \le L/3$ due to velocity alignment on the torus, while the active coupling run dispersed.

## 4. Verdict
- **Refuted.** The outcome **refutes the hypothesis** that the current coordinate latency field can sustain stable hierarchical N-body bound states. The field is dispersive for $N \ge 3$ at the current envelope. Furthermore, the occurrence of torus capture in the matched vacuum control indicates that the previously observed 2-body orbit (Iteration 235) is an orientation-dependent ballistic alignment effect rather than a field-driven gravitational attraction.

## 5. Construction-vs-Empirical Note
- The bit conservation is exact by construction (enforced by the reversibility and binary rules of the underlying LGCA engine).
- The dispersive nature of the latency field and the presence of ballistic recurrence on the torus are empirical behaviors that represent genuine new information about how the coupled field behaves dynamically.

## 6. Limitations
- This null result is bound to the current localized pheromone-like latency deposition scheme ($\eta=2.0$, $\sigma=2.5$, $\gamma=0.9$) on a $32^3$ toroidal grid.
- It does not rule out other local coupling schemes (e.g., gradient-based direct trapping, anisotropic latency fields, or non-toroidal boundary conditions).

---

