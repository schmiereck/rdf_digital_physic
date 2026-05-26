Implement and execute the O_h-symmetric non-additive LUT construction and exhaustive multi-bit glider search for the 3D FCC lattice.

### Key Implementation Guidelines

Use the following highly optimized, 100% mathematically correct unwrapped sparse simulation algorithm:
```python
def simulate_unwrapped(seed_channels, lut, L=32, steps=200):
    # Each bit is represented as [l, r, c, ch] where l, r, c are unwrapped float/int coordinates
    bits = [[16, 16, 16, ch] for ch in seed_channels]
    initial_len = len(bits)
    com_start = np.array([16.0, 16.0, 16.0])
    
    for t in range(steps):
        # 1. Stream step
        for b in bits:
            sh = SHIFTS[b[3]]
            b[0] += sh[0]
            b[1] += sh[1]
            b[2] += sh[2]
            
        # 2. Collide step
        cell_groups = {}
        for b in bits:
            gl = b[0] % L
            gr = b[1] % L
            gc = b[2] % L
            key = (gl, gr, gc)
            cell_groups.setdefault(key, []).append(b)
            
        new_bits = []
        for key, group in cell_groups.items():
            packed = 0
            for b in group:
                packed |= (1 << b[3])
            
            new_packed = lut[packed]
            
            # Use unwrapped position of the first bit in this cell
            ul, ur, uc = group[0][0], group[0][1], group[0][2]
            
            for ch in range(12):
                if (new_packed >> ch) & 1:
                    new_bits.append([ul, ur, uc, ch])
                    
        bits = new_bits
        if len(bits) != initial_len:
            return None # Not bit-conserving
            
        # Check localization (spread < 4.0)
        coords = np.array([[b[0], b[1], b[2]] for b in bits])
        com = coords.mean(axis=0)
        spread = np.max(np.abs(coords - com))
        if spread >= 4.0:
            return None # Not localized
            
    coords_end = np.array([[b[0], b[1], b[2]] for b in bits])
    com_end = coords_end.mean(axis=0)
    disp = com_end - com_start
    disp_norm = np.linalg.norm(disp)
    
    return {
        "displacement": disp.tolist(),
        "displacement_norm": float(disp_norm),
        "final_bits": bits
    }
```

### Steps:
1. Write `src/non_additive_lut_v2.py`:
   - Generate the 128 unique O_h-symmetric weight-2 sub-tables.
   - For each weight-2 configuration:
     - The weight-1 sub-table is fixed to the correct O_h-symmetric Cartesian transposition: `0<->3, 1<->2, 4<->7, 5<->6, 8<->11, 9<->10`.
     - Weight-2 is the specific configuration.
     - Weight-3+ is the additive extension of weight-1.
   - Also generate the fully ADDITIVE control LUT where weight-2+ is the additive extension of weight-1.
   - Verify all generated LUTs: bijection, bit conservation, O_h symmetry.

2. Write `src/experiment_250_nonadditive_search.py`:
   - Run the high-speed `simulate_unwrapped` for ALL 128 unique configurations across ALL 66 weight-2 single-cell seeds.
   - Run the same seeds under the ADDITIVE control LUT as a baseline check (expected: 0 moving gliders).
   - Generate 40 distinct LUTs with random/equivariant weight-3+ configurations, and run ALL 220 weight-3 single-cell seeds.
   - Log any candidates with `displacement_norm > 2.0`.
   - If candidates are found, perform the Three-Test Coherence Verification (Decomposition, Stability, and O_h Covariance).

3. Save the exhaustive results and write a highly rigorous scientific report to `archive/iter_250/results/nonadditive_search_report.md`. If no gliders are found, report it as a definitive null result (F2/F3 triggered). Keep language restrained, precise, and scientific. No hype.