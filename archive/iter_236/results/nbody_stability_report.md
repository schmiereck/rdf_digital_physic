# Phase 5.4 — N-Body Stability Report

**Iteration:** 236  
**Engine:** `ClosedLoopLatchingEngine` (FFT-smoothed closed-loop latching, FCC 12-channel)  
**Grid size:** L = 32  
**Latency parameters:** gamma=0.9, eta_active=2.0, eta_control=0.0, threshold=0.045, alpha=2.0, sigma=2.5  
**LUT seed:** 8 (LUT-08 hierarchical glider, 4 bits/glider)  
**Simulation length:** 160 steps per run  

## 1. Pre-registration

This section was committed to the experiment script header before any simulation execution. It is reproduced verbatim here so the reader can verify the falsification criteria were not adjusted post-hoc.

**Working hypothesis.** Under the Phase 5.3 envelope (sigma=2.5, eta=2.0, gamma=0.9, threshold=0.045, alpha=2.0, LUT-08 glider), a hierarchical N-body configuration on the 3D+1 FCC-projected (Oh) lattice can be sustained over a 160-step window such that (a) bit conservation holds (total bits = 4*N), and (b) every glider remains within a finite radius of the system barycenter (i.e. no monotonic outward drift beyond the vacuum-control baseline).

**Falsification criteria.**
- **F1** — Bit-count drift: total active+latched bits != 4*N at any step (latching merger). Logged but does not invalidate the run.
- **F2** — Dispersion collapse: maximum particle distance from barycenter at step 160 exceeds the vacuum-control mean by more than 1 sigma for >= 2 of N particles.
- **F3** — Latching singularity: all particles coalesce (max pairwise distance < 2.0 lattice units) for >= 20 consecutive steps.

**Controls.** Active (eta=2.0) and vacuum (eta=0.0) runs are matched on initial conditions, Oh-permutation, and grid size.

**Oh-anisotropy controls.** Each configuration is run under Permutation 0 and Permutation 10. Stability that depends on a specific orientation is reported as a lattice-anisotropy limitation.

## 2. Protocol

- **Configurations.**
  - *3-body hierarchical:* tight binary at displacements `(0,-3,0)` and `(0,2,0)` from grid centre, plus a third glider at `(0, 10, 0)` (third_offset=8 along the row axis from the second binary member).
  - *4-body double-binary:* two binaries separated by 8 lattice units along both row and column axes.
- **Permutations.** Each configuration is executed with Oh permutation index `g=0` (identity) and `g=10` (90-degree layer/row swap mirror — matches the iter_235.8 long-term bound-state run).
- **Active vs vacuum.** `eta=2.0` versus `eta=0.0`; identical seeds and initial conditions otherwise.
- **Tracking.** At each step, active+latched bits are extracted, unwrapped onto a continuous frame using the previous step's barycenter as the reference, then partitioned into N clusters via a self-contained k-means++ implementation (deterministic seed). Glider coordinates are the cluster centroids; barycenter is the mean of the centroids.

## 3. Results

### 3.1 Active vs vacuum, 3-body and 4-body, both permutations

All distances are minimum-image (torus-correct) Euclidean distances; max possible value on a 32^3 torus is sqrt(3)*16 ~ 27.71. Classification thresholds (mean max pair dist): Captured <= L/3 (~10.67), Escaped >= 2L/3 (~21.33), Drifted otherwise.

| Config | N | Perm | eta | Bit cons. | max_pair_dist (mean / max / final) | max_dispersion (mean / max / final) | Verdict |
|---|---|---|---|---|---|---|---|
| 3body_hier__perm0__active | 3 | 0 | 2.0 | True | 16.48 / 21.13 / 19.58 | 11.16 / 21.14 / 15.86 | Drifted (intermediate) |
| 3body_hier__perm0__control | 3 | 0 | 0.0 | True | 12.65 / 13.00 / 10.50 | 7.25 / 12.20 / 11.63 | Drifted (intermediate) |
| 3body_hier__perm10__active | 3 | 10 | 2.0 | True | 14.48 / 25.21 / 7.57 | 10.85 / 22.36 / 4.20 | Drifted (intermediate) |
| 3body_hier__perm10__control | 3 | 10 | 0.0 | True | 7.73 / 15.03 / 15.03 | 6.05 / 18.29 / 17.79 | Captured (mean max pair dist <= L/3) |
| 4body_dblbin__perm0__active | 4 | 0 | 2.0 | True | 17.25 / 23.45 / 14.17 | 11.48 / 18.26 / 8.15 | Drifted (intermediate) |
| 4body_dblbin__perm0__control | 4 | 0 | 0.0 | True | 14.58 / 15.70 / 12.14 | 9.10 / 16.67 / 16.64 | Drifted (intermediate) |
| 4body_dblbin__perm10__active | 4 | 10 | 2.0 | True | 16.10 / 26.60 / 11.42 | 11.37 / 23.32 / 7.15 | Drifted (intermediate) |
| 4body_dblbin__perm10__control | 4 | 10 | 0.0 | True | 12.57 / 14.01 / 10.16 | 8.85 / 21.81 / 21.81 | Drifted (intermediate) |

