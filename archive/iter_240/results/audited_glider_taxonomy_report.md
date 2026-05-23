# Rigorous Glider Audit (LUT-08)

## Setup

- LUT source: `archive/iter_224/results/glider_00_lut08_sub03.json`
- Candidate gliders loaded from `archive/iter_240/results/new_glider_*.json`: **175**
- Reference particle included: **1**
- Total candidates audited: **176**
- Toroidal grid: L = 32
- Simulation steps: 200 (5 expected periods of P=40)
- Stability criterion: bit_count == initial_bits AND max_extent <= 6 on every step
- Symmetry group: full 48-element O_h, applied to (l, r, c) via signed-permutation matrices M_g coupled with induced 12-channel permutations
- c_max = sqrt(2)

## Aggregate results

- Distinct O_h equivalence classes: **164**
- STABLE classes: **22**
- Classes equivalent to LUT-08 reference orbit: **1**

## Per-class details

### Class 0 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [0, 0, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 1.7763568394002505e-15, 1.7763568394002505e-15]
- |displacement| over 200 steps: 0.000000
- Coordinate velocity v = |disp|/200: 0.000000
- Normalized speed v/c = v/sqrt(2): **0.000000**

### Class 1 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [1, 0, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 1.7763568394002505e-15, -96.03912461343366]
- |displacement| over 200 steps: 96.039125
- Coordinate velocity v = |disp|/200: 0.480196
- Normalized speed v/c = v/sqrt(2): **0.339550**

### Class 2 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [1, 1, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.011744273792441362, 1.7763568394002505e-15]
- |displacement| over 200 steps: 0.011744
- Coordinate velocity v = |disp|/200: 0.000059
- Normalized speed v/c = v/sqrt(2): **0.000042**

### Class 3 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [1, 1, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.011744273792441362, -96.03912461343366]
- |displacement| over 200 steps: 96.039125
- Coordinate velocity v = |disp|/200: 0.480196
- Normalized speed v/c = v/sqrt(2): **0.339550**

### Class 4 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 2], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -0.012957796875003424, 1.7763568394002505e-15]
- |displacement| over 200 steps: 0.012958
- Coordinate velocity v = |disp|/200: 0.000065
- Normalized speed v/c = v/sqrt(2): **0.000046**

### Class 5 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 0], [1, 0, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 1.7763568394002505e-15, 1.7763568394002505e-15]
- |displacement| over 200 steps: 0.000000
- Coordinate velocity v = |disp|/200: 0.000000
- Normalized speed v/c = v/sqrt(2): **0.000000**

### Class 6 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 0], [2, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.36133788240687, -98.21393694033534]
- |displacement| over 200 steps: 138.999749
- Coordinate velocity v = |disp|/200: 0.694999
- Normalized speed v/c = v/sqrt(2): **0.491438**

### Class 7 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 0], [2, 1, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.011744273792441362, -96.03912461343366]
- |displacement| over 200 steps: 96.039125
- Coordinate velocity v = |disp|/200: 0.480196
- Normalized speed v/c = v/sqrt(2): **0.339550**

### Class 8 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 2], [1, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 1.7763568394002505e-15, 96.03546079307586]
- |displacement| over 200 steps: 96.035461
- Coordinate velocity v = |disp|/200: 0.480177
- Normalized speed v/c = v/sqrt(2): **0.339537**

### Class 9 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 2], [1, 0, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -98.36133788240687, 98.5166527550594]
- |displacement| over 200 steps: 139.213806
- Coordinate velocity v = |disp|/200: 0.696069
- Normalized speed v/c = v/sqrt(2): **0.492195**

### Class 10 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 2], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -0.012957796875003424, 1.7763568394002505e-15]
- |displacement| over 200 steps: 0.012958
- Coordinate velocity v = |disp|/200: 0.000065
- Normalized speed v/c = v/sqrt(2): **0.000046**

### Class 11 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 0], [1, 0, 2, 2], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.02768222825372, -97.02060849815726]
- |displacement| over 200 steps: 137.212862
- Coordinate velocity v = |disp|/200: 0.686064
- Normalized speed v/c = v/sqrt(2): **0.485121**

### Class 12 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 0], [1, 1, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.011744273792441362, 96.03546079307586]
- |displacement| over 200 steps: 96.035462
- Coordinate velocity v = |disp|/200: 0.480177
- Normalized speed v/c = v/sqrt(2): **0.339537**

### Class 13 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 2], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -0.012957796875003424, -96.03912461343366]
- |displacement| over 200 steps: 96.039125
- Coordinate velocity v = |disp|/200: 0.480196
- Normalized speed v/c = v/sqrt(2): **0.339550**

### Class 14 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 2], [1, 1, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -98.30740524498248, 98.5166527550594]
- |displacement| over 200 steps: 139.175705
- Coordinate velocity v = |disp|/200: 0.695879
- Normalized speed v/c = v/sqrt(2): **0.492060**

### Class 15 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [1, 1, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 1.7763568394002505e-15, 1.7763568394002505e-15]
- |displacement| over 200 steps: 0.000000
- Coordinate velocity v = |disp|/200: 0.000000
- Normalized speed v/c = v/sqrt(2): **0.000000**

