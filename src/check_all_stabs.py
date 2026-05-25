#!/usr/bin/env python3
import json, numpy as np
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.search_3d_gliders import (
    get_oh_permutations, precompute_perm_action, compute_orbits,
    compute_all_stabilizers, hamming
)

perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbit_list, orbit_of = compute_orbits(action)
stabs = compute_all_stabilizers(action)

# Get all stabilizers in orbit 6 and 8
stabs_6 = set(stabs[s] for s in orbit_list[6])
stabs_8 = set(stabs[s] for s in orbit_list[8])

print(f"Unique stabilizers in orbit 6: {len(stabs_6)}")
print(f"Unique stabilizers in orbit 8: {len(stabs_8)}")
print(f"Intersection: {len(stabs_6 & stabs_8)}")
print(f"Union: {len(stabs_6 | stabs_8)}")

print("\nStabilizers in orbit 6:")
for s in sorted(stabs_6):
    print(f"  {s}")

print("\nStabilizers in orbit 8:")
for s in sorted(stabs_8):
    print(f"  {s}")