Per-step logs are in:
- `archive/iter_236/results/nbody_3body_hier__perm0__active.csv`
- `archive/iter_236/results/nbody_3body_hier__perm0__control.csv`
- `archive/iter_236/results/nbody_3body_hier__perm10__active.csv`
- `archive/iter_236/results/nbody_3body_hier__perm10__control.csv`
- `archive/iter_236/results/nbody_4body_dblbin__perm0__active.csv`
- `archive/iter_236/results/nbody_4body_dblbin__perm0__control.csv`
- `archive/iter_236/results/nbody_4body_dblbin__perm10__active.csv`
- `archive/iter_236/results/nbody_4body_dblbin__perm10__control.csv`

### 3.2 Oh-symmetry / lattice-anisotropy check

For each configuration we compare Permutation 0 (identity) and Permutation 10. A verdict that flips between permutations would constitute a lattice-anisotropy limitation; identical verdicts across both orientations indicate orientation-independent N-body behaviour within the tested subset.

**3body_hier**:
  - active : Perm0 -> Drifted (intermediate); Perm10 -> Drifted (intermediate)
  - control: Perm0 -> Drifted (intermediate); Perm10 -> Captured (mean max pair dist <= L/3)

**4body_dblbin**:
  - active : Perm0 -> Drifted (intermediate); Perm10 -> Drifted (intermediate)
  - control: Perm0 -> Drifted (intermediate); Perm10 -> Drifted (intermediate)

### 3.3 Escape-velocity probe (3-body, varying third-glider offset)

Active (eta=2.0), Permutation 0. The first two gliders are fixed at the iter_235 binary geometry; the third glider's distance along the row axis is varied. Outcome classification rule (same as section 3.1): bit non-conservation -> *Latching/Collapse*; mean max-pair-distance >= 2L/3 -> *Escaped*; mean max-pair-distance <= L/3 -> *Captured*; otherwise the probe outcome bucket collapses 'Drifted' and 'Captured' under the same label *Captured* because the system remains on the torus.

| third_offset | outcome | bit conserved | max_pair_dist (mean / max) | max_dispersion (mean / max) |
|---|---|---|---|---|
| 4 | Captured | True | 14.34 / 20.21 | 10.28 / 21.03 |
| 6 | Captured | True | 15.65 / 20.55 | 10.76 / 19.92 |
| 8 | Captured | True | 16.48 / 21.13 | 11.16 / 21.14 |
| 10 | Captured | True | 17.86 / 22.25 | 12.01 / 18.61 |
| 12 | Captured | True | 19.57 / 24.13 | 13.13 / 19.03 |
| 14 | Captured | True | 20.68 / 24.70 | 13.72 / 19.20 |

Probe data in `nbody_escape_velocity.csv`.

## 4. Honest verdict

This section is written to satisfy the Manager's directive on non-promotional language. It records the most defensible interpretation of the data, including null and partial-null outcomes.

- Across the four active N-body runs (3-body & 4-body, perm 0 & 10): **Captured = 0**, **Drifted = 4**, **Escaped = 0**, **Latching/Collapse = 0**. Zero active runs achieved the *Captured* verdict at this envelope.

- **Active vs vacuum delta (mean max pair distance, torus-correct).** The active runs are systematically *more* dispersive than their vacuum controls in every configuration tested:

  | Config | Perm | active mean | control mean | delta (active - control) |
  |---|---|---|---|---|
  | 3body_hier | 0 | 16.48 | 12.65 | +3.83 |
  | 3body_hier | 10 | 14.48 | 7.73 | +6.75 |
  | 4body_dblbin | 0 | 17.25 | 14.58 | +2.67 |
  | 4body_dblbin | 10 | 16.10 | 12.57 | +3.53 |

  The active eta=2.0 latency field increases the mean max pair distance over vacuum in **4 of 4** N-body configurations. This is the opposite of the working hypothesis. We interpret this as a **first-class null result for N-body binding at the Phase 5.3 envelope**: the closed-loop latency field that sustained a 2-body bound state in iter_235 does *not* scale to bind 3- or 4-body configurations under the same envelope; instead it perturbs the gliders' trajectories and the vacuum control is the more localized regime.

