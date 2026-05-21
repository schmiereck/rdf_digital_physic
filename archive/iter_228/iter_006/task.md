Write the following code exactly to `src/engine_d4_spacetime_18.py`:

```python
#!/usr/bin/env python3
\"\"\"engine_d4_spacetime_18.py — 3D+1 Spacetime LGCA on the D4 Lattice (18 channels).

Every cell carries 18 boolean channels:
  - 6 future-directed light-like D4 vectors (T = 1, projected to 3D octahedron of radius 1)
  - 12 spatial vectors (dT = 0, projected to 3D cuboctahedron of radius sqrt(2))

Equivariant under the full 48-element octahedral symmetry group O_h.
\"\"\"

import numpy as np
import math
import itertools
from typing import Dict, FrozenSet, List, Tuple

# 1. 18 Channels definition
D4_VECTORS_4D = np.array([
    # 6 Temporal channels (T = (x+y+z+w)/2 = 1, x^2+y^2+z^2+w^2 = 2)
    [1, 1, 0, 0],  # T0
    [0, 0, 1, 1],  # T1
    [1, 0, 1, 0],  # T2
    [0, 1, 0, 1],  # T3
    [1, 0, 0, 1],  # T4
    [0, 1, 1, 0],  # T5
    # 12 Spatial channels (dT = 0, x^2+y^2+z^2+w^2 = 2): 12 permutations of [1, -1, 0, 0]
    [1, -1, 0, 0],  # S0
    [-1, 1, 0, 0],  # S1
    [0, 0, 1, -1],  # S2
    [0, 0, -1, 1],  # S3
    [1, 0, 0, -1],  # S4
    [-1, 0, 0, 1],  # S5
    [1, 0, -1, 0],  # S6
    [-1, 0, 1, 0],  # S7
    [0, 1, 0, -1],  # S8
    [0, -1, 0, 1],  # S9
    [0, 1, -1, 0],  # S10
    [0, -1, 1, 0]   # S11
], dtype=np.int64)

NUM_CHANNELS = 18
NUM_STATES = 1 << NUM_CHANNELS  # 262,144

# Spatial grid shifts in 3D: temporal channels shift by first 3 components, spatial do not shift
SHIFTS = [
    (1, 1, 0),  # T0
    (0, 0, 1),  # T1
    (1, 0, 1),  # T2
    (0, 1, 0),  # T3
    (1, 0, 0),  # T4
    (0, 1, 1)   # T5
] + [(0, 0, 0)] * 12

def project_to_3d(v4d: np.ndarray) -> np.ndarray:
    \"\"\"Project 4D vector to the 3D spatial coordinate space perpendicular to [1,1,1,1].\"\"\"
    x, y, z, w = v4d
    # Pure integer projection as x, y, z, w are even/balanced
    return np.array([
        (x - y + z - w) // 2,
        (x - y - z + w) // 2,
        (x + y - z - w) // 2
    ], dtype=np.int64)

PROJECTED_VECTORS = np.array([project_to_3d(v) for v in D4_VECTORS_4D], dtype=np.int64)

def _signed_permutation_matrices() -> List[np.ndarray]:
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            M = np.zeros((3, 3), dtype=np.int64)
            for col, row in enumerate(perm):
                M[row, col] = signs[col]
            mats.append(M)
    return mats

def _channel_perm_from_matrix(M: np.ndarray) -> Tuple[int, ...]:
    transformed = PROJECTED_VECTORS @ M.T
    induced = []
    for tv in transformed:
        found = False
        for idx, pv in enumerate(PROJECTED_VECTORS):
            if np.array_equal(pv, tv):
                induced.append(idx)
                found = True
                break
        if not found:
            raise ValueError(f"Vector {tv} not preserved under matrix.")
    # Ensure it's a valid permutation of 0..17
    induced = induced[:18]
    assert len(set(induced)) == 18, f"Induced permutation is invalid: {induced}"
    return tuple(induced)

def _build_oh_group() -> List[Tuple[int, ...]]:
    perms = []
    for M in _signed_permutation_matrices():
        perms.append(_channel_perm_from_matrix(M))
    assert len(set(perms)) == 48, "O_h must induce 48 unique permutations on 18 channels."
    return perms

OH_GROUP = _build_oh_group()

# Precompute bit-wise permutations for ultra-fast lookups
# bit_perms[g_idx][b] contains the bitmask in the target state contributed by bit b of source state
bit_perms = []
for g in OH_GROUP:
    perms_for_g = [0] * 18
    for b in range(18):
        for i in range(18):
            if g[i] == b:
                perms_for_g[b] |= (1 << i)
    bit_perms.append(perms_for_g)

def apply_channel_perm(g_idx: int, state: int) -> int:
    \"\"\"Apply the g_idx-th channel permutation to state.\"\"\"
    res = 0
    p = bit_perms[g_idx]
    for b in range(18):
        if (state >> b) & 1:
            res |= p[b]
    return res

def compute_orbits() -> List[List[int]]:
    \"\"\"Partition {0,...,2^18-1} into orbits under OH_GROUP.\"\"\"
    seen = np.zeros(NUM_STATES, dtype=bool)
    orbits = []
    for s in range(NUM_STATES):
        if seen[s]:
            continue
        # Apply all 48 permutations to state s
        orb = {apply_channel_perm(g_idx, s) for g_idx in range(48)}
        for x in orb:
            seen[x] = True
        orbits.append(sorted(orb))
    return orbits

def compute_stabilizer(state: int) -> FrozenSet[int]:
    \"\"\"Indices of OH_GROUP elements that fix state.\"\"\"
    return frozenset(g_idx for g_idx in range(48) if apply_channel_perm(g_idx, state) == state)

def compute_momentum(state: int) -> Tuple[int, int, int]:
    \"\"\"Total integer 3D spatial momentum of a state.\"\"\"
    px, py, pz = 0, 0, 0
    for b in range(18):
        if (state >> b) & 1:
            pv = PROJECTED_VECTORS[b]
            px += pv[0]
            py += pv[1]
            pz += pv[2]
    return (px, py, pz)

def orbit_signature(orbit: List[int]) -> Tuple[int, int, FrozenSet[int], Tuple[int, int, int]]:
    \"\"\"(Hamming weight, orbit size, stabilizer subgroup, momentum of representative).\"\"\"
    rep = orbit[0]
    w = bin(rep).count("1")
    sz = len(orbit)
    stab = compute_stabilizer(rep)
    mom = compute_momentum(rep)
    return w, sz, stab, mom

def pack(grid: np.ndarray) -> np.ndarray:
    if grid.shape[-1] != NUM_CHANNELS:
        raise ValueError(f"grid must have shape (..., {NUM_CHANNELS})")
    out = np.zeros(grid.shape[:-1], dtype=np.int32)
    for i in range(NUM_CHANNELS):
        out |= (grid[..., i].astype(np.int32) & 1) << i
    return out

def unpack(packed: np.ndarray) -> np.ndarray:
    out = np.zeros(packed.shape + (NUM_CHANNELS,), dtype=np.uint8)
    for i in range(NUM_CHANNELS):
        out[..., i] = ((packed >> i) & 1).astype(np.uint8)
    return out

def stream(grid: np.ndarray, reverse: bool = False) -> np.ndarray:
    if grid.shape[-1] != NUM_CHANNELS:
        raise ValueError(f"grid must have shape (..., {NUM_CHANNELS})")
    out = np.empty_like(grid)
    sign = -1 if reverse else 1
    for i, (dx, dy, dz) in enumerate(SHIFTS):
        if dx == 0 and dy == 0 and dz == 0:
            out[..., i] = grid[..., i]
        else:
            out[..., i] = np.roll(grid[..., i], shift=(sign*dx, sign*dy, sign*dz), axis=(0,1,2))
    return out

def collide(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    return unpack(lut[pack(grid)])

def generate_symmetric_lut(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    orbits = compute_orbits()
    
    # Group orbits by signature
    sig_groups = {}
    for orb in orbits:
        sig = orbit_signature(orb)
        # sig is (weight, size, stabilizer, momentum)
        sig_groups.setdefault(sig, []).append(orb)
        
    lut = np.full(NUM_STATES, -1, dtype=np.int32)
    
    for sig, orbit_list in sig_groups.items():
        n = len(orbit_list)
        # Shuffle orbits within signature class to get non-trivial mixing
        order = list(rng.permutation(n))
        for src_idx, tgt_idx in enumerate(order):
            src_orbit = orbit_list[src_idx]
            tgt_orbit = orbit_list[tgt_idx]
            
            r = src_orbit[0]
            stab_r = sig[2]  # stabilizer of representative
            
            # Target candidates: representatives or members of tgt_orbit that are fixed by stab_r
            candidates = [
                t for t in tgt_orbit
                if all(apply_channel_perm(g_idx, t) == t for g_idx in stab_r)
            ]
            if not candidates:
                raise RuntimeError("No equivariant target.")
            
            t = int(rng.choice(candidates))
            for g_idx in range(48):
                lhs = apply_channel_perm(g_idx, r)
                rhs = apply_channel_perm(g_idx, t)
                if lut[lhs] != -1 and lut[lhs] != rhs:
                    raise RuntimeError("Equivariance conflict.")
                lut[lhs] = rhs
                
    if (lut == -1).any():
        raise RuntimeError("LUT incomplete.")
        
    return lut.astype(np.int32)

def verify_lut_properties(lut: np.ndarray) -> Tuple[bool, bool, bool, bool]:
    # 1. Bijection
    bij = len(set(lut.tolist())) == NUM_STATES
    # 2. Bit conservation
    bit_cons = True
    for s in range(NUM_STATES):
        if bin(s).count("1") != bin(int(lut[s])).count("1"):
            bit_cons = False
            break
    # 3. Momentum conservation
    mom_cons = True
    for s in range(NUM_STATES):
        if compute_momentum(s) != compute_momentum(int(lut[s])):
            mom_cons = False
            break
    # 4. Octahedral symmetry
    sym = True
    for g_idx in range(48):
        for s in range(1000): # Test 1000 random states for speed
            s_perm = apply_channel_perm(g_idx, s)
            lhs = lut[s_perm]
            rhs = apply_channel_perm(g_idx, int(lut[s]))
            if lhs != rhs:
                sym = False
                break
        if not sym:
            break
    return bij, bit_cons, sym, mom_cons

def main():
    print("=== D4 18-Channel Spacetime CA Engine self-test ===")
    print(f"Number of states: {NUM_STATES}")
    
    print("Constructing O_h point group on 18 channels...")
    print(f"O_h size: {len(OH_GROUP)}")
    
    print("Performing fast orbit decomposition of the 262,144 state space...")
    import time
    t0 = time.time()
    orbits = compute_orbits()
    t1 = time.time()
    print(f"Decomposition complete: {len(orbits)} orbits found in {t1-t0:.4f} seconds.")
    
    print("Generating randomized O_h-symmetric, bit-preserving, momentum-preserving LUT...")
    lut = generate_symmetric_lut(seed=42)
    print("LUT generation complete.")
    
    print("Verifying LUT physical constraints...")
    bij, bcons, sym, mcons = verify_lut_properties(lut)
    print(f"  Bijective: {bij}")
    print(f"  Bit-conserving (Energy/Mass): {bcons}")
    print(f"  Momentum-conserving: {mcons}")
    print(f"  O_h symmetry equivariant: {sym}")
    
    assert bij and bcons and sym and mcons, \"LUT verification failed!\"
    print("LUT physical verification PASSED.")
    
    # 3D Grid test
    L = 4
    grid = np.zeros((L, L, L, NUM_CHANNELS), dtype=np.uint8)
    # Set a few random bits to test conservation
    grid[1, 1, 1, 0] = 1 # temporal bit
    grid[1, 1, 1, 6] = 1 # spatial bit
    grid[2, 2, 2, 2] = 1 # temporal bit
    
    def get_total_bits_and_momentum(g):
        bits = int(g.sum())
        packed_g = pack(g)
        px, py, pz = 0, 0, 0
        for s in packed_g.flat:
            mx, my, mz = compute_momentum(int(s))
            px += mx
            py += my
            pz += mz
        return bits, (px, py, pz)
        
    init_bits, init_mom = get_total_bits_and_momentum(grid)
    print(f"Initial state: bits = {init_bits}, momentum = {init_mom}")
    
    curr = grid.copy()
    for step in range(1, 6):
        curr = collide(stream(curr), lut)
        step_bits, step_mom = get_total_bits_and_momentum(curr)
        print(f"  Step {step}: bits = {step_bits}, momentum = {step_mom}")
        assert step_bits == init_bits, f\"Bit mismatch at step {step}\"
        assert step_mom == init_mom, f\"Momentum mismatch at step {step}\"
        
    print("Multi-step conservation verification PASSED.")
    
    # Reversibility check
    inv_lut = np.zeros_like(lut)
    inv_lut[lut] = np.arange(NUM_STATES, dtype=np.int32)
    
    rev = curr.copy()
    for step in range(5):
        rev = stream(collide(rev, inv_lut), reverse=True)
    assert np.array_equal(rev, grid), \"Reversibility check failed!\"
    print("Perfect reversibility round-trip PASSED.")
    print("=== ALL TESTS PASSED! ===")

if __name__ == \"__main__\":
    main()
```

After writing the file, run it with `python src/engine_d4_spacetime_18.py` and print out the entire terminal output. Task success criterion: stdout ends with `=== ALL TESTS PASSED! ===`.