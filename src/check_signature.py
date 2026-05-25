#!/usr/bin/env python3
import numpy as np
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

for oid in [6, 8]:
    orbit = orbit_list[oid]
    rep = orbit[0]
    w = hamming(rep)
    sz = len(orbit)
    stab_set = frozenset(stabs[x] for x in orbit)
    print(f"Orbit {oid}: weight={w}, size={sz}, stab_set_size={len(stab_set)}")
    print(f"  stab_set = {sorted(stab_set)}")
