# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, `v<c` glider.

**Confirmed:**
- A new fitness function, `NetDisplacementFitness`, has been implemented. It is based on *net* start-to-end displacement to defeat oscillator exploits, while retaining a bounding-box penalty to defeat "puffer" exploits (iter_204.1).
- The `NetDisplacementFitness` function has been validated and proven to be robust against all previously discovered exploits, including the "puffer" and "compact oscillator" patterns (iter_204.2).

**Refuted:**
- N/A

**Best Result:**
- The `v=1c` elastic collision rule (`iter_193`) remains the best confirmed result for particle physics. No progress has been made on finding a `v<c` glider.

**In Progress:**
- **BLOCKED:** The `v<c` glider search is stalled. The evolutionary search experiment (iter_204.3) could not be run due to persistent "Usage quota exceeded" errors in the execution environment.

**Open Questions:**
- Can a `v<c` glider be found using the now-validated `NetDisplacementFitness` function once the execution environment is stable?
- Is the 3-bit L-tromino seed too prone to oscillation, and should we explore larger, more rigid seeds if the next search fails?
- Are there other search techniques besides evolution (e.g., direct construction) that might be better suited for finding `v<c` gliders?
