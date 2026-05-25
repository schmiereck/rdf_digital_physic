# Research Result 247 — Pair Production Experiment (Corrected)

## Pre-Declared Hypothesis & Falsification

**Hypothesis:** Same-chirality LUT-08 collisions produce debris from which at least one stable propagating glider species (distinct from LUT-08 in bit-count, period, or velocity) emerges within 200 steps post-collision, demonstrating that collision kinetic energy can be converted into the rest mass of new particle species.

**Falsification Criteria (pre-registered):**
- **F1:** No stable propagating patterns detected across all impact parameters → REFUTED
- **F2:** All propagating patterns are LUT-08 (after O_h filter) → REFUTED
- **F3:** All stable debris are stationary → REFUTED
- **F4:** Pair production not robust to ±1 lattice-unit variation → REFUTED

## Protocol

1. **Load LUT-08** (4-bit, period 2, v ≈ [0.5, 0.0, 1.0]) from `archive/iter_224/results/glider_00_lut08_sub03.json`
2. **Find same-chirality partner pC** via `find_pC()` over 48 O_h proper rotations (det=+1), selecting the transform whose step-1 displacement best matches −dA
3. **Confirm pC stability:** 80-step solo propagation on L=64 with constant 4-bit count
4. **Measure exact LUT-08 velocity:** 80-step average displacement via `compute_com_circular`
5. **Generate O_h orbit velocities:** Apply all 48 transforms to measured velocity vector
6. **Vacuum control:** Single LUT-08 on L=64 for 300 steps, confirm one 4-bit cluster at every 10-step checkpoint
7. **Collision experiments:** 9 impact parameters (dy = 0, ±1, ±2, ±3, ±4), pA at (20,32,20), pC at (44,32+dy,44), L=64, 300 steps, save grid every 10 steps
8. **Debris analysis (step 60–300):** Extract clusters via `grid_cells`, group by toroidal Manhattan distance ≤ 4, track across time by positional overlap
9. **Classification:**
   - Propagating: net CoM displacement ≥ 2 cells, velocity variance < 20%
   - Stationary: net CoM displacement < 1 cell
   - Transient: all others
10. **O_h orbit matching:** 4-bit + period 2 (±1) + velocity within 0.3 cells/tick of any O_h-rotated LUT-08 velocity → "LUT-08_scattered"
11. **Vacuum isolation:** NEW_CANDIDATE patterns tested solo on clean L=64 for 300 steps (constant bits, velocity drift < 10%, periodicity maintained)

## Observations

### LUT-08 Characterization
- **Measured velocity:** [0.5, 0.0, 1.0] cells/tick (confirmed over 80 steps)
- **pC stability:** Confirmed stable for 80 steps (4 bits conserved)
- **Vacuum control:** PASSED — single LUT-08 remained as one 4-bit cluster for entire 300 steps

### Collision Debris Summary (9 configurations)

| dy | Propagating | Stationary | Transient | New Candidates |
|----|-------------|------------|-----------|----------------|
| 0  | 0           | 0          | 74        | 0              |
| 1  | 0           | 0          | 74        | 0              |
| -1 | 0           | 0          | 74        | 0              |
| 2  | 0           | 0          | 74        | 0              |
| -2 | 0           | 0          | 74        | 0              |
| 3  | 0           | 0          | 74        | 0              |
| -3 | 0           | 0          | 74        | 0              |
| 4  | 0           | 0          | 74        | 0              |
| -4 | 0           | 0          | 73        | 0              |

**Key findings:**
- **Zero propagating clusters** detected across all 9 impact parameters
- **Zero stationary clusters** detected
- All debris classified as **transient**
- Cluster bit counts observed: 1-bit, 3-bit, 4-bit, and one 5-bit instance (dy=-4)
- No cluster survived the O_h filter as LUT-08_scattered (because none were propagating)
- **No new candidates** passed the vacuum isolation threshold

### Falsification Evaluation
- **F1:** TRUE — No stable propagating patterns in any configuration
- **F2:** FALSE — Not applicable (no propagating patterns at all)
- **F3:** FALSE — Not applicable (no stable debris of any kind)
- **F4:** FALSE — Not applicable (no pair production to test robustness)

## Verdict

**REFUTED** (triggered by F1)

The hypothesis that same-chirality LUT-08 collisions produce new stable propagating glider species is refuted under the tested conditions. Across all 9 impact parameters (dy = 0 through ±4), collision debris consisted entirely of transient clusters (1-bit, 3-bit, 4-bit, and occasional 5-bit fragments). No propagating patterns — neither LUT-08 nor novel species — were detected in the 300-step post-collision window.

The vacuum control confirmed that LUT-08 is stable in isolation, ruling out spontaneous decay as an explanation. The absence of propagating debris therefore indicates that same-chirality LUT-08 collisions on the L=64 toroidal grid result in complete fragmentation or thermalization rather than elastic scattering or pair production under these geometric conditions.

## Construction-vs-Empirical Note

This result is purely empirical. The LUT-08 glider and its same-chirality partner pC were discovered through prior automated search (iter_224/245). The collision outcomes were not engineered or anticipated — the automated cluster-tracking protocol was applied uniformly across all 9 configurations without post-hoc adjustment. The refutation is robust to the pre-registered ±1 lattice-unit variation test (F4) because the null result persists across the full dy sweep.

## Limitations

1. **Grid size:** L=64 may be too small for long-range elastic scattering; larger grids (L=128, L=256) could reveal different behavior if gliders require more separation to re-form after collision
2. **Collision geometry:** Only transverse offsets in the r-direction were tested; collisions with offsets in l or c, or with relative rotations, remain unexplored
3. **Tracking sensitivity:** The 10-step sampling interval and 4-cell clustering threshold may miss very short-lived propagating patterns that exist between snapshots
4. **Velocity variance threshold:** The 20% variance cutoff for "propagating" classification is strict; marginal cases with higher jitter were classified as transient
5. **Single species:** Only LUT-08 was tested. Other glider species discovered in iter_240 may exhibit different collision phenomenology
6. **Time horizon:** 300 steps may be insufficient if pair production requires longer settling times; however, the pre-registered protocol specified this window

---
*Result generated by src/experiment_247_pair_production.py (218 lines)*
*Output: archive/iter_247/results/pair_production_results.json*
