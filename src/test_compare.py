#!/usr/bin/env python3
import numpy as np
import json

with open('archive/iter_218/results/champion_rule.json') as f:
    rd = json.load(f)

lut = np.arange(128, dtype=np.uint8)
for k, v in rd['rule_dict'].items():
    lut[int(k)] = int(v)
lut = ((lut >> 6) & 1).astype(np.uint8)

def step(g):
    e = np.roll(g, -1, axis=0)
    w = np.roll(g, 1, axis=0)
    ne = np.roll(g, -1, axis=1)
    sw = np.roll(g, 1, axis=1)
    se = np.roll(e, 1, axis=1)
    nw = np.roll(w, -1, axis=1)
    s = ((g.astype(np.uint16) << 6) | (e.astype(np.uint16) << 5) |
         (se.astype(np.uint16) << 4) | (sw.astype(np.uint16) << 3) |
         (w.astype(np.uint16) << 2) | (nw.astype(np.uint16) << 1) |
         ne.astype(np.uint16)).astype(np.uint8)
    return lut[s]

# Try on 128x128 grid first
GS = 128
g = np.zeros((GS, GS), dtype=np.uint8)
# Seed as in evolution.py: (63,63),(64,63),(64,64)
g[63, 63] = 1
g[64, 63] = 1
g[64, 64] = 1

for t in range(1, 201):
    g = step(g)

r, c = np.where(g > 0)
cells = list(zip(r.tolist(), c.tolist()))
print(f'Grid 128x128: Active cells: {len(r)}')
for cell in cells:
    print(f'  {cell}')
com_r = np.mean(r); com_c = np.mean(c)
print(f'CoM: ({com_r:.4f}, {com_c:.4f})')
print()

# Now on 256x256 with the task-specified seed
GS = 256
g = np.zeros((GS, GS), dtype=np.uint8)
g[128, 128] = 1
g[129, 128] = 1
g[129, 129] = 1

for t in range(1, 301):
    g = step(g)

r, c = np.where(g > 0)
cells = list(zip(r.tolist(), c.tolist()))
print(f'Grid 256x256: Active cells: {len(r)}')
for cell in cells:
    print(f'  {cell}')
com_r = np.mean(r); com_c = np.mean(c)
print(f'CoM: ({com_r:.4f}, {com_c:.4f})')