### Class 16 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [1, 1, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 1.7763568394002505e-15, -96.03912461343366]
- |displacement| over 200 steps: 96.039125
- Coordinate velocity v = |disp|/200: 0.480196
- Normalized speed v/c = v/sqrt(2): **0.339550**

### Class 17 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [1, 2, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 96.03546079307586, 1.7763568394002505e-15]
- |displacement| over 200 steps: 96.035461
- Coordinate velocity v = |disp|/200: 0.480177
- Normalized speed v/c = v/sqrt(2): **0.339537**

### Class 18 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.4657602248814, -98.21393694033534]
- |displacement| over 200 steps: 139.073662
- Coordinate velocity v = |disp|/200: 0.695368
- Normalized speed v/c = v/sqrt(2): **0.491700**

### Class 19 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 2, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 96.03546079307586, 1.7763568394002505e-15]
- |displacement| over 200 steps: 96.035461
- Coordinate velocity v = |disp|/200: 0.480177
- Normalized speed v/c = v/sqrt(2): **0.339537**

### Class 20 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 2, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.5166527550594, -98.21393694033534]
- |displacement| over 200 steps: 139.109699
- Coordinate velocity v = |disp|/200: 0.695548
- Normalized speed v/c = v/sqrt(2): **0.491827**

### Class 21 (UNSTABLE)

- Members: **3**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 2, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 96.03546079307586, -96.03912461343366]
- |displacement| over 200 steps: 135.817242
- Coordinate velocity v = |disp|/200: 0.679086
- Normalized speed v/c = v/sqrt(2): **0.480186**

### Class 22 (STABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 0], [0, 0, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 23 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 0], [1, 1, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 24 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 3], [0, 1, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 2 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 25 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 3], [1, 0, 2, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.00000000000001]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 26 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 1, 0, 0], [1, 0, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 27 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 1, 0, 3], [0, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 28 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 1, 0, 3], [1, 1, 0, 0], [1, 1, 0, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 29 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 0, 3], [1, 0, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 2 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 30 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [1, 0, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 31 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [1, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 4 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 32 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [2, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 4 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 33 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [2, 1, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 34 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 2, 0], [1, 0, 2, 3], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 4 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 99.99999999999999, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 35 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 0, 0], [1, 1, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 36 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 0, 3], [2, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 37 (STABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [1, 1, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 38 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [1, 1, 1, 3], [1, 2, 1, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 39 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [1, 1, 1, 3], [2, 1, 2, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 40 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [2, 1, 2, 3]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 41 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [2, 2, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 4 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 42 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 3], [1, 2, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 4 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 43 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [0, 0, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.2441865150641327, 165.75581348493583, -100.0]
- |displacement| over 200 steps: 193.597588
- Coordinate velocity v = |disp|/200: 0.967988
- Normalized speed v/c = v/sqrt(2): **0.684471**

### Class 44 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [0, 0, 1, 4], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.5882683752082336, 101.58826837520826, -100.0]
- |displacement| over 200 steps: 142.557704
- Coordinate velocity v = |disp|/200: 0.712789
- Normalized speed v/c = v/sqrt(2): **0.504018**

### Class 45 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [0, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9599182659418872, 100.97253375148293, -100.0]
- |displacement| over 200 steps: 142.113947
- Coordinate velocity v = |disp|/200: 0.710570
- Normalized speed v/c = v/sqrt(2): **0.502449**

### Class 46 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 100.9599182659419, -100.0]
- |displacement| over 200 steps: 142.105070
- Coordinate velocity v = |disp|/200: 0.710525
- Normalized speed v/c = v/sqrt(2): **0.502417**

### Class 47 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 0, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 166.0, -100.0]
- |displacement| over 200 steps: 193.803971
- Coordinate velocity v = |disp|/200: 0.969020
- Normalized speed v/c = v/sqrt(2): **0.685201**

### Class 48 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 0, 2, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 166.0, -100.0]
- |displacement| over 200 steps: 193.803971
- Coordinate velocity v = |disp|/200: 0.969020
- Normalized speed v/c = v/sqrt(2): **0.685201**

### Class 49 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 98.04069988596672, -96.33127392454377]
- |displacement| over 200 steps: 137.450497
- Coordinate velocity v = |disp|/200: 0.687252
- Normalized speed v/c = v/sqrt(2): **0.485961**

### Class 50 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 1, 0, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 101.99479036198538, -100.0]
- |displacement| over 200 steps: 142.852779
- Coordinate velocity v = |disp|/200: 0.714264
- Normalized speed v/c = v/sqrt(2): **0.505061**

### Class 51 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [0, 1, 0, 4], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.5882683752082336, 101.57564040446847, -100.00000000000001]
- |displacement| over 200 steps: 142.548705
- Coordinate velocity v = |disp|/200: 0.712744
- Normalized speed v/c = v/sqrt(2): **0.503986**

### Class 52 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [0, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 166.0, -100.0]
- |displacement| over 200 steps: 193.804025
- Coordinate velocity v = |disp|/200: 0.969020
- Normalized speed v/c = v/sqrt(2): **0.685201**

### Class 53 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 100.97253375148293, -100.0]
- |displacement| over 200 steps: 142.114033
- Coordinate velocity v = |disp|/200: 0.710570
- Normalized speed v/c = v/sqrt(2): **0.502449**

