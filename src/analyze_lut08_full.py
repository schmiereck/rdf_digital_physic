#!/usr/bin/env python3
"""Full analysis of LUT-08 orbit structure and orbit-to-orbit mapping."""
import json, numpy as np
from pathlib import Path
import sys
from collections import defaultdict

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

print("=" * 80)
print("ORBIT SIGNATURES")
print("=" * 80)

# Group orbits by signature
sig_groups = defaultdict(list)
for oid, orbit in enumerate(orbit_list):
    rep = orbit[0]
    w = hamming(rep)
    sz = len(orbit)
    stab_set = frozenset(stabs[x] for x in orbit)
    sig = (w, sz, stab_set)
    sig_groups[sig].append(oid)

for sig, oids in sorted(sig_groups.items(), key=lambda x: x[0][0]):
    w, sz, _ = sig
    print(f"Weight={w}, size={sz}: orbits {oids}")

print("\n" + "=" * 80)
print("WEIGHT-2 ORBIT MAPPING")
print("=" * 80)

w1_cycles = [[0,3],[1,2],[4,7],[5,6],[8,11],[9,10]]
cycle_names = {tuple(c): f"C{i}" for i, c in enumerate(w1_cycles)}

def get_cycle(ch):
    for cyc in w1_cycles:
        if ch in cyc:
            return tuple(cyc)
    return None

def describe_state(s):
    chs = [ch for ch in range(12) if s & (1 << ch)]
    cycles = [get_cycle(ch) for ch in chs]
    return chs, cycles

# For each weight-2 orbit, find where it maps
w2_oids = [i for i, o in enumerate(orbit_list) if hamming(o[0]) == 2]

for src_oid in w2_oids:
    src_orbit = orbit_list[src_oid]
    rep = src_orbit[0]
    dst = lut08[rep]
    dst_oid = orbit_of[dst]
    dst_orbit = orbit_list[dst_oid]
    
    src_chs, src_cycs = describe_state(rep)
    dst_chs, dst_cycs = describe_state(dst)
    
    # Check if mapping is uniform across the orbit
    all_dst_oids = set()
    for s in src_orbit:
        d = lut08[s]
        all_dst_oids.add(int(orbit_of[d]))
    
    print(f"Src orbit {src_oid:2d} (size {len(src_orbit):2d}) -> Dst orbit {dst_oid:2d} (size {len(dst_orbit):2d})")
    print(f"  Rep {rep:4d}: ch_in={src_chs} cycles={src_cycs}")
    print(f"  Out {dst:4d}: ch_out={dst_chs} cycles={dst_cycs}")
    print(f"  Uniform mapping: {len(all_dst_oids) == 1} (all dst orbits: {sorted(all_dst_oids)})")
    print()

print("=" * 80)
print("VERIFY ADDITIVITY")
print("=" * 80)

# For each weight-2 state, check if lut[a|b] == lut[a]|lut[b]
from itertools import combinations
additive_count = 0
non_additive = []
for a, b in combinations(range(12), 2):
    s = (1 << a) | (1 << b)
    expected = lut08[1 << a] | lut08[1 << b]
    actual = lut08[s]
    if actual == expected:
        additive_count += 1
    else:
        non_additive.append((a, b, s, expected, actual))

print(f"Additive: {additive_count}/66")
print(f"Non-additive: {len(non_additive)}")
for a, b, s, exp, act in non_additive:
    print(f"  ch({a},{b}) state={s}: expected={exp} ({describe_state(exp)[0]}), actual={act} ({describe_state(act)[0]})")
