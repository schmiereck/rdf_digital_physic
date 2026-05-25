#!/usr/bin/env python3
import numpy as np
from pathlib import Path
import sys
from collections import defaultdict

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

orbit_sigs = []
for o in orbit_list:
    rep = o[0]
    w = hamming(rep)
    sz = len(o)
    stab_set = frozenset(stabs[x] for x in o)
    orbit_sigs.append((w, sz, stab_set))

groups = defaultdict(list)
for idx, sig in enumerate(orbit_sigs):
    groups[sig].append(idx)

for sig, oids in sorted(groups.items(), key=lambda x: x[0][0]):
    w, sz, stab_set = sig
    if w == 2:
        print(f"Weight={w}, size={sz}: orbits {oids}")
        print(f"  stab_set = {sorted(stab_set)}")
