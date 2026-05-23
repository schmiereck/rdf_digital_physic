# Exhaustive Glider Search — Iteration 240.2

## Objective

Conduct an exhaustive, multi-method search for sub-light stable, propagating glider particles under the **LUT-08** rule on the 3D FCC lattice. Determine whether the previously discovered LUT-08 glider (`archive/iter_224/results/glider_00_lut08_sub03.json`) is the only such object or whether additional gliders exist in O_h orbits disjoint from it.

## Setup

- LUT source: `archive\iter_224\results\glider_00_lut08_sub03.json`
- Grid: toroidal, **L = 20**
- Simulation duration: **T = 80** steps
- Stability: bit count constant AND `max_extent <= 6`
- Propagation: `||cumulative_displacement|| >= 4.0` lattice units
- Symmetry: applied all 48 signed permutations of (l, r, c) coordinates; **4 of 48** preserved the engine's SHIFTS set and were used as the lattice symmetry group for canonicalization. The remaining 48-N transformations send SHIFTS to vectors outside the SHIFTS basis and so are not faithful actions on (l, r, c, ch) particles. (The full 48-element O_h does act on the abstract 12 channel indices via `get_oh_permutations()`, but that action is not the lattice symmetry of the engine's SHIFTS basis.)

## Reference glider (LUT-08, sub-3)

- Particle: `[(-1, 0, -1, 5), (-1, 1, 0, 5), (0, -1, -1, 5), (0, -1, 1, 6)]`
- Initial weight: W = 4
- Net displacement after T=80: **89.443** lattice units
- Stable: True
- Shape periodic: True, period: 40

## Method A — Systematic Connected Sweep

Enumerated all connected cell-coordinate shapes of size 1 and 2, where connectivity is defined by the 12 engine SHIFTS displacements. For each cell-shape and each W in {4, 5}, every assignment of W bits across the 12 channels of those cells was enumerated (each cell must carry at least one bit). Particles were deduplicated by canonical orbit representative before simulation.

- Total particles enumerated: ~203511
- Unique orbits enumerated: 76437
- Unique orbits simulated (random subsample if budget exceeded): 74759
- Gliders found by Method A: **8**

## Method B — Massive Randomized Compact Search

For each W in {4, 5, 6, 7, 8}, generated 300 unique compact contiguous random particles (built by alternating bit-addition within current cells and growth into adjacent cells, bounded to max coordinate extent 3). Particles were deduplicated by orbit and each unique orbit simulated.

- Unique particles generated (sum over W): 1500
- Unique orbits simulated: 1497
- Gliders found by Method B: **0**

## Method C — Genetic Algorithm

For each W in {4, 5, 6, 7, 8}: population 50, 10 generations. Initialization with compact random particles. Mutation shifts one bit to a neighboring cell/channel and rejects connectivity loss. Crossover BFS-picks W contiguous bits from the union of parents. Fitness = displacement norm (zero if not stable) + periodic bonus (2.0).

- Gliders found by Method C: **11**

## Aggregate Findings

- Total candidate glider records (across methods): 19
- Unique-orbit gliders (after O_h deduplication): 19
- Disjoint from LUT-08 reference orbit: **19**
- LUT-08 orbit re-detected by search: **False**

## Newly discovered gliders

### New glider #0: W=4, method A