- **Vacuum-control localization without latency field.** The 3-body Perm10 vacuum control is the only run that satisfies the *Captured* threshold (mp_mean = 7.73). Because no latency field is active in this control, the localization observed in iter_235 (two-body binary at Perm 10) is most parsimoniously attributed to **ballistic alignment of the glider's lattice-direction velocity vectors under that particular permutation**, rather than a true coordinate-latency binding mechanism. This re-interprets the Phase 5.3 result as orientation-dependent ballistic recurrence on the torus, not an emergent gravitational-like binding.

- **Oh anisotropy.** The 3-body active verdict is qualitatively the same across both tested permutations (both 'Drifted'); the 4-body active verdict is also permutation-invariant ('Drifted' x 2). However the control verdicts differ between permutations for the 3-body system ('Drifted' at Perm 0, 'Captured' at Perm 10). The vacuum-control discrepancy is a lattice-anisotropy signature, not an active-field signature.

- **Escape-velocity probe.** Across third-glider offsets of 4, 6, 8, 10, 12, 14 lattice units (Perm 0, eta=2.0) the outcome classifier returns *Captured* in every case (because mean max pair distance stays below the 2L/3 *Escaped* threshold). Mean max pair distance grows monotonically with offset (from 14.34 at offset 4 to 20.68 at offset 14), which is consistent with a third glider that is simply being launched further away and therefore samples a larger toroidal volume. The probe does **not** isolate a sharp escape-velocity transition; we cannot claim any binding-energy-like threshold here.

- **Bit conservation.** All 14 simulations (4 active+control pairs x 2 + 6 escape probe) preserved the expected bit count (4*N) at every step. No latching merger or annihilation event was observed. Falsification criterion **F1 is not triggered**.

- **Coalescence singularity.** No run produced a stretch >= 20 consecutive steps with max pairwise distance < 2.0. Falsification criterion **F3 is not triggered**.

- **F2 status.** In every active 3-body and 4-body run, the time-averaged max pair distance exceeds the matched control's by 3-7 lattice units, but never crosses the *Escaped* threshold. We do not have repeated trials at the same envelope, so we cannot fit a 1-sigma noise band; instead we report the deterministic delta as positive and monotonic, which is a **partial null** verdict against the working hypothesis. The hypothesis would require the active runs to be at least *as compact* as the controls; they are systematically *less* compact.

## 5. Limitations

- **Grid size.** L=32 keeps the maximum torus-correct Euclidean distance at sqrt(3)*16 ~ 27.71. The *Escaped*/*Captured* thresholds (2L/3 and L/3) are necessarily a function of L; with a larger grid a more definitive *Captured* envelope could be defined. The qualitative result (active runs more dispersive than controls) is unlikely to invert with grid size, but the absolute thresholds would shift.
- **K-means partitioning.** The clustering is constrained to exactly N centroids; when two gliders overlap on the same lattice neighbourhood the centroid pair becomes degenerate. We mitigate by warm-starting from the previous step's barycenter as the unwrap reference and by re-seeding up to three times if any cluster is empty. We do not attempt to detect splits/merges (which would require variable-K clustering). For 3- and 4-glider systems where the individual gliders are well-separated (most steps), this is adequate; the metric should be interpreted with caution during transient close encounters.
- **Anisotropy.** Only two of 48 Oh permutations are tested (g=0 and g=10). A full Oh-anisotropy sweep is outside the scope of this iteration but would be required to claim isotropy.
- **Single hierarchical geometry.** The 4-body run uses a double-binary with axis-aligned separations. Off-axis geometries (e.g. tetrahedral) are not explored here and could exhibit different bound-state physics.
- **No repeated trials.** Each (config, perm, eta) combination is run once. The simulation is deterministic given identical seeds, so the only source of randomness left is the k-means clustering, which uses a deterministic step-derived seed. Hence there is no per-run noise band to do a Welch t-test against; the active-vs-control comparisons are scalar deltas, not significance tests.
- **Single envelope.** Per the Manager's parameter-tuning-hygiene directive, only the Phase 5.3 envelope is probed. We explicitly do not search for parameter combinations that would force N-body stability; this is, by design, a hypothesis test of the existing envelope, not a tuning run.

## 6. Artifacts

- Script: `src/test_nbody_stability.py`
- Per-run CSV logs: `archive/iter_236/results/nbody_*.csv`
- Master JSON summary: `archive/iter_236/results/nbody_summary.json`
- Escape probe table: `archive/iter_236/results/nbody_escape_velocity.csv`
- This report: `archive/iter_236/results/nbody_stability_report.md`
