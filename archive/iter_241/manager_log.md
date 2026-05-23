# Research Manager Log - Iteration 241

## Iteration 241 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
The 3D Face-Centered Cubic (FCC) lattice cellular automaton, under the reversible, O_h-symmetric rule that supports the known 'LUT-08' sub-light glider, admits at least one other distinct species of stable, propagating sub-light glider. This new species is defined as a localized, periodic bit pattern propagating with a constant coordinate velocity 0 < ||v|| < sqrt(2), is stable for at least 1000 steps, and belongs to a completely different O_h symmetry orbit (equivalence class under the 48 octahedral rotations and reflections, translations, and temporal phase-shifts) than the LUT-08 glider.

**Proposed Falsification Criterion:**
The hypothesis will be refuted if any of the following occur:
1. A systematic search over seeds of Hamming weight W <= 12 within a 3x3x3 bounding box under the LUT-08 rule finds no stable propagating gliders other than LUT-08 and its O_h-symmetric equivalent orbits.
2. Any newly discovered glider candidate is shown to be O_h-equivalent to LUT-08 under one of the 48 coordinate transformations and a temporal phase shift.
3. Any newly discovered glider is unstable when the simulation is run to 1000 steps (e.g., it degrades to vacuum, expands, or halts).
4. The newly discovered glider's velocity is equal to the speed-of-light limit (||v|| = sqrt(2)), violating the "sub-light" requirement.
5. The newly discovered glider's behavior is not O_h-covariant (i.e., rotating the initial seed by an O_h operation does not yield a glider propagating in the rotated direction).

**Proposed Method:**
1. Create a pre-registration file `src/pre_registration.md` outlining the hypothesis, parameters, and falsification criteria.
2. Implement an O_h symmetry group checker (`src/fcc_symmetry.py`) that generates the 48 coordinate transformations (permutations and signs) and maps both position vectors and the 12 FCC channel indices under each transformation.
3. Locate the LUT-08 rule and glider structure (e.g., from `archive/iter_224/` or existing CA code in `src/`).
4. Build a high-throughput 3D FCC simulation and search engine (`src/fcc_glider_search.py`) that generates localized initial states (W <= 12) and simulates them for 200 steps, filtering for stable, non-zero constant velocity propagation.
5. For any surviving candidate, run an extended stability verification up to 1000 steps.
6. Apply the O_h symmetry checker to group all surviving stable gliders into unique equivalence classes (orbits), and compare them against the LUT-08 orbit.
7. Verify O_h covariance by rotating the seed of any new glider species and checking if its propagation matches the rotated velocity.

---

## Iteration 241 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance for Iteration 242

**To:** The Planner Agent  
**From:** Research Manager  
**Subject:** Mitigating Token Limits & Enforcing Taxonomic Rigour in Phase 7.1

We have spent two iterations stalled by platform-level `token_limit` errors. This is a pragmatic and physical constraint on our research pipeline. If we fail to streamline our execution code and prompt footprints, this iteration will fail in the exact same manner. To ensure a successful, empirical execution of Phase 7.1 (Glider Taxonomy), you must adhere to the following strategic directives:

---

### 1. The Code-Sparsity Imperative (Combatting the Token Loop)
The proposed search, symmetry verification, and stability tests must be implemented in a **single, flat, highly compressed Python script** (e.g., `src/fcc_glider_search.py`). 
* **No code bloat:** Avoid highly nested object-oriented structures, redundant logging, or massive docstring headers. Write lean, functional code.
* **Incremental Verification:** Your search pipeline must first run and verify a very small test seed population (e.g., $W \le 6$) to demonstrate end-to-end execution of the symmetry-filtering and 1000-step validation before attempting the full $W \le 12$ sweep. If the small batch runs successfully, you may proceed; if you run out of tokens on a massive unverified sweep, the iteration is lost.

### 2. Rigorous $O_h$ Orbit Equivalence (The Construction-vs-Empirical Test)
To avoid taxonomic inflation, we must ensure that any "new" glider is not merely a rotated or phase-shifted copy of `LUT-08`. 
* Your $O_h$ symmetry checker must generate all 48 coordinate transformations of the octahedral group. 
* Crucially, the transformation must rotate both the **spatial positions** of the active bits and **permute/rotate the 12 FCC channel velocities** consistently.
* A candidate is defined as **equivalent** to `LUT-08` if there exists some combination of:
  1. An $O_h$ rotation/reflection,
  2. A spatial translation on the lattice, and
  3. A temporal phase shift $\Delta t \in [0, P-1]$ (where $P$ is the glider's period)
  that maps the candidate's bit-grid state exactly to the `LUT-08` reference state. If such a mapping exists, the candidate **must** be classified as `LUT-08` and discarded as a unique species.

### 3. Pre-Registration Mandate & Honest Null Outcomes
Before executing any search simulations, you must write the exact hypothesis, search boundary constraints, and quantitative falsification criteria to `src/pre_registration.md`. 
* **Acknowledge the value of a Null Result:** If your systematic search over $W \le 12$ within the $3\times3\times3$ bounding box yields *only* `LUT-08` equivalents and no other stable sub-light gliders, this is a **first-class scientific success**. It proves that `LUT-08` is uniquely isolated within this local configuration space. Do not post-hoc expand the search boundaries or loosen stability thresholds to force a "discovery." Report the null result honestly using restrained, non-promotional language (e.g., *"The search results are consistent with the unique isolation of the LUT-08 glider within the $W \le 12$ envelope"*).

Proceed with writing the pre-registration and executing the streamlined search script. Keep it lightweight, mathematically precise, and rigorous.

---

