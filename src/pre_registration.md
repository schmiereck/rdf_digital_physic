# RDF Scientific Pre-Registration

*   **Iteration:** 248
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
(1) The FCC lattice under O_h-symmetric LUT rules admits at least one axis-aligned glider species (velocity parallel to an FCC nearest-neighbor direction, with integer Cartesian velocity components) that is NOT in the same O_h orbit as LUT-08, with bit-count 3–12 and period ≤ 8.
(2) Conditional on (1): Cross-species collisions between LUT-08 and any newly discovered axis-aligned species produce at least one stable propagating debris cluster that belongs to neither input species.

## 2. Falsification Criteria
F1: The active targeted search (covering 3–12 bit seeds within compact neighborhoods, under LUT-08 and ≥3 additional O_h-symmetric LUTs, period ≤ 8) finds NO stable axis-aligned glider species in a distinct O_h orbit from LUT-08.
F2: No new stable propagating clusters emerge from any cross-species collision (9 impact parameters, 300-step debris analysis, vacuum isolation protocol).
F3: Any "new" clusters are sub-fragments of input species (trivial fragmentation).
F4: Collision outcome is not O_h-covariant (lattice-axis artifact).
F5: Effect only appears after post-hoc widening of parameter sweep beyond pre-declared ranges.

## 3. Search Space Bounds
- **Bit count:** 3–12 bits per seed
- **Spatial extent:** cells within Manhattan distance ≤ 2 from origin
- **Period:** ≤ 8 steps
- **Velocity criterion:** axis-aligned = Cartesian velocity components are all integers (or half-integers at most, no irrational components)
- **LUT rules tested:** LUT-08 (reference) + ≥3 additional O_h-symmetric LUTs with different seeds
- **Stability criterion:** bit-conserving over 2×period steps, bounding extent ≤ 6 cells on every step
- **Simulation grid:** L=32 for screening, L=64 for verification
- **O_h-equivalence:** candidate must have a different O_h canonical form from LUT-08

## 4. Stability Quantitative Thresholds
- **Debris thermalization:** surviving cluster must persist ≥ 300 steps in vacuum isolation with bit count conserved and extent ≤ 6
- **Pair production:** new species must be demonstrably NOT a sub-fragment of either input species (different bit count OR different O_h orbit from both inputs)

---

## 5. Proposed Method

### 5.1 iter_241 Catalog Audit (justification for active search)
- Review archive/iter_241/ to document the scope and findings of the prior search
- Confirm the search was limited to 100 candidates under a single LUT (LUT-08)
- Document that this narrow scope justifies the need for an expanded active search

### 5.2 Stage 1 — Active Targeted Glider Search (high complexity)
- Enumerate all seed configurations with bit-count 3–12 within Manhattan distance ≤ 2 of origin
- For each seed, simulate under LUT-08 and ≥3 additional O_h-symmetric LUT rules
- Detect axis-aligned glider candidates (integer/half-integer Cartesian velocity, period ≤ 8)
- Apply stability criterion: bit-conserving over 2×period steps, bounding extent ≤ 6 cells
- Compute O_h canonical form for each candidate; discard if O_h-equivalent to LUT-08
- Screen on L=32 grid; verify candidates on L=64 grid
- Output: species_table_248.csv with columns [species_id, lut_seed, bit_count, period, velocity, O_h_orbit_id, screen_l, verify_l]

### 5.3 Stage 2 — Cross-Species Collision Scan (high complexity)
- For each pair (LUT-08, newly discovered species) from Stage 1:
  a. Place both species on L=64 FCC grid in head-on collision geometry
  b. Test 9 impact parameters dy ∈ [0, ±1, ±2, ±3, ±4]
  c. Run each collision for 300 steps
  d. From step 60 onward, track all clusters via automated debris analysis
     (same method as iter_247)
  e. Apply O_h-equivalence filter to identify genuinely new species
  f. For any candidate new species, run 300-step vacuum isolation test
  g. Apply O_h covariance test: rotate initial conditions by one O_h
     element and verify outcome transforms covariantly
- Confirm new species is NOT a sub-fragment of either input (different bit count OR different O_h orbit)
- Record whether any new species appears and classify outcome

### 5.4 Stage 3 — Verdict (planner complexity)
- If F1 triggered: Declare active search complete with documented null result. Note that the expanded search under multiple LUTs still found no novel axis-aligned gliders. Recommend whether to broaden search space or pivot.
- If F2 triggered (no new species from any cross-species collision): Same as F1 — close with comprehensive null result for pair production.
- If a new species IS confirmed (passes vacuum isolation, is not a sub-fragment, is O_h-covariant): Report as evidence for novel glider species or pair production. Document bit-energy scaling and O_h orbit classification.

### 5.5 Falsification Decision Logic
| Criterion | Condition | Outcome |
|-----------|-----------|---------|
| F1 | Active search across 3–12 bit seeds, ≥4 LUTs, period ≤8 finds no distinct O_h-orbit species | Null: no new glider species |
| F2 | No new propagating debris from any collision (9 params, 300 steps) | Null: no pair production |
| F3 | All debris candidates are sub-fragments of inputs | Null: trivial fragmentation only |
| F4 | Collision outcome not O_h-covariant | Artifact: lattice-axis effect |
| F5 | New species only appears after widening beyond pre-declared ranges | Methodological warning: post-hoc |

Files to create/modify:
- src/experiment_248_active_search.py: Stage 1 active targeted search engine
- src/experiment_248_cross_species.py: Stage 2 collision engine
- src/pre_registration.md: Pre-registration document (this file)
- archive/iter_248/: Results directory
- archive/iter_248/iter_248_1_audit.md: Audit of iter_241 scope and findings

---
*Pre-registration updated per Research Manager directives for Phase 248: expanded from passive catalog audit to active targeted search across multiple O_h-symmetric LUT rules.*
