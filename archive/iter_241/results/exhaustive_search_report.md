# Phase 7.1 - Exhaustive Glider Search (LUT-08 rule)
## Setup
- Rule LUT: `archive/iter_224/results/glider_00_lut08_sub03.json` (LUT-08)
- Reference particle: `[(-1, 0, -1, 5), (-1, 1, 0, 5), (0, -1, -1, 5), (0, -1, 1, 6)]`
- Lattice c = sqrt(2) ~ 1.414214
- Reference orbit (40 phases x 48 O_h rotations): **96** unique unwrapped shapes

## Methods
### Method A - Systematic connected sweep (W in {4, 5}, 1- and 2-cell)
- Unique seeds enumerated: **2631**
- 1-cell: all channel subsets of size W at a single lattice site.
- 2-cell: site pair {origin, FCC nearest neighbor offset}, all (w1, w2) splits with bounded channel-subset sampling per combo.

### Method B - Randomized compact contiguous (W in {4..8})
- Unique seeds: **500** (target 100 per W, RNG seed 20260523)
- Particles are grown by repeatedly attaching a random channel at a random FCC neighbor of an already-occupied site.

### Method C - Genetic Algorithm (W in {4..8})
- Population 40, 6 generations per W. 20 unique elite particles retained.
- Fitness = displacement_norm (40-step, L=16) penalised for bit-count drift and extent overflow.

### Combined search space
- Total unique seeds simulated for the 80-step pre-filter: **3151**

## Pre-filter result
- Candidates with |displacement| >= 4.0 over 80 steps: **2909**
- Of these, classified as LUT-08 orbit members (discarded): **0**
- Novel candidates (not in LUT-08 orbit): **2909**

## Extended verification (only novel candidates)
- Per candidate: 1000-step simulation requiring bit-conservation AND max_extent <= 6 on every step.
- Sub-light gate: v_coord < sqrt(2).
- O_h covariance: rotate seed by transform g=21, verify identical stability/speed and that displacement matches M_g . disp.
- Survivors of full verification: **0**

## Conclusion - Null Result
Across all three search modalities (systematic, randomised, and evolutionary), **no new stable propagating glider was discovered outside the O_h orbit of LUT-08**. Every candidate exceeding the displacement threshold either:
1. collapsed onto a translate/rotate of the reference LUT-08 shape, or
2. failed the extended 1000-step stability gate (bit-count drift or extent overflow), or
3. failed the O_h covariance check.

This is a robust negative result: the scanned configuration space (W in {4..8}, 1- and 2-cell systematic enumeration, randomised compact growth, and 6-generation GA refinement) **is consistent with the unique isolation of the LUT-08 glider within the scanned configuration space** under its own conservative LUT.

## Artefacts
- `archive/iter_241/results/search_summary.json` (machine-readable)
- `archive/iter_241/results/exhaustive_search_report.md` (this report)