- particle: `[(0, 0, 0, 0), (0, 0, 0, 3), (0, 0, 1, 0), (0, 0, 1, 3)]`
- displacement: **56.569** lattice units after T=80
- cumulative displacement vector: [0.0, 40.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #1: W=4, method A

- particle: `[(0, 0, 0, 4), (0, 0, 0, 7), (0, 0, 1, 4), (0, 0, 1, 7)]`
- displacement: **97.980** lattice units after T=80
- cumulative displacement vector: [40.0, 80.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #2: W=4, method A

- particle: `[(0, 0, 0, 0), (0, 0, 0, 3), (0, 1, -1, 0), (0, 1, -1, 3)]`
- displacement: **56.569** lattice units after T=80
- cumulative displacement vector: [0.0, 40.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #3: W=4, method A

- particle: `[(0, 0, 0, 4), (0, 0, 0, 7), (0, 1, -1, 4), (0, 1, -1, 7)]`
- displacement: **97.980** lattice units after T=80
- cumulative displacement vector: [40.0, 80.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #4: W=4, method A

- particle: `[(0, 0, 0, 0), (0, 0, 0, 3), (1, 1, 1, 0), (1, 1, 1, 3)]`
- displacement: **56.569** lattice units after T=80
- cumulative displacement vector: [0.0, 40.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #5: W=4, method A

- particle: `[(0, 0, 0, 4), (0, 0, 0, 7), (1, 1, 1, 4), (1, 1, 1, 7)]`
- displacement: **97.980** lattice units after T=80
- cumulative displacement vector: [40.0, 80.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #6: W=4, method A

- particle: `[(0, 0, 0, 0), (0, 0, 0, 3), (1, 0, 1, 0), (1, 0, 1, 3)]`
- displacement: **56.569** lattice units after T=80
- cumulative displacement vector: [0.0, 40.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #7: W=4, method A

- particle: `[(0, 0, 0, 4), (0, 0, 0, 7), (1, 0, 1, 4), (1, 0, 1, 7)]`
- displacement: **97.980** lattice units after T=80
- cumulative displacement vector: [40.0, 80.0, -40.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #8: W=4, method C

- particle: `[(0, 0, 0, 5), (0, 0, 0, 6), (1, 1, 0, 6), (2, 2, 0, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 4
- periodic shape: True, period: 40

### New glider #9: W=4, method C

- particle: `[(1, 1, 0, 5), (1, 1, 0, 6), (1, 2, -1, 5), (2, 2, 0, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #10: W=4, method C

- particle: `[(-1, 0, -1, 6), (0, 0, 0, 5), (0, 0, 0, 6), (1, 1, 0, 6)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.00000000000001, 0.0, 80.0]
- max extent: 4
- periodic shape: True, period: 40

### New glider #11: W=4, method C

- particle: `[(0, 0, 0, 5), (0, 0, 0, 6), (1, 1, 0, 5), (1, 1, 0, 6)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 4
- periodic shape: True, period: 40

### New glider #12: W=4, method C

- particle: `[(-1, 0, -1, 6), (0, 0, 0, 6), (1, 1, 0, 5), (1, 1, 0, 6)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #13: W=4, method C

- particle: `[(0, 0, 0, 5), (1, 1, 0, 5), (1, 1, 0, 6), (1, 2, -1, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 4
- periodic shape: True, period: 40

### New glider #14: W=4, method C

- particle: `[(0, 0, 0, 5), (0, 0, 0, 6), (1, 1, 0, 5), (1, 1, 1, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #15: W=4, method C

- particle: `[(-1, 0, -1, 6), (0, 0, 0, 5), (0, 0, 0, 6), (1, 1, 0, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #16: W=4, method C

- particle: `[(0, 0, 0, 5), (0, 0, 0, 6), (0, 1, 0, 5), (1, 1, 0, 6)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.000000000000014, 0.0, 80.0]
- max extent: 4
- periodic shape: True, period: 40

### New glider #17: W=4, method C

- particle: `[(1, 1, 0, 5), (1, 1, 0, 6), (1, 2, 0, 5), (2, 2, 0, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 3
- periodic shape: True, period: 40

### New glider #18: W=4, method C

- particle: `[(1, 1, 0, 6), (1, 1, 1, 5), (1, 2, -1, 5), (2, 2, 0, 5)]`
- displacement: **89.443** lattice units after T=80
- cumulative displacement vector: [40.0, 0.0, 80.0]
- max extent: 3
- periodic shape: True, period: 40

## Runtime: 592.0 s
