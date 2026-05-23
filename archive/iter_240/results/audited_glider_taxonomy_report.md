# Rigorous Glider Audit (LUT-08) - Original-Orientation Simulation Pipeline

## Setup

- LUT source: `archive/iter_224/results/glider_00_lut08_sub03.json`
- Candidate gliders loaded from `archive/iter_240/results/new_glider_*.json`: **175**
- Reference particle included: **1**
- Total candidates audited: **176**
- Toroidal grid: L = 32
- Simulation steps: 200 (5 expected periods of P=40)
- Stability criterion: bit_count == initial_bits AND max_extent <= 6 on every step of the unrotated candidate's original orientation
- Symmetry group for grouping: full 48-element O_h, applied to (l, r, c) via signed-permutation matrices M_g coupled with induced 12-channel permutations
- c_max = sqrt(2)

## Aggregate Results

- Total candidates loaded: **176** (175 new + 1 reference)
- STABLE candidates: **176**
- UNSTABLE candidates: **0**
- Unique STABLE O_h orbits found: **164**
- Stable orbits equivalent to LUT-08 reference orbit: **1**
  - The LUT-08 reference glider was successfully verified as **STABLE** (original unrotated orientation) and belongs to Orbit 163.
  - This reference orbit has **1** members.
- Non-reference unique stable orbits: **163**
  - **Verification**: The new stable orbits are **completely disjoint** from the reference orbit.

## Per-Orbit Details (Stable Classes only)

### Orbit 0 (STABLE)

- Representative: `new_glider_03_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [0, 0, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_03_W4_methodA.json`
- `new_glider_152_W4_methodC.json`

### Orbit 1 (STABLE)

- Representative: `new_glider_19_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [1, 0, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_19_W4_methodA.json`

### Orbit 2 (STABLE)

- Representative: `new_glider_90_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [1, 1, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -99.99999999999999]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_90_W4_methodA.json`

### Orbit 3 (STABLE)

- Representative: `new_glider_09_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 0], [1, 1, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -99.99999999999999]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_09_W4_methodA.json`
- `new_glider_68_W4_methodA.json`

### Orbit 4 (STABLE)

- Representative: `new_glider_38_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 1, 2], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_38_W4_methodA.json`

### Orbit 5 (STABLE)

- Representative: `new_glider_05_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 0], [1, 0, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_05_W4_methodA.json`
- `new_glider_153_W4_methodC.json`

### Orbit 6 (STABLE)

- Representative: `new_glider_13_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 0], [2, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_13_W4_methodA.json`

### Orbit 7 (STABLE)

- Representative: `new_glider_113_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 0], [2, 1, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -99.99999999999999]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_113_W4_methodA.json`

### Orbit 8 (STABLE)

- Representative: `new_glider_15_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 2], [1, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_15_W4_methodA.json`

### Orbit 9 (STABLE)

- Representative: `new_glider_99_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 2], [1, 0, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_99_W4_methodA.json`

### Orbit 10 (STABLE)

- Representative: `new_glider_158_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 1, 2], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_158_W4_methodC.json`

### Orbit 11 (STABLE)

- Representative: `new_glider_136_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 0], [1, 0, 2, 2], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -99.99999999999999]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_136_W5_methodA.json`

### Orbit 12 (STABLE)

- Representative: `new_glider_91_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 0], [1, 1, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_91_W4_methodA.json`

### Orbit 13 (STABLE)

- Representative: `new_glider_25_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 2], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_25_W4_methodA.json`

### Orbit 14 (STABLE)

- Representative: `new_glider_83_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 0, 2, 2], [1, 1, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_83_W4_methodA.json`

### Orbit 15 (STABLE)

- Representative: `new_glider_01_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [1, 1, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_01_W4_methodA.json`

### Orbit 16 (STABLE)

- Representative: `new_glider_76_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [1, 1, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_76_W4_methodA.json`

### Orbit 17 (STABLE)

- Representative: `new_glider_65_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [1, 2, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_65_W4_methodA.json`

### Orbit 18 (STABLE)

- Representative: `new_glider_57_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_57_W4_methodA.json`

### Orbit 19 (STABLE)

- Representative: `new_glider_36_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 2, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_36_W4_methodA.json`

### Orbit 20 (STABLE)

- Representative: `new_glider_74_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 2, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_74_W4_methodA.json`

### Orbit 21 (STABLE)

