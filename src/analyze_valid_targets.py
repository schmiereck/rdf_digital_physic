#!/usr/bin/env python3
"""Analyze valid targets for orbit mappings in LUT-08."""
import json, numpy as np
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.search_3d_gliders import (
    get_oh_permutations, precompute_perm_action, compute_orbits,
    compute_all_stabilizers, hamming
)

with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
    ref = json.load(f)
lut08 = np.array(ref["lut"], dtype=np.uint16)

perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbit_list, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

w2_oids = [i for i, o in enumerate(orbit_list) if hamming(o[0]) == 2]

print("Valid targets analysis for weight-2 orbits:")
for oid in w2_oids:
    orbit = orbit_list[oid]
    rep = orbit[0]
    H = stabs[rep]
    valid = [t for t in orbit if stabs[t] == H]
    print(f"Orbit {oid} (size {len(orbit)}): rep={rep}, stabilizer size={len(H)}, valid targets={len(valid)}")
    print(f"  Valid targets: {valid}")
    # Show what LUT-08 maps rep to
    actual = lut08[rep]
    print(f"  LUT-08 maps rep -> {actual} (in orbit {orbit_of[actual]})")
    print()