### Class 54 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [1, 1, 0, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 102.0, -100.0]
- |displacement| over 200 steps: 142.856499
- Coordinate velocity v = |disp|/200: 0.714282
- Normalized speed v/c = v/sqrt(2): **0.505074**

### Class 55 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [1, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 134.00000000000006, -99.99999999999997]
- |displacement| over 200 steps: 167.212377
- Coordinate velocity v = |disp|/200: 0.836062
- Normalized speed v/c = v/sqrt(2): **0.591185**

### Class 56 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 4], [0, 1, 1, 0], [0, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [98.420953237368, 198.4243595955314, -100.0]
- |displacement| over 200 steps: 243.020391
- Coordinate velocity v = |disp|/200: 1.215102
- Normalized speed v/c = v/sqrt(2): **0.859207**

### Class 57 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 4], [1, 0, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043551, 199.04800341043557, -100.0]
- |displacement| over 200 steps: 243.783951
- Coordinate velocity v = |disp|/200: 1.218920
- Normalized speed v/c = v/sqrt(2): **0.861906**

### Class 58 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 4], [1, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043554, 199.0611240441944, -100.0]
- |displacement| over 200 steps: 243.794664
- Coordinate velocity v = |disp|/200: 1.218973
- Normalized speed v/c = v/sqrt(2): **0.861944**

### Class 59 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 0, 0], [1, 0, 0, 4], [1, 0, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [32.5326445607741, 129.6020087349611, -97.67811260399283]
- |displacement| over 200 steps: 165.517574
- Coordinate velocity v = |disp|/200: 0.827588
- Normalized speed v/c = v/sqrt(2): **0.585193**

### Class 60 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 0, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9801532312425927, 100.95991826594187, -99.99999999999997]
- |displacement| over 200 steps: 142.105122
- Coordinate velocity v = |disp|/200: 0.710526
- Normalized speed v/c = v/sqrt(2): **0.502417**

### Class 61 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [1, 1, 0, 0], [1, 1, 0, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.5811173761375024, 101.57564040446857, -100.00000000000001]
- |displacement| over 200 steps: 142.548626
- Coordinate velocity v = |disp|/200: 0.712743
- Normalized speed v/c = v/sqrt(2): **0.503985**

### Class 62 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9801532312425927, 100.97253375148293, -100.0]
- |displacement| over 200 steps: 142.114085
- Coordinate velocity v = |disp|/200: 0.710570
- Normalized speed v/c = v/sqrt(2): **0.502449**

### Class 63 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [1, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [66.00000000000001, 133.99479036198537, -100.0]
- |displacement| over 200 steps: 179.751506
- Coordinate velocity v = |disp|/200: 0.898758
- Normalized speed v/c = v/sqrt(2): **0.635518**

### Class 64 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [2, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9925267691393493, 100.97253375148293, -100.0]
- |displacement| over 200 steps: 142.114171
- Coordinate velocity v = |disp|/200: 0.710571
- Normalized speed v/c = v/sqrt(2): **0.502449**

### Class 65 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 0, 0], [1, 1, 0, 4], [1, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [98.21826353008962, 196.0252517191866, -96.6512566360692]
- |displacement| over 200 steps: 239.612587
- Coordinate velocity v = |disp|/200: 1.198063
- Normalized speed v/c = v/sqrt(2): **0.847158**

### Class 66 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 0, 4], [2, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [34.01510278841495, 102.0, -100.0]
- |displacement| over 200 steps: 146.836737
- Coordinate velocity v = |disp|/200: 0.734184
- Normalized speed v/c = v/sqrt(2): **0.519146**

### Class 67 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 0, 4], [2, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 20 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.06952870744323, 199.0611240441944, -99.99999999999997]
- |displacement| over 200 steps: 243.803410
- Coordinate velocity v = |disp|/200: 1.219017
- Normalized speed v/c = v/sqrt(2): **0.861975**

### Class 68 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 1, 0], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9801532312425927, 100.9801532312426, -100.0]
- |displacement| over 200 steps: 142.119499
- Coordinate velocity v = |disp|/200: 0.710597
- Normalized speed v/c = v/sqrt(2): **0.502468**

### Class 69 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 1, 4], [1, 1, 2, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.06112404419443, 199.0611240441944, -100.00000000000001]
- |displacement| over 200 steps: 243.799995
- Coordinate velocity v = |disp|/200: 1.219000
- Normalized speed v/c = v/sqrt(2): **0.861963**

### Class 70 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 0], [0, 0, 1, 5]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, -30.0, 2.0]
- |displacement| over 200 steps: 30.133038
- Coordinate velocity v = |disp|/200: 0.150665
- Normalized speed v/c = v/sqrt(2): **0.106536**

### Class 71 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 0], [0, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9599182659418872, 99.04800341043563, -98.19306606230715]
- |displacement| over 200 steps: 139.475111
- Coordinate velocity v = |disp|/200: 0.697376
- Normalized speed v/c = v/sqrt(2): **0.493119**

### Class 72 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 0], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 99.04800341043563, -98.19306606230715]
- |displacement| over 200 steps: 139.475199
- Coordinate velocity v = |disp|/200: 0.697376
- Normalized speed v/c = v/sqrt(2): **0.493119**

