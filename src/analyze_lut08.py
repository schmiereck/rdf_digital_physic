#!/usr/bin/env python3
"""Analyze LUT-08 weight-2 orbit structure."""
import json, numpy as np
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.search_3d_gliders import (
    get_oh_permutations, precompute_perm_action, compute_orbits,
    compute_all_stabilizers, hamming
)

# Load LUT-08
with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
    ref = json.load(f)
lut08 = np.array(ref["lut"], dtype=np.uint16)

perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbit_list, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

print("Total orbits:", len(orbit_list))

# Find all weight-2 orbits
w2_orbits = [(i, o) for i, o in enumerate(orbit_list) if hamming(o[0]) == 2]
print(f"Weight-2 orbits: {len(w2_orbits)}")

# Weight-1 cycles from fundamental spectrum
w1_cycles = [[0,3],[1,2],[4,7],[5,6],[8,11],[9,10]]

def get_cycle(ch):
    for cyc in w1_cycles:
        if ch in cyc:
            return tuple(cyc)
    return None

for oid, orbit in w2_orbits:
    rep = orbit[0]
    channels_in = [ch for ch in range(12) if rep & (1 << ch)]
    out = lut08[rep]
    channels_out = [ch for ch in range(12) if out & (1 << ch)]
    in_cycles = [get_cycle(ch) for ch in channels_in]
    out_cycles = [get_cycle(ch) for ch in channels_out]
    print(f"Orbit {oid:2d}, size={len(orbit):2d}, rep={rep:4d} ch_in={channels_in}, out={out:4d} ch_out={channels_out}, in_cycles={in_cycles}, out_cycles={out_cycles}")
