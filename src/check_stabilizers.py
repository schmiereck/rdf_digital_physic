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

# Check stabilizers of orbit 6 and 8
for oid in [6, 8]:
    orbit = orbit_list[oid]
    print(f"Orbit {oid} stabilizers:")
    for s in orbit[:10]:
        print(f"  state {s}: stab={stabs[s]}")
    print()

# Check if any state in orbit 8 has same stabilizer as rep=17
rep17_stab = stabs[17]
print(f"Stabilizer of 17: {rep17_stab}")
matches = [s for s in orbit_list[8] if stabs[s] == rep17_stab]
print(f"States in orbit 8 with same stabilizer as 17: {matches}")

rep20_stab = stabs[20]
print(f"Stabilizer of 20: {rep20_stab}")
matches = [s for s in orbit_list[6] if stabs[s] == rep20_stab]
print(f"States in orbit 6 with same stabilizer as 20: {matches}")