### Class 73 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 5], [1, 0, 1, 5]]`
- Bit conserving: True
- Max extent over 200 steps: 21 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043551, 0.9599182659418872, 166.78870742187638]
- |displacement| over 200 steps: 193.984281
- Coordinate velocity v = |disp|/200: 0.969921
- Normalized speed v/c = v/sqrt(2): **0.685838**

### Class 74 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 5], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [34.00500184580668, 1.9947903619853902, 194.08028763655258]
- |displacement| over 200 steps: 197.046891
- Coordinate velocity v = |disp|/200: 0.985234
- Normalized speed v/c = v/sqrt(2): **0.696666**

### Class 75 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 0], [0, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9599182659418872, 99.06112404419449, -98.32555525778875]
- |displacement| over 200 steps: 139.577729
- Coordinate velocity v = |disp|/200: 0.697889
- Normalized speed v/c = v/sqrt(2): **0.493482**

### Class 76 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 20 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 99.0480034104356, -98.32555525778879]
- |displacement| over 200 steps: 139.568505
- Coordinate velocity v = |disp|/200: 0.697843
- Normalized speed v/c = v/sqrt(2): **0.493449**

### Class 77 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 0], [1, 1, 0, 5]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 2.0, 2.0]
- |displacement| over 200 steps: 3.461096
- Coordinate velocity v = |disp|/200: 0.017305
- Normalized speed v/c = v/sqrt(2): **0.012237**

### Class 78 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 5], [1, 1, 0, 5]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043551, 0.9801532312425927, 198.4765091344217]
- |displacement| over 200 steps: 221.820631
- Coordinate velocity v = |disp|/200: 1.109103
- Normalized speed v/c = v/sqrt(2): **0.784254**

### Class 79 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 5], [1, 2, 0, 5]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043551, 0.9925267691393493, 198.4765091344217]
- |displacement| over 200 steps: 221.820686
- Coordinate velocity v = |disp|/200: 1.109103
- Normalized speed v/c = v/sqrt(2): **0.784255**

### Class 80 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 5], [1, 2, 1, 5]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043551, 0.9925267691393493, 198.62252315825435]
- |displacement| over 200 steps: 221.951343
- Coordinate velocity v = |disp|/200: 1.109757
- Normalized speed v/c = v/sqrt(2): **0.784716**

### Class 81 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [1, 1, 1, 5], [1, 2, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [34.0, 1.9842698286878608, 33.999999999999986]
- |displacement| over 200 steps: 48.124187
- Coordinate velocity v = |disp|/200: 0.240621
- Normalized speed v/c = v/sqrt(2): **0.170145**

### Class 82 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 0, 1, 6], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0050018458066745, 98.37514846498692, -63.06531623778837]
- |displacement| over 200 steps: 116.871399
- Coordinate velocity v = |disp|/200: 0.584357
- Normalized speed v/c = v/sqrt(2): **0.413203**

### Class 83 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 0, 1, 6], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0050018458066745, 33.99479036198538, -30.03374831509622]
- |displacement| over 200 steps: 45.405857
- Coordinate velocity v = |disp|/200: 0.227029
- Normalized speed v/c = v/sqrt(2): **0.160534**

### Class 84 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 20 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 99.71464124950305, -98.21515637796011]
- |displacement| over 200 steps: 139.964897
- Coordinate velocity v = |disp|/200: 0.699824
- Normalized speed v/c = v/sqrt(2): **0.494851**

### Class 85 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 1, 0, 0], [1, 0, 1, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 65.99479036198538, -94.03374831509618]
- |displacement| over 200 steps: 114.898378
- Coordinate velocity v = |disp|/200: 0.574492
- Normalized speed v/c = v/sqrt(2): **0.406227**

### Class 86 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 1, 0, 6], [1, 0, 1, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043554, 64.97253375148287, 102.62252315825441]
- |displacement| over 200 steps: 156.726894
- Coordinate velocity v = |disp|/200: 0.783634
- Normalized speed v/c = v/sqrt(2): **0.554113**

### Class 87 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 0], [0, 0, 1, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 158.0, -26.0]
- |displacement| over 200 steps: 160.137441
- Coordinate velocity v = |disp|/200: 0.800687
- Normalized speed v/c = v/sqrt(2): **0.566171**

### Class 88 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 0], [0, 0, 2, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 130.0, -95.20684865694929]
- |displacement| over 200 steps: 161.146964
- Coordinate velocity v = |disp|/200: 0.805735
- Normalized speed v/c = v/sqrt(2): **0.569741**

### Class 89 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 0], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 97.14091467394171, -95.20684865694929]
- |displacement| over 200 steps: 136.020760
- Coordinate velocity v = |disp|/200: 0.680104
- Normalized speed v/c = v/sqrt(2): **0.480906**

### Class 90 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 7], [0, 1, 0, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 21 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.0400817340581, 199.0480034104357, -100.00000000000003]
- |displacement| over 200 steps: 243.780732
- Coordinate velocity v = |disp|/200: 1.218904
- Normalized speed v/c = v/sqrt(2): **0.861895**

### Class 91 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 7], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0050018458066745, 162.09936525700485, -95.20684865694929]
- |displacement| over 200 steps: 188.001511
- Coordinate velocity v = |disp|/200: 0.940008
- Normalized speed v/c = v/sqrt(2): **0.664686**

