Implement a new `StainedCollisionFitness` function in the evolutionary framework.

**File Location:** The relevant logic is likely in `src/fitness.py` and used by `src/evolution.py`. Please modify these or create new files as needed.

**Fitness Logic (`StagedCollisionFitness`):**
The function must provide a continuous gradient by awarding partial scores for key stages of a two-body collision.

1.  **Input:** A rule and the standard two-particle (L-tromino) initial state.
2.  **Simulation:** Run the simulation and capture the state at three checkpoints: `t_initial` (step 0), `t_mid` (e.g., step 200), and `t_final` (e.g., step 400).
3.  **Bit Conservation Check:** Verify that the total bit count is perfectly conserved at `t_mid` and `t_final` compared to `t_initial`. If conservation fails at any point, the fitness score is immediately **0.0**.
4.  **Center of Mass Calculation:** For each of the two objects, calculate its center of mass (CoM) at all three checkpoints.
5.  **Distance Calculation:** Calculate the Euclidean distance between the two CoMs at each checkpoint: `d_initial`, `d_mid`, `d_final`.
6.  **Staged Scoring:**
    *   Define a `MARGIN` of at least `1.0` grid units to prevent floating-point exploits.
    *   `approach_score = 1.0` if `d_mid < d_initial - MARGIN`, else `0.0`. This rewards rules that bring the particles closer together.
    *   `recession_score = 1.0` if `d_final > d_mid + MARGIN`, else `0.0`. This rewards rules that make the particles move apart after coming close.
7.  **Final Fitness:** The total fitness is `approach_score + recession_score`.
    *   A rule that achieves nothing gets 0.0.
    *   A rule that only makes particles approach gets 1.0.
    *   A rule that achieves a full approach-then-recede sequence gets 2.0.

This creates a clear gradient for the evolutionary search to optimize.

**Deliverable:**
- Modified source code with the new `StagedCollisionFitness` class.
- A brief confirmation in the result's `experimenter_view` that the class has been implemented as specified.