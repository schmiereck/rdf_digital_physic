You are working on a digital physics research project. Your task is twofold:

1. **Update the pre-registration file** at `src/pre_registration.md` to reflect the Research Manager's directives for Phase 248. The current file is incomplete — it only mentions a passive catalog audit. You must add the ACTIVE search requirements. The updated pre-registration must include:

## Hypothesis
(1) The FCC lattice under O_h-symmetric LUT rules admits at least one axis-aligned glider species (velocity parallel to an FCC nearest-neighbor direction, with integer Cartesian velocity components) that is NOT in the same O_h orbit as LUT-08, with bit-count 3–12 and period ≤ 8.
(2) Conditional on (1): Cross-species collisions between LUT-08 and any newly discovered axis-aligned species produce at least one stable propagating debris cluster that belongs to neither input species.

## Falsification Criteria
F1: The active targeted search (covering 3–12 bit seeds within compact neighborhoods, under LUT-08 and ≥3 additional O_h-symmetric LUTs, period ≤ 8) finds NO stable axis-aligned glider species in a distinct O_h orbit from LUT-08.
F2: No new stable propagating clusters emerge from any cross-species collision (9 impact parameters, 300-step debris analysis, vacuum isolation protocol).
F3: Any "new" clusters are sub-fragments of input species (trivial fragmentation).
F4: Collision outcome is not O_h-covariant (lattice-axis artifact).
F5: Effect only appears after post-hoc widening of parameter sweep beyond pre-declared ranges.

## Search Space Bounds
- Bit count: 3–12 bits per seed
- Spatial extent: cells within Manhattan distance ≤ 2 from origin
- Period: ≤ 8 steps
- Velocity criterion: axis-aligned = Cartesian velocity components are all integers (or half-integers at most, no irrational components)
- LUT rules tested: LUT-08 (reference) + ≥3 additional O_h-symmetric LUTs with different seeds
- Stability criterion: bit-conserving over 2×period steps, bounding extent ≤ 6 cells on every step
- Simulation grid: L=32 for screening, L=64 for verification
- O_h-equivalence: candidate must have a different O_h canonical form from LUT-08

## Stability Quantitative Thresholds
- Debris thermalization: surviving cluster must persist ≥ 300 steps in vacuum isolation with bit count conserved and extent ≤ 6
- Pair production: new species must be demonstrably NOT a sub-fragment of either input species (different bit count OR different O_h orbit from both inputs)

2. **Audit the iter_241 catalog** by reading `archive/iter_241/results/search_summary.json` and `archive/iter_241/results/exhaustive_search_report.md`. Document exactly what was searched and what was found. The audit should confirm that the iter_241 search was limited to only 100 candidates under a single LUT, justifying the need for an active expanded search.

Write the updated pre-registration to `src/pre_registration.md`. Write a brief audit report to `archive/iter_248/iter_248_1_audit.md` (create the directory first).

Key files to read:
- `src/pre_registration.md` (current pre-registration)
- `archive/iter_241/results/search_summary.json`
- `archive/iter_241/results/exhaustive_search_report.md`