### Class 92 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [0, 1, 0, 7], [1, 2, 0, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [98.4225365214874, 130.92712549715995, -32.94558509714606]
- |displacement| over 200 steps: 167.075790
- Coordinate velocity v = |disp|/200: 0.835379
- Normalized speed v/c = v/sqrt(2): **0.590702**

### Class 93 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 97.16531578593188, -95.25433703338244]
- |displacement| over 200 steps: 136.071427
- Coordinate velocity v = |disp|/200: 0.680357
- Normalized speed v/c = v/sqrt(2): **0.481085**

### Class 94 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.5756404044685333, 101.58111737613751, -99.99999999999994]
- |displacement| over 200 steps: 142.552468
- Coordinate velocity v = |disp|/200: 0.712762
- Normalized speed v/c = v/sqrt(2): **0.503999**

### Class 95 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [1, 2, 1, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 97.84231748640534, -95.25433703338244]
- |displacement| over 200 steps: 136.566786
- Coordinate velocity v = |disp|/200: 0.682834
- Normalized speed v/c = v/sqrt(2): **0.482837**

### Class 96 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 7], [1, 1, 1, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 21 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [99.04800341043554, 199.06112404419443, -100.00000000000003]
- |displacement| over 200 steps: 243.794664
- Coordinate velocity v = |disp|/200: 1.218973
- Normalized speed v/c = v/sqrt(2): **0.861944**

### Class 97 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 7], [1, 2, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0050018458066745, 134.01510278841494, -100.00000000000003]
- |displacement| over 200 steps: 167.224603
- Coordinate velocity v = |disp|/200: 0.836123
- Normalized speed v/c = v/sqrt(2): **0.591228**

### Class 98 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [1, 1, 1, 0], [1, 2, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9801532312425927, 97.1732712139871, -95.25433703338244]
- |displacement| over 200 steps: 136.077162
- Coordinate velocity v = |disp|/200: 0.680386
- Normalized speed v/c = v/sqrt(2): **0.481105**

### Class 99 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 8], [0, 0, 1, 0], [1, 1, 0, 8]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 34.00500184580668, -1.9949981541933237]
- |displacement| over 200 steps: 34.063473
- Coordinate velocity v = |disp|/200: 0.170317
- Normalized speed v/c = v/sqrt(2): **0.120433**

### Class 100 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 0, 1, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.592625007514247, 98.47650913442175, -100.0]
- |displacement| over 200 steps: 140.357256
- Coordinate velocity v = |disp|/200: 0.701786
- Normalized speed v/c = v/sqrt(2): **0.496238**

### Class 101 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 0, 1, 9], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 21 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.0193711515304003, -61.24939615307875, -34.32555525778875]
- |displacement| over 200 steps: 70.219452
- Coordinate velocity v = |disp|/200: 0.351097
- Normalized speed v/c = v/sqrt(2): **0.248263**

### Class 102 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 0, 1, 9], [1, 1, 0, 9]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-134.30740524498245, -198.32555525778875, -100.00000000000003]
- |displacement| over 200 steps: 259.560215
- Coordinate velocity v = |disp|/200: 1.297801
- Normalized speed v/c = v/sqrt(2): **0.917684**

### Class 103 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 1, 0, 9], [1, 0, 1, 9]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-198.30740524498233, -198.32555525778872, -100.0]
- |displacement| over 200 steps: 297.756365
- Coordinate velocity v = |disp|/200: 1.488782
- Normalized speed v/c = v/sqrt(2): **1.052728**

### Class 104 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 0], [1, 0, 1, 9], [2, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-2.9637327149773096, 96.29095421740546, -100.0]
- |displacement| over 200 steps: 138.855074
- Coordinate velocity v = |disp|/200: 0.694275
- Normalized speed v/c = v/sqrt(2): **0.490927**

### Class 105 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 0], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 21 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.5, 33.19204520445369, -64.33127392454375]
- |displacement| over 200 steps: 72.391123
- Coordinate velocity v = |disp|/200: 0.361956
- Normalized speed v/c = v/sqrt(2): **0.255941**

### Class 106 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 0], [2, 0, 2, 9]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-3.9645392069241687, -2.0, -100.0]
- |displacement| over 200 steps: 100.098539
- Coordinate velocity v = |disp|/200: 0.500493
- Normalized speed v/c = v/sqrt(2): **0.353902**

### Class 107 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 9], [1, 1, 0, 9]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-134.26482947051346, -198.32555525778875, -100.00000000000003]
- |displacement| over 200 steps: 259.538187
- Coordinate velocity v = |disp|/200: 1.297691
- Normalized speed v/c = v/sqrt(2): **0.917606**

### Class 108 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 9], [2, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-196.03912461343344, -194.03374831509626, -100.0]
- |displacement| over 200 steps: 293.394673
- Coordinate velocity v = |disp|/200: 1.466973
- Normalized speed v/c = v/sqrt(2): **1.037307**

### Class 109 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 1, 0, 0], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.534239775118639, 98.78870742187635, -99.99999999999997]
- |displacement| over 200 steps: 140.575825
- Coordinate velocity v = |disp|/200: 0.702879
- Normalized speed v/c = v/sqrt(2): **0.497011**

