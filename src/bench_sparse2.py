#!/usr/bin/env python3
"""Benchmark full sparse quick_sim."""
import sys, time
from pathlib import Path
import numpy as np
from collections import defaultdict
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import SHIFTS
from src.search_3d_gliders import generate_symmetric_lut, get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers

perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbits, _ = compute_orbits(action)
stabs = compute_all_stabilizers(action)
lut = generate_symmetric_lut(seed=42, perms=perms, action=action, orbits=orbits, stabs=stabs)

L = 32

def stream_bits(bits):
    return [((l + SHIFTS[ch][0]) % L, (r + SHIFTS[ch][1]) % L, (c + SHIFTS[ch][2]) % L, ch) for (l, r, c, ch) in bits]

def collide_bits(bits):
    cell_map = {}
    for (l, r, c, ch) in bits:
        cell_map[(l, r, c)] = cell_map.get((l, r, c), 0) | (1 << ch)
    new_bits = []
    for (l, r, c), packed in cell_map.items():
        new_packed = lut[packed]
        for ch in range(12):
            if (new_packed >> ch) & 1:
                new_bits.append((l, r, c, ch))
    return new_bits

def com_bits(bits):
    if not bits:
        return None
    coords = np.array([[b[0], b[1], b[2]] for b in bits], dtype=float)
    result = np.zeros(3)
    theta = 2 * np.pi * coords / L
    for a in range(3):
        x = np.cos(theta[:, a]).sum()
        y = np.sin(theta[:, a]).sum()
        result[a] = (L * np.arctan2(y, x) / (2 * np.pi)) % L
    return result

def extent_bits(bits):
    if not bits:
        return (0, 0, 0)
    coords = np.array([[b[0], b[1], b[2]] for b in bits])
    ext = []
    for a in range(3):
        pos = coords[:, a]
        best = L
        for s in np.unique(pos):
            shifted = (pos - s) % L
            w = int(shifted.max() - shifted.min() + 1)
            if w < best:
                best = w
        ext.append(best)
    return tuple(ext)

def quick_sim(particle, steps=16):
    c = L // 2
    bits = [(c + dl, c + dr, c + dc, ch) for (dl, dr, dc, ch) in particle]
    b0 = len(bits)
    com_prev = com_bits(bits)
    cd = np.zeros(3)
    for _ in range(steps):
        bits = stream_bits(bits)
        bits = collide_bits(bits)
        if len(bits) != b0:
            return None
        if max(extent_bits(bits)) > 6:
            return None
        com = com_bits(bits)
        if com is not None and com_prev is not None:
            d = com - com_prev
            d = (d + L // 2) % L - L // 2
            cd += d
        com_prev = com
    return cd

# Benchmark
n = 1000
particle = [(0,0,0,i) for i in range(4)]
t0 = time.time()
for _ in range(n):
    cd = quick_sim(particle, 16)
t1 = time.time()
print(f"{n} runs: {t1-t0:.3f}s, per run: {(t1-t0)/n*1000:.2f} ms")

# Test with actual LUT-08
import json
with open(ROOT/"archive/iter_224/results/glider_00_lut08_sub03.json") as f:
    ref = json.load(f)
lut08 = np.array(ref["lut"], dtype=np.uint16)
ref_particle = [tuple(c) for c in ref["particle"]]

# Replace lut with lut08 for this test
def collide_bits08(bits):
    cell_map = {}
    for (l, r, c, ch) in bits:
        cell_map[(l, r, c)] = cell_map.get((l, r, c), 0) | (1 << ch)
    new_bits = []
    for (l, r, c), packed in cell_map.items():
        new_packed = lut08[packed]
        for ch in range(12):
            if (new_packed >> ch) & 1:
                new_bits.append((l, r, c, ch))
    return new_bits

# Run 200 steps with sparse approach
c = L // 2
bits = [(c + dl, c + dr, c + dc, ch) for (dl, dr, dc, ch) in ref_particle]
b0 = len(bits)
com_prev = com_bits(bits)
cd = np.zeros(3)
for step in range(200):
    bits = stream_bits(bits)
    # temporarily replace collide function
    cell_map = {}
    for (l, r, c, ch) in bits:
        cell_map[(l, r, c)] = cell_map.get((l, r, c), 0) | (1 << ch)
    new_bits = []
    for (l, r, c), packed in cell_map.items():
        new_packed = lut08[packed]
        for ch in range(12):
            if (new_packed >> ch) & 1:
                new_bits.append((l, r, c, ch))
    bits = new_bits
    if len(bits) != b0:
        print(f"Bit loss at step {step}")
        break
    com = com_bits(bits)
    if com is not None and com_prev is not None:
        d = com - com_prev
        d = (d + L // 2) % L - L // 2
        cd += d
    com_prev = com
else:
    print(f"Sparse 200-step cumdisp: {cd}")
    print(f"Reference 200-step cumdisp: {ref['cumulative_displacement']}")
    print(f"Match: {np.allclose(cd, ref['cumulative_displacement'])}")
