#!/usr/bin/env python3
"""Verify sparse sim matches full grid sim for LUT-08 reference."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import stream, collide, pack, unpack, SHIFTS
from src.search_3d_gliders import generate_symmetric_lut, get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers

with open(ROOT/"archive/iter_224/results/glider_00_lut08_sub03.json") as f:
    ref = json.load(f)
lut = np.array(ref["lut"], dtype=np.uint16)
particle = [tuple(c) for c in ref["particle"]]

L = 32
steps = 16

# Full grid approach
def seed_grid(L, particle):
    grid = np.zeros((L, L, L, 12), dtype=np.uint8)
    c = L // 2
    for (dl, dr, dc, ch) in particle:
        grid[(c + dl) % L, (c + dr) % L, (c + dc) % L, ch] = 1
    return grid

def compute_com_circular(grid):
    L = grid.shape[0]
    total = int(grid.sum())
    if total == 0:
        return None
    coords = np.zeros(3)
    pos = np.arange(L)
    theta = 2 * np.pi * pos / L
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    for axis in range(3):
        if axis == 0:
            w = grid.sum(axis=(1, 2, 3)).astype(np.float64)
        elif axis == 1:
            w = grid.sum(axis=(0, 2, 3)).astype(np.float64)
        else:
            w = grid.sum(axis=(0, 1, 3)).astype(np.float64)
        x = (w * cos_t).sum()
        y = (w * sin_t).sum()
        coords[axis] = (L * np.arctan2(y, x) / (2 * np.pi)) % L
    return coords

def full_sim(particle, steps):
    grid = seed_grid(L, particle)
    coms = [compute_com_circular(grid)]
    for _ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
        coms.append(compute_com_circular(grid))
    cumdisp = np.zeros(3)
    for i in range(1, len(coms)):
        d = coms[i] - coms[i-1]
        for a in range(3):
            if d[a] > L/2: d[a] -= L
            elif d[a] < -L/2: d[a] += L
        cumdisp += d
    return cumdisp

# Sparse approach
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

def sparse_sim(particle, steps):
    c = L // 2
    bits = [(c + dl, c + dr, c + dc, ch) for (dl, dr, dc, ch) in particle]
    coms = [com_bits(bits)]
    for _ in range(steps):
        bits = stream_bits(bits)
        bits = collide_bits(bits)
        coms.append(com_bits(bits))
    cumdisp = np.zeros(3)
    for i in range(1, len(coms)):
        d = coms[i] - coms[i-1]
        for a in range(3):
            if d[a] > L/2: d[a] -= L
            elif d[a] < -L/2: d[a] += L
        cumdisp += d
    return cumdisp

for n in [4, 16, 100, 200]:
    f = full_sim(particle, n)
    s = sparse_sim(particle, n)
    print(f"steps={n:3d}: full={f}, sparse={s}, match={np.allclose(f,s)}")