### Class 110 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 1, 1, 9], [2, 2, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-196.03912461343344, -194.10188853062408, -100.0]
- |displacement| over 200 steps: 293.439741
- Coordinate velocity v = |disp|/200: 1.467199
- Normalized speed v/c = v/sqrt(2): **1.037466**

### Class 111 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 0, 1, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.13461241624495, -97.10769256103845]
- |displacement| over 200 steps: 137.350052
- Coordinate velocity v = |disp|/200: 0.686750
- Normalized speed v/c = v/sqrt(2): **0.485606**

### Class 112 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 0, 1, 0], [1, 0, 1, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.7662606278126596, -1.999999999999993, -97.10769256103845]
- |displacement| over 200 steps: 97.144344
- Coordinate velocity v = |disp|/200: 0.485722
- Normalized speed v/c = v/sqrt(2): **0.343457**

### Class 113 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 0, 1, 0], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.592625007514247, 98.6225231582544, -99.99999999999997]
- |displacement| over 200 steps: 140.459740
- Coordinate velocity v = |disp|/200: 0.702299
- Normalized speed v/c = v/sqrt(2): **0.496600**

### Class 114 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 1, 0, 0], [0, 1, 0, 10], [1, 1, 0, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-129.3690735757804, -131.1669745653573, -31.134612416244856]
- |displacement| over 200 steps: 186.843508
- Coordinate velocity v = |disp|/200: 0.934218
- Normalized speed v/c = v/sqrt(2): **0.660592**

### Class 115 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.14091467394168, -97.11280057791897]
- |displacement| over 200 steps: 137.358121
- Coordinate velocity v = |disp|/200: 0.686791
- Normalized speed v/c = v/sqrt(2): **0.485634**

### Class 116 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 0, 10], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-4.0, -66.03374831509629, -100.00000000000003]
- |displacement| over 200 steps: 119.901860
- Coordinate velocity v = |disp|/200: 0.599509
- Normalized speed v/c = v/sqrt(2): **0.423917**

### Class 117 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [1, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.13461241624495, -97.0876690537134]
- |displacement| over 200 steps: 137.335896
- Coordinate velocity v = |disp|/200: 0.686679
- Normalized speed v/c = v/sqrt(2): **0.485556**

### Class 118 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [1, 0, 2, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.7351705294865631, -1.999999999999993, -97.0876690537134]
- |displacement| over 200 steps: 97.123768
- Coordinate velocity v = |disp|/200: 0.485619
- Normalized speed v/c = v/sqrt(2): **0.343384**

### Class 119 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [2, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.13461241624495, -97.0876690537134]
- |displacement| over 200 steps: 137.335896
- Coordinate velocity v = |disp|/200: 0.686679
- Normalized speed v/c = v/sqrt(2): **0.485556**

### Class 120 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [2, 1, 2, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-0.49878056237523083, -31.0126756569477, -97.74817671545401]
- |displacement| over 200 steps: 102.551162
- Coordinate velocity v = |disp|/200: 0.512756
- Normalized speed v/c = v/sqrt(2): **0.362573**

### Class 121 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 10], [2, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-127.50125559722062, -130.00520963801458, -29.227575714059107]
- |displacement| over 200 steps: 184.423903
- Coordinate velocity v = |disp|/200: 0.922120
- Normalized speed v/c = v/sqrt(2): **0.652037**

### Class 122 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 10], [2, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-129.71310184880105, -130.12993149980838, -97.0876690537134]
- |displacement| over 200 steps: 207.810739
- Coordinate velocity v = |disp|/200: 1.039054
- Normalized speed v/c = v/sqrt(2): **0.734722**

### Class 123 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 10], [2, 1, 2, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-130.26504119018804, -193.63835583809683, -97.74817671545401]
- |displacement| over 200 steps: 253.020750
- Coordinate velocity v = |disp|/200: 1.265104
- Normalized speed v/c = v/sqrt(2): **0.894563**

### Class 124 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 0, 10], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.7351705294865631, -2.207659586111385, -97.11280057791897]
- |displacement| over 200 steps: 97.153387
- Coordinate velocity v = |disp|/200: 0.485767
- Normalized speed v/c = v/sqrt(2): **0.343489**

### Class 125 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 0, 10], [1, 1, 1, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-129.7351705294866, -193.21087973712315, -97.51694960893687]
- |displacement| over 200 steps: 252.331556
- Coordinate velocity v = |disp|/200: 1.261658
- Normalized speed v/c = v/sqrt(2): **0.892127**

### Class 126 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 1, 0], [2, 1, 2, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-0.49878056237523083, -63.04132805850463, -97.74817671545401]
- |displacement| over 200 steps: 116.314934
- Coordinate velocity v = |disp|/200: 0.581575
- Normalized speed v/c = v/sqrt(2): **0.411235**

### Class 127 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 1, 10], [2, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-126.9926714037725, -61.540081734058106, -97.01573017131216]
- |displacement| over 200 steps: 171.249444
- Coordinate velocity v = |disp|/200: 0.856247
- Normalized speed v/c = v/sqrt(2): **0.605458**

### Class 128 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 1, 10], [2, 1, 2, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-131.50729276757087, -196.55332994131743, -96.74817671545394]
- |displacement| over 200 steps: 255.514362
- Coordinate velocity v = |disp|/200: 1.277572
- Normalized speed v/c = v/sqrt(2): **0.903380**

