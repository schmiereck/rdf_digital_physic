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

