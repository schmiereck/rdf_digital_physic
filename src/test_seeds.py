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

# Test seed orientation A: (0,0),(0,1),(1,1) - from JSON seed_particle
# Test seed orientation B: (0,0),(1,0),(1,1) - from task description
# Test seed orientation C: (63,63),(64,63),(64,64) - from evolution.py

print("=== Seed A: (0,0),(0,1),(1,1) on 128x128 ===")
g = np.zeros((128,128), dtype=np.uint8)
g[0,0]=1; g[0,1]=1; g[1,1]=1
for t in range(1, 201):
    g = step(g)
r, c = np.where(g > 0)
print(f"Bits: {len(r)}")
if len(r) > 0:
    print(f"Cells: {list(zip(r.tolist(), c.tolist()))}")

print()
print("=== Seed B: (0,0),(1,0),(1,1) on 128x128 ===")
g = np.zeros((128,128), dtype=np.uint8)
g[0,0]=1; g[1,0]=1; g[1,1]=1
for t in range(1, 201):
    g = step(g)
r, c = np.where(g > 0)
print(f"Bits: {len(r)}")
if len(r) > 0:
    print(f"Cells: {list(zip(r.tolist(), c.tolist()))}")

print()
print("=== Seed C: (63,63),(64,63),(64,64) on 128x128 ===")
g = np.zeros((128,128), dtype=np.uint8)
g[63,63]=1; g[64,63]=1; g[64,64]=1
for t in range(1, 201):
    g = step(g)
r, c = np.where(g > 0)
print(f"Bits: {len(r)}")
if len(r) > 0:
    print(f"Cells: {list(zip(r.tolist(), c.tolist()))}")

print()
print("=== Seed D: (127,127),(128,127),(128,128) on 256x256 ===")
g = np.zeros((256,256), dtype=np.uint8)
g[127,127]=1; g[128,127]=1; g[128,128]=1
for t in range(1, 301):
    g = step(g)
r, c = np.where(g > 0)
print(f"Bits: {len(r)}")
if len(r) > 0:
    print(f"Cells: {list(zip(r.tolist(), c.tolist()))}")
