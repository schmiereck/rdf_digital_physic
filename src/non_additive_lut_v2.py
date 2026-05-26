#!/usr/bin/env python3
"""
non_additive_lut_v2.py — O_h-symmetric non-additive LUT construction for 3D FCC lattice.

Constructs:
1. ADDITIVE control LUT: Cartesian transposition weight-1 sub-table,
   with additive extension for all other weights.
2. 128 unique O_h-symmetric weight-2 non-additive LUTs.
3. 40 distinct LUTs with random/equivariant weight-3+ configurations
   (fixed weight-1/weight-2, randomized weight >= 3).

All LUTs are verified for bijection, bit conservation, and O_h symmetry.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.search_3d_gliders import (
    get_oh_permutations,
    precompute_perm_action,
    compute_orbits,
    compute_all_stabilizers,
    hamming,
)

# ========================================================================
# Cartesian transposition weight-1 sub-table
# ========================================================================
CARTESIAN_PAIRS = [(0, 3), (1, 2), (4, 7), (5, 6), (8, 11), (9, 10)]

_CARTESIAN_LUT = [0] * 12
for a, b in CARTESIAN_PAIRS:
    _CARTESIAN_LUT[a] = b
    _CARTESIAN_LUT[b] = a

# ========================================================================
# Cached O_h infrastructure
# ========================================================================
_oh_cache: dict = {}


def _get_oh():
    if "perms" not in _oh_cache:
        perms = get_oh_permutations(verbose=False)
        action = precompute_perm_action(perms)
        orbits, orbit_of = compute_orbits(action)
        stabs = compute_all_stabilizers(action)
        _oh_cache["perms"] = perms
        _oh_cache["action"] = action
        _oh_cache["orbits"] = orbits
        _oh_cache["orbit_of"] = orbit_of
        _oh_cache["stabs"] = stabs
    return (
        _oh_cache["perms"],
        _oh_cache["action"],
        _oh_cache["orbits"],
        _oh_cache["orbit_of"],
        _oh_cache["stabs"],
    )


# ========================================================================
# Weight-2 orbit data
# ========================================================================
def _identify_w2_orbit_data():
    perms, action, orbits, orbit_of, stabs = _get_oh()
    w2_orbits = []
    for idx, o in enumerate(orbits):
        if hamming(o[0]) == 2:
            rep = o[0]
            H = stabs[rep]
            valid = [t for t in o if stabs[t] == H]
            w2_orbits.append({
                "global_idx": idx,
                "rep": rep,
                "orbit_members": sorted(o),
                "stab_size": len(H),
                "valid_targets": sorted(valid),
            })
    w2_orbits.sort(key=lambda d: d["rep"])
    for i, d in enumerate(w2_orbits):
        d["local_label"] = f"O_{i}"
    return w2_orbits


_W2_ORBIT_DATA = None


def get_w2_orbit_data():
    global _W2_ORBIT_DATA
    if _W2_ORBIT_DATA is None:
        _W2_ORBIT_DATA = _identify_w2_orbit_data()
    return _W2_ORBIT_DATA


# ========================================================================
# Build additive LUT (Cartesian transposition, additive extension)
# ========================================================================
def build_additive_lut() -> np.ndarray:
    lut = np.zeros(4096, dtype=np.uint16)
    w1_out = np.zeros(12, dtype=np.uint16)
    for ch in range(12):
        w1_out[ch] = 1 << _CARTESIAN_LUT[ch]
    for s in range(4096):
        out = 0
        for ch in range(12):
            if (s >> ch) & 1:
                out |= w1_out[ch]
        lut[s] = out
    return lut


# ========================================================================
# Build non-additive LUT with specific weight-2 configuration
# ========================================================================
def build_nonadditive_lut(config_index: int) -> np.ndarray:
    """
    Build an O_h-symmetric non-additive LUT.
    
    Weight-1: Cartesian transposition (fixed).
    Weight-2: determined by config_index (0..127).
    Weight-w (w>=3): additive extension of weight-1.
    """
    if not (0 <= config_index < 128):
        raise ValueError(f"config_index must be in [0, 127], got {config_index}")
    
    perms, action, orbits, orbit_of, stabs = _get_oh()
    n_perms = len(perms)
    
    # Start from additive LUT
    lut = build_additive_lut().astype(np.int32).copy()
    
    w2_data = get_w2_orbit_data()
    
    # Decode config_index into choices for each orbit
    # O_0: 4 choices, O_1: 2 choices, O_2: 4 choices, O_3: 4 choices
    choices = []
    remaining = config_index
    for d in w2_data:
        n = len(d["valid_targets"])
        choices.append(remaining % n)
        remaining //= n
    assert remaining == 0, "config_index out of range"
    
    # Apply equivariant mapping for each weight-2 orbit
    for d, choice_idx in zip(w2_data, choices):
        rep = d["rep"]
        target = d["valid_targets"][choice_idx]
        
        for g in range(n_perms):
            src = int(action[g, rep])
            dst = int(action[g, target])
            lut[src] = dst
    
    return lut.astype(np.uint16)


# ========================================================================
# Build LUT with randomized weight-3+ (fixed w0/w1/w2)
# ========================================================================
def build_randomized_w3plus_lut(w2_config_index: int, seed: int) -> np.ndarray:
    """
    Build LUT with:
    - Weight-0,1,2 fixed (weight-2 from w2_config_index).
    - Weight >= 3 randomized via O_h-equivariant orbit pairing.
    """
    rng = np.random.default_rng(seed)
    perms, action, orbits, orbit_of, stabs = _get_oh()
    n_perms = len(perms)
    
    # Start with non-additive LUT for weights 0-2
    lut = build_nonadditive_lut(w2_config_index).astype(np.int32).copy()
    
    # Identify which states are already mapped (weights 0,1,2)
    mapped = np.zeros(4096, dtype=bool)
    for s in range(4096):
        if hamming(s) <= 2:
            mapped[s] = True
    
    # Group remaining orbits by signature
    from collections import defaultdict
    groups = defaultdict(list)
    for idx, o in enumerate(orbits):
        rep = o[0]
        w = hamming(rep)
        if w <= 2:
            continue
        sz = len(o)
        stab_set = frozenset(stabs[x] for x in o)
        sig = (w, sz, stab_set)
        groups[sig].append(idx)
    
    # Pair orbits randomly within each group
    for sig, orbit_indices in groups.items():
        n = len(orbit_indices)
        if n == 0:
            continue
        shuffled = list(orbit_indices)
        if n > 1:
            order = rng.permutation(n)
            shuffled = [orbit_indices[i] for i in order]
        
        for src_idx, dst_idx in zip(orbit_indices, shuffled):
            src_orbit = orbits[src_idx]
            dst_orbit = orbits[dst_idx]
            rep_src = src_orbit[0]
            H_src = stabs[rep_src]
            
            valid_targets = [t for t in dst_orbit if stabs[t] == H_src]
            if len(valid_targets) == 0:
                raise RuntimeError(
                    f"No valid target for orbit {src_idx} -> {dst_idx}"
                )
            target = int(valid_targets[rng.integers(len(valid_targets))])
            
            for g in range(n_perms):
                src = int(action[g, rep_src])
                dst = int(action[g, target])
                if mapped[src]:
                    # Verify consistency (should match existing if already set)
                    if lut[src] != dst:
                        raise RuntimeError(
                            f"Inconsistent map at {src}: existing={lut[src]}, new={dst}"
                        )
                else:
                    lut[src] = dst
                    mapped[src] = True
    
    assert mapped.all(), "LUT incomplete"
    return lut.astype(np.uint16)


# ========================================================================
# Verification
# ========================================================================
def verify_lut(lut: np.ndarray) -> dict:
    """Verify bijection, bit conservation, and O_h symmetry."""
    perms, action, orbits, orbit_of, stabs = _get_oh()
    
    results = {}
    results['bijection'] = bool(len(np.unique(lut)) == 4096)
    
    pop_in = np.array([hamming(s) for s in range(4096)])
    pop_out = np.array([hamming(int(lut[s])) for s in range(4096)])
    results['bit_conserving'] = bool(np.array_equal(pop_in, pop_out))
    
    sym_ok = True
    bad = None
    for g in range(action.shape[0]):
        lhs = lut[action[g]]
        rhs = action[g, lut]
        if not np.array_equal(lhs, rhs):
            sym_ok = False
            bad = g
            break
    results['symmetric'] = sym_ok
    if bad is not None:
        results['first_violating_perm'] = int(bad)
    return results


def verify_all_luts():
    """Verify the additive LUT and a sample of non-additive/randomized LUTs."""
    print("Verifying additive LUT...")
    add_lut = build_additive_lut()
    v = verify_lut(add_lut)
    print(f"  Additive: {v}")
    assert v['bijection'] and v['bit_conserving'] and v['symmetric']
    
    print("Verifying all 128 non-additive LUTs...")
    for i in range(128):
        lut = build_nonadditive_lut(i)
        v = verify_lut(lut)
        if not (v['bijection'] and v['bit_conserving'] and v['symmetric']):
            print(f"  FAILED at config {i}: {v}")
            raise AssertionError(f"LUT {i} verification failed")
    print("  All 128 non-additive LUTs verified.")
    
    print("Verifying 40 randomized w3+ LUTs...")
    for i in range(40):
        lut = build_randomized_w3plus_lut(w2_config_index=i % 128, seed=i)
        v = verify_lut(lut)
        if not (v['bijection'] and v['bit_conserving'] and v['symmetric']):
            print(f"  FAILED at seed {i}: {v}")
            raise AssertionError(f"Randomized LUT {i} verification failed")
    print("  All 40 randomized LUTs verified.")
    
    return True


# ========================================================================
# Seed generation
# ========================================================================
def generate_weight2_seeds() -> list[list[int]]:
    """Generate all 66 weight-2 single-cell seeds (combinations of 2 channels)."""
    seeds = []
    for i in range(12):
        for j in range(i + 1, 12):
            seeds.append([i, j])
    return seeds


def generate_weight3_seeds() -> list[list[int]]:
    """Generate all 220 weight-3 single-cell seeds (combinations of 3 channels)."""
    seeds = []
    for i in range(12):
        for j in range(i + 1, 12):
            for k in range(j + 1, 12):
                seeds.append([i, j, k])
    return seeds


# ========================================================================
# Main
# ========================================================================
if __name__ == "__main__":
    verify_all_luts()
    print("\nAll verifications passed.")
    
    # Save metadata
    w2_data = get_w2_orbit_data()
    meta = {
        "cartesian_pairs": CARTESIAN_PAIRS,
        "num_w2_configs": 128,
        "w2_orbits": [
            {
                "label": d["local_label"],
                "rep": d["rep"],
                "size": len(d["orbit_members"]),
                "stab_size": d["stab_size"],
                "num_valid_targets": len(d["valid_targets"]),
            }
            for d in w2_data
        ],
    }
    out_dir = ROOT / "archive" / "iter_250" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "nonadditive_lut_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata saved to {out_dir / 'nonadditive_lut_metadata.json'}")
