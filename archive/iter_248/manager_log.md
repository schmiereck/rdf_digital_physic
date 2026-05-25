# Research Manager Log - Iteration 248

## Iteration 248 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
(1) The iter_241 FCC glider catalog contains at least one O_h-orbit-distinct
glider species with a different bit-count and/or velocity from LUT-08
(i.e., the particle zoo has genuine diversity, not just directional variants of
a single species).
(2) Conditional on (1): Cross-species collisions between any two distinct species
from the catalog produce at least one stable propagating debris cluster that
belongs to neither input species, and whose formation rate scales positively
with total collision bit-energy (sum of input glider bit-counts weighted by speed).

**Proposed Falsification Criterion:**
F1: The iter_241 catalog contains only LUT-08 and its O_h-directional equivalents
(bit-count = 4, same speed in different directions) — catalog is monospecific.
F2: For every tested pair of distinct species and every impact parameter dy ∈ [-4,+4],
no new stable propagating clusters emerge from debris over 300 steps (using the
same vacuum isolation protocol from iter_247).
F3: Any "new" clusters are sub-fragments of input species (trivial fragmentation,
not pair production).
F4: Collision outcome is not O_h-covariant (beyond coordinate-rounding tolerance),
indicating lattice-axis artifact.
F5: Effect only appears after post-hoc widening of parameter sweep beyond
pre-declared ranges.

**Proposed Method:**
Stage 1 — Catalog Audit (medium complexity):
- Read the iter_241 glider catalog files from archive/iter_241/
- Extract all distinct O_h-orbit species with their bit-counts, periods,
  and velocities
- If only LUT-08 variants found → F1 triggered, close Phase 7 with null result,
  skip Stage 2
- Output: species_table.csv with columns [species_id, bit_count, period,
  velocity, O_h_orbit_id]

Stage 2 — Cross-Species Collision Scan (high complexity):
- For each pair of distinct species (A, B) from Stage 1:
  a. Place A and B on L=64 FCC grid in head-on collision geometry
  b. Test impact parameters dy ∈ [0, ±1, ±2, ±3, ±4] (9 values)
  c. Run each collision for 300 steps
  d. From step 60 onward, track all clusters via automated debris analysis
     (same method as iter_247)
  e. Apply O_h-equivalence filter to identify genuinely new species
  f. For any candidate new species, run 300-step vacuum isolation test
  g. Apply O_h covariance test: rotate initial conditions by one O_h
     element and verify outcome transforms covariantly
- Record whether any new species appears that is NOT a sub-fragment of
  either input species
- Test scaling: plot new-species appearance rate vs total input bit-energy

Stage 3 — Verdict (planner complexity):
- If F1 triggered: Declare Phase 7 complete with documented null results
  for 7.3 (no annihilation) and 7.4 (no pair production). Prepare Phase 7
  milestone report. Recommend advancing to Phase 8.
- If F2 triggered (no new species from any cross-species collision):
  Same as F1 — Phase 7 closes with comprehensive null result.
- If a new species IS confirmed (passes vacuum isolation, is not a
  sub-fragment, is O_h-covariant): Report as evidence for pair production,
  note the bit-energy threshold, and test whether the threshold scales
  predictably with rest-energy of produced species (Phase 7.4 scaling criterion).

Files to create/modify:
- src/experiment_248_catalog_audit.py: Stage 1 catalog reader
- src/experiment_248_cross_species.py: Stage 2 collision engine
- src/pre_registration.md: Pre-registration document
- archive/iter_248/: Results directory

---

## Iteration 248 -> Planner [Strategic Guidance]

### Strategic Guidance: Manager's Note

To maintain scientific rigour and ensure we do not prematurely close Phase 7 based on passive file-reading, you must refine your proposed plan according to the following directives:

1. **Actively Search, Do Not Passively Audit (Avoid the "Stale Catalog" Cop-out)**
   Stage 1 of your plan relies entirely on reading static files from `archive/iter_241/`. If that catalog is empty, incomplete, or contains only LUT-08 variants, **you must not immediately abort.** We have established that LUT-08's non-axis-aligned trajectory is a fundamental bottleneck for O_h covariance and collision dynamics. 
   * **Directive:** If the audited catalog does not contain a distinct, axis-aligned glider (e.g., propagation along high-symmetry axes of the FCC lattice like $v \parallel [1, 1, 0]$ or equivalent layer-stacking directions), you must **actively execute a targeted search** for axis-aligned species (up to 8 or 12 bits, period $\le 8$). 
   * Only if this active, targeted search yields a null result are you permitted to trigger $F1$ and declare Phase 7 complete.

2. **Pre-Registration & Falsification Rigour**
   The Orchestrator will automatically write and commit your pre-registration to `src/pre_registration.md` before execution. You must ensure this document defines:
   * The exact search space bounds (max bits, max period, specific velocity vectors) for the active axis-aligned search.
   * Clear mathematical criteria for O_h-equivalence to prevent taxonomic inflation (i.e., verifying if a candidate is in a different orbit of the $O_h$ group than LUT-08).
   * Quantitative thresholds for what constitutes "debris thermalization" vs. "stable pair production" (e.g., surviving cluster mass/period over 300 steps under vacuum isolation).

3. **Establish Geometric and Coordinate Resilience**
   If any novel glider species (especially axis-aligned ones) are discovered during the active search, you must test their solo propagation over 300 steps under at least two different proper $O_h$ rotations on the $L=64$ grid. This empirical test is required to prove that the new species is geometrically resilient to coordinate-rounding artifacts, unlike the non-axis-aligned LUT-08.

*Proceed with preparing your pre-registration and executing this refined strategy. A well-documented, active null result on axis-aligned glider existence is a highly valuable scientific contribution; a passive null result from reading a stale folder is not.*

---

