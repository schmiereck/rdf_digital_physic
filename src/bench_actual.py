#!/usr/bin/env python3
"""Benchmark actual quick_sim from experiment script."""
import sys, time
from pathlib import Path
import numpy as np
from itertools import combinations
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

# Benchmark Phase A style
particles_a = []
for k in range(3, 13):
    for subset in combinations(range(12), k):
        particles_a.append([(0, 0, 0, ch) for ch in subset])

n = len(particles_a)
t0 = time.time()
for p in particles_a:
    quick_sim(p, 16)
t1 = time.time()
print(f"Phase A style: {n} particles in {t1-t0:.2f}s ({(t1-t0)/n*1000:.3f} ms each)")

# Benchmark Phase C style
rng = np.random.default_rng(248)
particles_c = []
for _ in range(5000):
    nbits = int(rng.integers(3, 13))
    bits = set()
    while len(bits) < nbits:
        bits.add((int(rng.integers(-1, 2)), int(rng.integers(-1, 2)), int(rng.integers(-1, 2)), int(rng.integers(0, 12))))
    particles_c.append(list(bits))

t0 = time.time()
for p in particles_c:
    quick_sim(p, 16)
t1 = time.time()
print(f"Phase C style: {len(particles_c)} particles in {t1-t0:.2f}s ({(t1-t0)/len(particles_c)*1000:.3f} ms each)")