- Representative: `new_glider_129_W4_methodA.json`
- Number of stable members in orbit: **3**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 2], [1, 1, 1, 0], [2, 2, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_129_W4_methodA.json`
- `new_glider_35_W4_methodA.json`
- `new_glider_44_W4_methodA.json`

### Orbit 22 (STABLE)

- Representative: `new_glider_00_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 0], [0, 0, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_00_W4_methodA.json`
- `new_glider_121_W4_methodA.json`

### Orbit 23 (STABLE)

- Representative: `new_glider_78_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 0], [1, 1, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_78_W4_methodA.json`

### Orbit 24 (STABLE)

- Representative: `new_glider_111_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 3], [0, 1, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_111_W4_methodA.json`

### Orbit 25 (STABLE)

- Representative: `new_glider_110_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 0, 1, 3], [1, 0, 2, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.00000000000001]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_110_W4_methodA.json`

### Orbit 26 (STABLE)

- Representative: `new_glider_47_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 1, 0, 0], [1, 0, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_47_W4_methodA.json`

### Orbit 27 (STABLE)

- Representative: `new_glider_104_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 1, 0, 3], [0, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_104_W4_methodA.json`

### Orbit 28 (STABLE)

- Representative: `new_glider_142_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [0, 1, 0, 3], [1, 1, 0, 0], [1, 1, 0, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_142_W5_methodA.json`

### Orbit 29 (STABLE)

- Representative: `new_glider_81_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 0, 3], [1, 0, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_81_W4_methodA.json`

### Orbit 30 (STABLE)

- Representative: `new_glider_06_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [1, 0, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_06_W4_methodA.json`

### Orbit 31 (STABLE)

- Representative: `new_glider_116_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [1, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_116_W4_methodA.json`

### Orbit 32 (STABLE)

- Representative: `new_glider_48_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [2, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_48_W4_methodA.json`

### Orbit 33 (STABLE)

- Representative: `new_glider_43_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 1, 0], [2, 1, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -99.99999999999999]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_43_W4_methodA.json`

### Orbit 34 (STABLE)

- Representative: `new_glider_133_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 0, 2, 0], [1, 0, 2, 3], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -99.99999999999999, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_133_W5_methodA.json`

### Orbit 35 (STABLE)

- Representative: `new_glider_41_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 0, 0], [1, 1, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.00000000000001]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_41_W4_methodA.json`

### Orbit 36 (STABLE)

- Representative: `new_glider_109_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 0, 3], [2, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_109_W4_methodA.json`

### Orbit 37 (STABLE)

- Representative: `new_glider_04_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [1, 1, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_04_W4_methodA.json`
- `new_glider_127_W4_methodA.json`

### Orbit 38 (STABLE)

- Representative: `new_glider_131_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [1, 1, 1, 3], [1, 2, 1, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_131_W5_methodA.json`

### Orbit 39 (STABLE)

- Representative: `new_glider_137_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [1, 1, 1, 3], [2, 1, 2, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_137_W5_methodA.json`

### Orbit 40 (STABLE)

- Representative: `new_glider_70_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [2, 1, 2, 3]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_70_W4_methodA.json`

### Orbit 41 (STABLE)

- Representative: `new_glider_80_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 0], [2, 2, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_80_W4_methodA.json`

### Orbit 42 (STABLE)

- Representative: `new_glider_96_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 3], [1, 1, 1, 3], [1, 2, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_96_W4_methodA.json`

### Orbit 43 (STABLE)

- Representative: `new_glider_07_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [0, 0, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_07_W4_methodA.json`

### Orbit 44 (STABLE)

- Representative: `new_glider_140_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [0, 0, 1, 4], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_140_W5_methodA.json`

### Orbit 45 (STABLE)

- Representative: `new_glider_161_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [0, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_161_W4_methodC.json`

### Orbit 46 (STABLE)

- Representative: `new_glider_67_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_67_W4_methodA.json`

### Orbit 47 (STABLE)

- Representative: `new_glider_53_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 0, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_53_W4_methodA.json`

### Orbit 48 (STABLE)

- Representative: `new_glider_107_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 0, 2, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_107_W4_methodA.json`

### Orbit 49 (STABLE)

- Representative: `new_glider_150_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_150_W4_methodC.json`

### Orbit 50 (STABLE)

- Representative: `new_glider_160_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 0, 1, 0], [1, 1, 0, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_160_W4_methodC.json`

### Orbit 51 (STABLE)

- Representative: `new_glider_132_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [0, 1, 0, 4], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.00000000000001]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_132_W5_methodA.json`

### Orbit 52 (STABLE)

- Representative: `new_glider_16_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [0, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_16_W4_methodA.json`

### Orbit 53 (STABLE)

- Representative: `new_glider_112_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_112_W4_methodA.json`

### Orbit 54 (STABLE)

- Representative: `new_glider_156_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [1, 1, 0, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_156_W4_methodC.json`

### Orbit 55 (STABLE)

- Representative: `new_glider_154_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 0], [1, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_154_W4_methodC.json`

### Orbit 56 (STABLE)

- Representative: `new_glider_138_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 4], [0, 1, 1, 0], [0, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_138_W5_methodA.json`

### Orbit 57 (STABLE)

- Representative: `new_glider_66_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 4], [1, 0, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_66_W4_methodA.json`

### Orbit 58 (STABLE)

- Representative: `new_glider_155_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [0, 1, 0, 4], [1, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_155_W4_methodC.json`

### Orbit 59 (STABLE)

- Representative: `new_glider_141_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 0, 0], [1, 0, 0, 4], [1, 0, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_141_W5_methodA.json`

### Orbit 60 (STABLE)

- Representative: `new_glider_145_W4_methodB.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 0, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_145_W4_methodB.json`

### Orbit 61 (STABLE)

- Representative: `new_glider_130_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [1, 1, 0, 0], [1, 1, 0, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.00000000000001, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_130_W5_methodA.json`

### Orbit 62 (STABLE)

- Representative: `new_glider_124_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_124_W4_methodA.json`

### Orbit 63 (STABLE)

- Representative: `new_glider_114_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [1, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_114_W4_methodA.json`
- `new_glider_95_W4_methodA.json`

### Orbit 64 (STABLE)

- Representative: `new_glider_62_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 0, 1, 0], [2, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_62_W4_methodA.json`

### Orbit 65 (STABLE)

- Representative: `new_glider_143_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 0, 0], [1, 1, 0, 4], [1, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_143_W5_methodA.json`

### Orbit 66 (STABLE)

- Representative: `new_glider_64_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 0, 4], [2, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_64_W4_methodA.json`

### Orbit 67 (STABLE)

- Representative: `new_glider_87_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 0, 4], [2, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_87_W4_methodA.json`

### Orbit 68 (STABLE)

- Representative: `new_glider_26_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 1, 0], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_26_W4_methodA.json`

### Orbit 69 (STABLE)

- Representative: `new_glider_31_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 4], [1, 1, 1, 4], [1, 1, 2, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_31_W4_methodA.json`

### Orbit 70 (STABLE)

- Representative: `new_glider_02_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 0], [0, 0, 1, 5]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_02_W4_methodA.json`

### Orbit 71 (STABLE)

- Representative: `new_glider_93_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 0], [0, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_93_W4_methodA.json`

### Orbit 72 (STABLE)

- Representative: `new_glider_97_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 0], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_97_W4_methodA.json`

### Orbit 73 (STABLE)

- Representative: `new_glider_102_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 5], [1, 0, 1, 5]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_102_W4_methodA.json`

### Orbit 74 (STABLE)

- Representative: `new_glider_126_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 0, 1, 5], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_126_W4_methodA.json`

### Orbit 75 (STABLE)

- Representative: `new_glider_103_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 0], [0, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_103_W4_methodA.json`

### Orbit 76 (STABLE)

- Representative: `new_glider_69_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_69_W4_methodA.json`

### Orbit 77 (STABLE)

- Representative: `new_glider_72_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 0], [1, 1, 0, 5]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_72_W4_methodA.json`

### Orbit 78 (STABLE)

- Representative: `new_glider_125_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 5], [1, 1, 0, 5]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_125_W4_methodA.json`

### Orbit 79 (STABLE)

- Representative: `new_glider_10_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 5], [1, 2, 0, 5]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 2 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_10_W4_methodA.json`

### Orbit 80 (STABLE)

- Representative: `new_glider_98_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [0, 1, 0, 5], [1, 2, 1, 5]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_98_W4_methodA.json`

### Orbit 81 (STABLE)

- Representative: `new_glider_27_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 5], [1, 1, 1, 5], [1, 2, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_27_W4_methodA.json`

### Orbit 82 (STABLE)

- Representative: `new_glider_32_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 0, 1, 6], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_32_W4_methodA.json`

### Orbit 83 (STABLE)

- Representative: `new_glider_58_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 0, 1, 6], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_58_W4_methodA.json`

### Orbit 84 (STABLE)

- Representative: `new_glider_105_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_105_W4_methodA.json`

### Orbit 85 (STABLE)

- Representative: `new_glider_147_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 1, 0, 0], [1, 0, 1, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_147_W4_methodC.json`

### Orbit 86 (STABLE)

- Representative: `new_glider_123_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 6], [0, 1, 0, 6], [1, 0, 1, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_123_W4_methodA.json`
- `new_glider_148_W4_methodC.json`

### Orbit 87 (STABLE)

- Representative: `new_glider_11_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 0], [0, 0, 1, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_11_W4_methodC.json`

### Orbit 88 (STABLE)

- Representative: `new_glider_08_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 0], [0, 0, 2, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_08_W4_methodC.json`

### Orbit 89 (STABLE)

- Representative: `new_glider_20_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 0], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_20_W4_methodA.json`

### Orbit 90 (STABLE)

- Representative: `new_glider_14_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 7], [0, 1, 0, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_14_W4_methodC.json`

### Orbit 91 (STABLE)

- Representative: `new_glider_128_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 0, 1, 7], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_128_W4_methodA.json`

### Orbit 92 (STABLE)

- Representative: `new_glider_135_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [0, 1, 0, 7], [1, 2, 0, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [99.99999999999999, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_135_W5_methodA.json`

### Orbit 93 (STABLE)

- Representative: `new_glider_12_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_12_W4_methodA.json`

### Orbit 94 (STABLE)

- Representative: `new_glider_144_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [99.99999999999999, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_144_W5_methodA.json`

### Orbit 95 (STABLE)

- Representative: `new_glider_30_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 0], [1, 2, 1, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_30_W4_methodA.json`

### Orbit 96 (STABLE)

- Representative: `new_glider_21_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 7], [1, 1, 1, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_21_W4_methodA.json`

### Orbit 97 (STABLE)

- Representative: `new_glider_120_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [0, 1, 0, 7], [1, 2, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_120_W4_methodA.json`

### Orbit 98 (STABLE)

- Representative: `new_glider_29_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 7], [1, 1, 1, 0], [1, 2, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_29_W4_methodA.json`

### Orbit 99 (STABLE)

- Representative: `new_glider_39_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 8], [0, 0, 1, 0], [1, 1, 0, 8]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -99.99999999999999]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_39_W4_methodA.json`

### Orbit 100 (STABLE)

- Representative: `new_glider_119_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 0, 1, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_119_W4_methodA.json`

### Orbit 101 (STABLE)

- Representative: `new_glider_108_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 0, 1, 9], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_108_W4_methodA.json`

### Orbit 102 (STABLE)

- Representative: `new_glider_24_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 0, 1, 9], [1, 1, 0, 9]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_24_W4_methodA.json`

### Orbit 103 (STABLE)

- Representative: `new_glider_79_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [0, 1, 0, 9], [1, 0, 1, 9]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_79_W4_methodA.json`

### Orbit 104 (STABLE)

- Representative: `new_glider_134_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 0], [1, 0, 1, 9], [2, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_134_W5_methodA.json`

### Orbit 105 (STABLE)

- Representative: `new_glider_59_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 0], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_59_W4_methodA.json`

### Orbit 106 (STABLE)

- Representative: `new_glider_40_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 0], [2, 0, 2, 9]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_40_W4_methodA.json`

### Orbit 107 (STABLE)

- Representative: `new_glider_88_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 9], [1, 1, 0, 9]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_88_W4_methodA.json`

### Orbit 108 (STABLE)

- Representative: `new_glider_106_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 0, 1, 9], [2, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, 100.0, -100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_106_W4_methodA.json`

### Orbit 109 (STABLE)

- Representative: `new_glider_52_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 1, 0, 0], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_52_W4_methodA.json`

### Orbit 110 (STABLE)

- Representative: `new_glider_11_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 9], [1, 1, 1, 9], [2, 2, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_11_W4_methodA.json`

### Orbit 111 (STABLE)

- Representative: `new_glider_37_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 0, 1, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_37_W4_methodA.json`

### Orbit 112 (STABLE)

- Representative: `new_glider_18_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 0, 1, 0], [1, 0, 1, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_18_W4_methodA.json`

### Orbit 113 (STABLE)

- Representative: `new_glider_51_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 0, 1, 0], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_51_W4_methodA.json`

### Orbit 114 (STABLE)

- Representative: `new_glider_139_W5_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 1, 0, 0], [0, 1, 0, 10], [1, 1, 0, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.00000000000001, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_139_W5_methodA.json`

### Orbit 115 (STABLE)

- Representative: `new_glider_42_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [0, 1, 0, 0], [1, 0, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_42_W4_methodA.json`

### Orbit 116 (STABLE)

- Representative: `new_glider_117_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 0, 10], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_117_W4_methodA.json`

### Orbit 117 (STABLE)

- Representative: `new_glider_115_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [1, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_115_W4_methodA.json`

### Orbit 118 (STABLE)

- Representative: `new_glider_118_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [1, 0, 2, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_118_W4_methodA.json`

### Orbit 119 (STABLE)

- Representative: `new_glider_82_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [2, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_82_W4_methodA.json`

### Orbit 120 (STABLE)

- Representative: `new_glider_101_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 0], [2, 1, 2, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_101_W4_methodA.json`

### Orbit 121 (STABLE)

- Representative: `new_glider_85_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 10], [2, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_85_W4_methodA.json`

### Orbit 122 (STABLE)

- Representative: `new_glider_92_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 10], [2, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_92_W4_methodA.json`

### Orbit 123 (STABLE)

- Representative: `new_glider_56_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 0, 1, 10], [2, 1, 2, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_56_W4_methodA.json`

### Orbit 124 (STABLE)

- Representative: `new_glider_55_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 0, 10], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_55_W4_methodA.json`

### Orbit 125 (STABLE)

- Representative: `new_glider_09_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 0, 10], [1, 1, 1, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_09_W4_methodC.json`

### Orbit 126 (STABLE)

- Representative: `new_glider_75_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 1, 0], [2, 1, 2, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_75_W4_methodA.json`

### Orbit 127 (STABLE)

- Representative: `new_glider_08_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 1, 10], [2, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_08_W4_methodA.json`

### Orbit 128 (STABLE)

- Representative: `new_glider_12_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 10], [1, 1, 1, 10], [2, 1, 2, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_12_W4_methodC.json`

### Orbit 129 (STABLE)

- Representative: `new_glider_151_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 0], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_151_W4_methodC.json`

### Orbit 130 (STABLE)

- Representative: `new_glider_23_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 0], [1, 1, 1, 11]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_23_W4_methodA.json`
- `new_glider_63_W4_methodA.json`

### Orbit 131 (STABLE)

- Representative: `new_glider_22_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 0], [2, 1, 2, 11]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -99.99999999999999]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_22_W4_methodA.json`

### Orbit 132 (STABLE)

- Representative: `new_glider_159_W4_methodC.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 11], [1, 1, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_159_W4_methodC.json`
- `new_glider_86_W4_methodA.json`

### Orbit 133 (STABLE)

- Representative: `new_glider_28_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 0, 1, 11], [1, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_28_W4_methodA.json`

### Orbit 134 (STABLE)

- Representative: `new_glider_73_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 0, 11], [1, 1, 1, 0], [2, 1, 2, 11]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_73_W4_methodA.json`

### Orbit 135 (STABLE)

- Representative: `new_glider_100_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 2], [1, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_100_W4_methodA.json`

### Orbit 136 (STABLE)

- Representative: `new_glider_149_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 2], [1, 1, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_149_W4_methodC.json`

### Orbit 137 (STABLE)

- Representative: `new_glider_49_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 5], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_49_W4_methodA.json`

### Orbit 138 (STABLE)

- Representative: `new_glider_14_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 6], [0, 0, 2, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_14_W4_methodA.json`

### Orbit 139 (STABLE)

- Representative: `new_glider_17_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 7], [1, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_17_W4_methodC.json`

### Orbit 140 (STABLE)

- Representative: `new_glider_16_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 7], [1, 0, 2, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_16_W4_methodC.json`

### Orbit 141 (STABLE)

- Representative: `new_glider_89_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 9], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_89_W4_methodA.json`

### Orbit 142 (STABLE)

- Representative: `new_glider_10_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 10], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_10_W4_methodC.json`

### Orbit 143 (STABLE)

- Representative: `new_glider_15_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 10], [1, 1, 2, 10]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_15_W4_methodC.json`

### Orbit 144 (STABLE)

- Representative: `new_glider_71_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 1, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_71_W4_methodA.json`

### Orbit 145 (STABLE)

- Representative: `new_glider_33_W4_methodA.json`
- Number of stable members in orbit: **2**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 0, 1, 6], [0, 1, 1, 0], [0, 1, 1, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 200.0, -100.0]
  - |displacement| over 200 steps: 244.948974
  - Coordinate velocity v = |disp|/200: 1.224745
  - Normalized speed v/c = v/sqrt(2): **0.866025**

#### Members in this orbit:
- `new_glider_33_W4_methodA.json`
- `new_glider_60_W4_methodA.json`

### Orbit 146 (STABLE)

- Representative: `new_glider_50_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 2], [1, 2, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_50_W4_methodA.json`

### Orbit 147 (STABLE)

- Representative: `new_glider_146_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 2], [1, 2, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_146_W4_methodC.json`

### Orbit 148 (STABLE)

- Representative: `new_glider_17_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 2], [1, 2, 1, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_17_W4_methodA.json`

### Orbit 149 (STABLE)

- Representative: `new_glider_77_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 4], [0, 1, 1, 4]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_77_W4_methodA.json`

### Orbit 150 (STABLE)

- Representative: `new_glider_13_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 7], [0, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_13_W4_methodC.json`

### Orbit 151 (STABLE)

- Representative: `new_glider_34_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 1, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.00000000000001]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_34_W4_methodA.json`

### Orbit 152 (STABLE)

- Representative: `new_glider_163_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 1, 2], [2, 1, 2, 2]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_163_W4_methodC.json`

### Orbit 153 (STABLE)

- Representative: `new_glider_61_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 0, 1, 7], [2, 1, 2, 7]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_61_W4_methodA.json`

### Orbit 154 (STABLE)

- Representative: `new_glider_122_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 0, 1, 10], [1, 0, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_122_W4_methodA.json`

### Orbit 155 (STABLE)

- Representative: `new_glider_157_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 0], [2, 1, 2, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_157_W4_methodC.json`

### Orbit 156 (STABLE)

- Representative: `new_glider_18_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 10], [1, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `new_glider_18_W4_methodC.json`

### Orbit 157 (STABLE)

- Representative: `new_glider_94_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 3], [2, 2, 0, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_94_W4_methodA.json`

### Orbit 158 (STABLE)

- Representative: `new_glider_45_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 6], [2, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_45_W4_methodA.json`

### Orbit 159 (STABLE)

- Representative: `new_glider_84_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 9], [2, 1, 1, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [0.0, -100.0, 100.0]
  - |displacement| over 200 steps: 141.421356
  - Coordinate velocity v = |disp|/200: 0.707107
  - Normalized speed v/c = v/sqrt(2): **0.500000**

#### Members in this orbit:
- `new_glider_84_W4_methodA.json`

### Orbit 160 (STABLE)

- Representative: `new_glider_46_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 1, 0], [1, 1, 1, 2], [2, 1, 2, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_46_W4_methodA.json`

### Orbit 161 (STABLE)

- Representative: `new_glider_54_W4_methodA.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 1, 0], [1, 1, 1, 6], [2, 1, 2, 6]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 4 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_54_W4_methodA.json`

### Orbit 162 (STABLE)

- Representative: `new_glider_162_W4_methodC.json`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **False**
- Canonical particle: `[[0, 0, 0, 0], [1, 1, 1, 11], [1, 2, 0, 11], [2, 1, 2, 11]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [-200.0, -200.0, -100.0]
  - |displacement| over 200 steps: 300.000000
  - Coordinate velocity v = |disp|/200: 1.500000
  - Normalized speed v/c = v/sqrt(2): **1.060660**

#### Members in this orbit:
- `new_glider_162_W4_methodC.json`

### Orbit 163 (STABLE)

- Representative: `reference (iter_224 glider_00_lut08_sub03)`
- Number of stable members in orbit: **1**
- Equivalent to LUT-08 reference: **True**
- Canonical particle: `[[0, 0, 0, 0], [2, 0, 3, 0], [2, 2, 2, 7], [4, 1, 5, 0]]`
- Representative's properties:
  - Bit conserving: True
  - Max extent over 200 steps: 3 (<=6: True)
  - Exact shape period P: **2**
  - Cumulative displacement: [100.0, 0.0, 200.0]
  - |displacement| over 200 steps: 223.606798
  - Coordinate velocity v = |disp|/200: 1.118034
  - Normalized speed v/c = v/sqrt(2): **0.790569**

#### Members in this orbit:
- `reference (iter_224 glider_00_lut08_sub03)` (Reference Glider)