### Class 129 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 0], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 20 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.534239775118639, 95.31592008470956, -98.26482947051346]
- |displacement| over 200 steps: 136.906739
- Coordinate velocity v = |disp|/200: 0.684534
- Normalized speed v/c = v/sqrt(2): **0.484038**

### Class 130 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 0], [1, 1, 1, 11]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -61.99499815419338, -98.00000000000001]
- |displacement| over 200 steps: 115.962838
- Coordinate velocity v = |disp|/200: 0.579814
- Normalized speed v/c = v/sqrt(2): **0.409991**

### Class 131 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 0], [2, 1, 2, 11]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.4833472449405338, -1.9006347429952113, -97.02570192575473]
- |displacement| over 200 steps: 97.055652
- Coordinate velocity v = |disp|/200: 0.485278
- Normalized speed v/c = v/sqrt(2): **0.343144**

### Class 132 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 11], [1, 1, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.158462243976924, -65.90063474299518, -64.28240674152313]
- |displacement| over 200 steps: 92.067712
- Coordinate velocity v = |disp|/200: 0.460339
- Normalized speed v/c = v/sqrt(2): **0.325509**

### Class 133 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 11], [1, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.534239775118639, -2.129931499808353, -33.0666650184709]
- |displacement| over 200 steps: 33.170692
- Coordinate velocity v = |disp|/200: 0.165853
- Normalized speed v/c = v/sqrt(2): **0.117276**

### Class 134 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 1, 1, 0], [2, 1, 2, 11]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.4833472449405338, -34.0, -97.02570192575476]
- |displacement| over 200 steps: 102.821142
- Coordinate velocity v = |disp|/200: 0.514106
- Normalized speed v/c = v/sqrt(2): **0.363528**

### Class 135 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 2], [1, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.36133788240687, -98.34153775602304]
- |displacement| over 200 steps: 139.089938
- Coordinate velocity v = |disp|/200: 0.695450
- Normalized speed v/c = v/sqrt(2): **0.491757**

### Class 136 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 2], [1, 1, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.011744273792441362, 0.0]
- |displacement| over 200 steps: 0.011744
- Coordinate velocity v = |disp|/200: 0.000059
- Normalized speed v/c = v/sqrt(2): **0.000042**

### Class 137 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 5], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 99.04800341043563, -98.45209785008123]
- |displacement| over 200 steps: 139.657683
- Coordinate velocity v = |disp|/200: 0.698288
- Normalized speed v/c = v/sqrt(2): **0.493764**

### Class 138 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 6], [0, 0, 2, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 66.0, -31.572505533199443]
- |displacement| over 200 steps: 73.190321
- Coordinate velocity v = |disp|/200: 0.365952
- Normalized speed v/c = v/sqrt(2): **0.258767**

### Class 139 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 7], [1, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9725337514828993, 36.95991826594189, -36.0]
- |displacement| over 200 steps: 51.604083
- Coordinate velocity v = |disp|/200: 0.258020
- Normalized speed v/c = v/sqrt(2): **0.182448**

### Class 140 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 7], [1, 0, 2, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 25 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.994790361985391, 130.0, -95.2275757140591]
- |displacement| over 200 steps: 161.159146
- Coordinate velocity v = |disp|/200: 0.805796
- Normalized speed v/c = v/sqrt(2): **0.569784**

### Class 141 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 9], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.592625007514247, 98.6225231582544, -100.0]
- |displacement| over 200 steps: 140.459740
- Coordinate velocity v = |disp|/200: 0.702299
- Normalized speed v/c = v/sqrt(2): **0.496600**

### Class 142 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 10], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.14091467394168, -97.10165824095321]
- |displacement| over 200 steps: 137.350243
- Coordinate velocity v = |disp|/200: 0.686751
- Normalized speed v/c = v/sqrt(2): **0.485606**

### Class 143 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 10], [1, 1, 2, 10]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, -30.503794151964172, -97.49999999999997]
- |displacement| over 200 steps: 102.160322
- Coordinate velocity v = |disp|/200: 0.510802
- Normalized speed v/c = v/sqrt(2): **0.361191**

### Class 144 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 1, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9599182659418872, 35.019846768757404, -34.622523158254374]
- |displacement| over 200 steps: 49.254748
- Coordinate velocity v = |disp|/200: 0.246274
- Normalized speed v/c = v/sqrt(2): **0.174142**

### Class 145 (UNSTABLE)

- Members: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 6], [0, 1, 1, 0], [0, 1, 1, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 65.99999999999999, -29.96625168490376]
- |displacement| over 200 steps: 72.511904
- Coordinate velocity v = |disp|/200: 0.362560
- Normalized speed v/c = v/sqrt(2): **0.256368**

### Class 146 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 2], [1, 2, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.34153775602303, -98.36133788240687]
- |displacement| over 200 steps: 139.089938
- Coordinate velocity v = |disp|/200: 0.695450
- Normalized speed v/c = v/sqrt(2): **0.491757**

### Class 147 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 2], [1, 2, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.34153775602303, -98.30740524498248]
- |displacement| over 200 steps: 139.051803
- Coordinate velocity v = |disp|/200: 0.695259
- Normalized speed v/c = v/sqrt(2): **0.491622**

