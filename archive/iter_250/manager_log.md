# Research Manager Log - Iteration 250

## Iteration 250 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
A bijective, bit-conserving LUT for the 12-channel FCC lattice, constructed by
introducing non-additive weight-2 mappings (where at least one weight-2 input
state maps to an output different from the independent sum of its weight-1
component transitions), can support at least one genuine dynamically-bound
multi-bit glider with binding energy > 0 that survives ≥200 propagation steps.

Specifically: starting from LUT-08's weight-1 sub-table (6 period-2
transpositions: ch0↔ch3, ch1↔ch2, ch4↔ch7, ch5↔ch6, ch8↔ch11, ch9↔ch10),
we replace the additive weight-2 sub-table with a non-additive permutation
of the 66 weight-2 states. When seeded with ≥2 bits in the same cell, at
least one such LUT variant will produce a stable propagating pattern where
the bits maintain correlated trajectories (binding energy > 0, verified by
Single-Bit Decomposition Test).

**Proposed Falsification Criterion:**
F1 (Construction Impossibility): Refuted if no bijective, bit-conserving
non-additive weight-2 permutation can be constructed from LUT-08's weight-1
sub-table while maintaining O_h symmetry (or, if O_h is relaxed, while
maintaining any valid permutation at all).

F2 (No Stable Structures): Refuted if ALL non-additive LUT variants produce
only chaotic (bit explosion >3x initial) or frozen (zero displacement after
step 50) dynamics from every multi-bit seed with ≥2 bits in the same cell,
with no structure surviving 200 steps.

F3 (Composite Only): Refuted if any stable propagating multi-bit structure
found under a non-additive LUT fails the Single-Bit Decomposition Test —
i.e., removing any single bit from the glider leaves the remaining bits'
propagation trajectory and speed unchanged, proving binding energy = 0.