### Class 148 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 2], [1, 2, 1, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.0, -0.012957796875003424]
- |displacement| over 200 steps: 0.012958
- Coordinate velocity v = |disp|/200: 0.000065
- Normalized speed v/c = v/sqrt(2): **0.000046**

### Class 149 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 4], [0, 1, 1, 4]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 161.37871048866361, -94.39868014173716]
- |displacement| over 200 steps: 186.971118
- Coordinate velocity v = |disp|/200: 0.934856
- Normalized speed v/c = v/sqrt(2): **0.661043**

### Class 150 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 7], [0, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9599182659418872, 100.9519965895644, -100.00000000000003]
- |displacement| over 200 steps: 142.099356
- Coordinate velocity v = |disp|/200: 0.710497
- Normalized speed v/c = v/sqrt(2): **0.502397**

### Class 151 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 1, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 20 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9599182659418872, 99.33473797991346, -98.4657602248814]
- |displacement| over 200 steps: 139.870717
- Coordinate velocity v = |disp|/200: 0.699354
- Normalized speed v/c = v/sqrt(2): **0.494518**

### Class 152 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 1, 2], [2, 1, 2, 2]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 0.011744273792441362, -96.01474994281597]
- |displacement| over 200 steps: 96.014751
- Coordinate velocity v = |disp|/200: 0.480074
- Normalized speed v/c = v/sqrt(2): **0.339463**

### Class 153 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 0, 1, 7], [2, 1, 2, 7]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 65.87006850019166, -95.2275757140591]
- |displacement| over 200 steps: 115.806550
- Coordinate velocity v = |disp|/200: 0.579033
- Normalized speed v/c = v/sqrt(2): **0.409438**

### Class 154 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 0, 1, 10], [1, 0, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 22 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 97.13461241624495, -97.10165824095321]
- |displacement| over 200 steps: 137.345786
- Coordinate velocity v = |disp|/200: 0.686729
- Normalized speed v/c = v/sqrt(2): **0.485591**

### Class 155 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 0], [2, 1, 2, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9067901292784057, 99.01984676875739, -99.15369362722106]
- |displacement| over 200 steps: 140.132820
- Coordinate velocity v = |disp|/200: 0.700664
- Normalized speed v/c = v/sqrt(2): **0.495444**

### Class 156 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 10], [1, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 17 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.6925947550175273, 98.1930660623072, -100.0]
- |displacement| over 200 steps: 140.159706
- Coordinate velocity v = |disp|/200: 0.700799
- Normalized speed v/c = v/sqrt(2): **0.495539**

### Class 157 (STABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 3], [2, 2, 0, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 3 (<=6: True)
- Exact shape period P: **2**
- Cumulative displacement: [0.0, 100.0, -100.0]
- |displacement| over 200 steps: 141.421356
- Coordinate velocity v = |disp|/200: 0.707107
- Normalized speed v/c = v/sqrt(2): **0.500000**

### Class 158 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 6], [2, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 20 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.9697333496073384, 93.73463559883982, -91.41471193901067]
- |displacement| over 200 steps: 130.934227
- Coordinate velocity v = |disp|/200: 0.654671
- Normalized speed v/c = v/sqrt(2): **0.462922**

### Class 159 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 9], [2, 1, 1, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.658462243976924, 98.3255552577888, -100.0]
- |displacement| over 200 steps: 140.252149
- Coordinate velocity v = |disp|/200: 0.701261
- Normalized speed v/c = v/sqrt(2): **0.495866**

### Class 160 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 1, 0], [1, 1, 1, 2], [2, 1, 2, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 18 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [0.0, 98.3074052449825, -98.34153775602304]
- |displacement| over 200 steps: 139.051803
- Coordinate velocity v = |disp|/200: 0.695259
- Normalized speed v/c = v/sqrt(2): **0.491622**

### Class 161 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 1, 0], [1, 1, 1, 6], [2, 1, 2, 6]]`
- Bit conserving: True
- Max extent over 200 steps: 24 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [2.0, 97.9949981541933, -61.99999999999999]
- |displacement| over 200 steps: 115.978531
- Coordinate velocity v = |disp|/200: 0.579893
- Normalized speed v/c = v/sqrt(2): **0.410046**

### Class 162 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 1, 11], [1, 2, 0, 11], [2, 1, 2, 11]]`
- Bit conserving: True
- Max extent over 200 steps: 23 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [-1.3727361503086435, -129.48501334330635, -64.65496684473239]
- |displacement| over 200 steps: 144.736028
- Coordinate velocity v = |disp|/200: 0.723680
- Normalized speed v/c = v/sqrt(2): **0.511719**

### Class 163 (UNSTABLE)

- Members: **1**
- Equivalent to LUT-08 reference: **True**
- Canonical particle: `[[0, 0, 0, 0], [2, 0, 3, 0], [2, 2, 2, 7], [4, 1, 5, 0]]`
- Bit conserving: True
- Max extent over 200 steps: 19 (<=6: False)
- Exact shape period P: **None**
- Cumulative displacement: [1.0, 100.88750526580479, -100.0]
- |displacement| over 200 steps: 142.053823
- Coordinate velocity v = |disp|/200: 0.710269
- Normalized speed v/c = v/sqrt(2): **0.502236**