F4 (O_h Non-Covariance): For O_h-symmetric LUT variants, refuted if any
found glider fails to transform covariantly under all 48 elements of O_h
(the glider's velocity and internal structure must rotate consistently).

**Proposed Method:**
EXPERIMENT 249: Non-Additive LUT Construction and Multi-Bit Glider Search

Step 1: Non-Additive LUT Construction Module (src/non_additive_lut.py)
- Load LUT-08's complete truth table as the base.
- Extract the weight-2 sub-table (66 entries) and identify:
  (a) 6 fixed-point pairs: {0,3}, {1,2}, {4,7}, {5,6}, {8,11}, {9,10}
  (b) 30 period-2 cycles from the remaining 60 states
- Construct O_h-symmetric non-additive variants by permuting fixed-point
  pairs within their O_h orbits:
  Variant A: Swap two fixed-point pairs {5,6}↔{4,7}
  Variant B: Create 3-cycle among fixed points {5,6}→{4,7}→{8,11}→{5,6}
  Variant C: Swap all 6 fixed points in paired exchanges
  Variant D: Redirect period-2 weight-2 cycles across transposition boundaries
- For each variant, verify: bijectivity (unique pre-images), bit conservation,
  non-additivity measure (count of weight-2 entries differing from additive).
- If O_h-symmetric variants cannot be constructed, relax O_h symmetry and
  construct arbitrary non-additive weight-2 permutations.
- Target: 20-50 distinct non-additive LUT variants.

Step 2: Systematic Seed Search (src/experiment_249_search.py)
- For each non-additive LUT variant:
  (a) Test all C(12,2)=66 weight-2 seeds (2 bits in same cell, all channel pairs)
  (b) Test 50 systematically chosen weight-3 seeds (3 bits in same cell)
  (c) Run each seed for 200 steps on L=32 FCC toroidal grid
  (d) Measure: bit_count_preservation, net_CoM_displacement, pattern_spread
- Control group: Run identical seed set under original additive LUT-08
  (expected: 0 genuine multi-bit gliders, confirming baseline)
- Identify candidates: bit_count preserved within 10%, displacement > 0,
  pattern spread < 4 lattice units (localization criterion).

Step 3: Three-Test Coherence Verification (on any candidates from Step 2)
- Single-Bit Decomposition Test: Remove one bit from the multi-bit seed;
  run remaining bits alone; compare trajectory and speed to the full glider.
  Binding energy > 0 iff trajectory or speed changes.
- Collision Coherence Test: Introduce a localized latency perturbation near
  the glider boundary; check if the glider coheres or fragments.
- Bit-Removal Stability Test: Remove each bit individually and test if
  the remaining pattern is structurally dependent on the removed bit.
- O_h Covariance Test: Apply all 48 O_h rotations to the glider seed;
  verify the resulting patterns propagate with rotated velocities.

Step 4: Evolutionary Search (if systematic search yields no candidates)
- Genome: the weight-2 sub-table permutation (66 entries)
- Mutation: swap two entries in the weight-2 permutation
- Crossover: recombine weight-2 sub-tables from two parent LUTs
- Fitness: max over all weight-2 seeds of (stability × displacement ×
  localization), where stability = 1 if bit_count preserved at step 200,
  displacement = |CoM(t=200) - CoM(t=0)|, localization = 1/(1 + spread).
- Constraint gate: reject any offspring that violates bijectivity or
  bit conservation.
- Population: 100 variants, 5 generations, 10 elites per generation.
- Starting population: seeded from best systematic variants + random
  non-additive permutations.

Step 5: 2D Hex Decomposition Check (src/experiment_249_hex_check.py)
- Load the iter_222 v=0.469c sub-light glider from the 2D hex grid.
- Extract individual bits and test if they propagate independently.
- If the glider is genuine (binding energy > 0): identify the mechanism
  that 2D hex has but 3D FCC lacks.
- If the glider is also a non-interacting composite: confirms the
  monospecificity is a general LGCA property, not FCC-specific.

Files to create/modify:
- src/non_additive_lut.py: Non-additive LUT construction module
- src/experiment_249_search.py: Systematic seed search experiment
- src/experiment_249_hex_check.py: 2D hex decomposition check
- src/pre_registration.md: Pre-registration document

---

## Iteration 250 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance for Iteration 249

The paradigm-shifting realization in Iteration 248—that our flagship 3D glider `LUT-08` is merely a non-interacting composite of single-bit particles—was a triumph of rigorous physical analysis. You correctly identified that single-cell additive collision operators $C$ are mathematically forbidden from creating bound states. 

Your proposal to transition to **non-additive collision LUT mutations** is the correct theoretical pivot. However, we must execute this with extreme scientific skepticism to ensure we do not replace one illusion with another. 

To guide this iteration, you must adhere strictly to the following three strategic directives:

---

### 1. The 2D Hex baseline Check is the Absolute Priority
Before you write complex generator code for 3D non-additive LUTs, you must perform the **2D Hex Decomposition Check** on the $v=0.469c$ glider (`champion_rule_perfect.json` from Iteration 222). 
* **The Question:** Is this 2D glider a genuinely bound particle with non-zero binding energy, or is it also a non-interacting composite of parallel single-bit streams? 
* **Action:** Isolate its constituent bits and simulate them. If it is a composite, this must be documented as an honest, foundational null result that recontextualizes our entire 2D history. If it is genuinely bound, analyze the precise mathematical mechanism that allows 2D hexagonal single-cell collisions to support binding where the 3D FCC single-cell collisions failed.

### 2. Guard the $O_h$ Symmetry Boundary (No Escape Hatches)
Your draft plan suggests relaxing $O_h$ symmetry if symmetric non-additive LUTs cannot be found. **Do not do this.** 
* Spatial covariance under the 48 elements of the octahedral group ($O_h$) is a non-negotiable physical constraint of our universe. A rule that achieves "binding" at the cost of breaking lattice symmetry is a classic parameter-tuning failure. 
* **Constraint:** Your search must strictly enforce $O_h$ symmetry on all non-additive LUT variants. If the entire space of $O_h$-symmetric, bijective, bit-conserving, non-additive single-cell LUTs yields zero stable multi-bit gliders, you must report this as a **definitive, honest null result** for single-cell LGCA. This would provide the necessary mathematical justification to transition to multi-site interaction rules in Phase 7.1.

### 3. Strict Pre-Registration of the Three-Test Coherence Protocol
The Orchestrator will automatically write and commit your finalized hypothesis and quantitative falsification criteria to `src/pre_registration.md` before execution begins. Your sub-agents must read and strictly adhere to this file. Ensure your pre-registered criteria are mathematically unyielding:
* **Quantitative F3 (Decomposition):** If a candidate $N$-bit glider is simulated, and any subset of $M < N$ bits propagates with the *same* velocity and trajectory as the original composite, the binding energy is $0.0$. F3 is triggered, and the candidate is refuted as a composite.
* **Isotropic Verification:** Any candidate that passes the coherence tests must be rotated using all 48 elements of $O_h$ to verify that its physical behavior is perfectly covariant.

Proceed with the construction of `src/pre_registration.md` and execute the 2D hex check and 3D non-additive search under these strict boundaries. Use restrained, falsifiable language in all generated reports.

---

