#!/usr/bin/env python3
"""Quick test: compare wrong seed vs correct seed"""
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

GS = 256

# WRONG seed: [[0,0],[1,0],[1,1]] at center (128,128)
g_wrong = np.zeros((GS, GS), dtype=np.uint8)
for dr, dc in [[0,0],[1,0],[1,1]]:
    g_wrong[128+dr, 128+dc] = 1
for t in range(300):
    g_wrong = step(g_wrong)
print(f"WRONG seed [[0,0],[1,0],[1,1]] at (128,128): bits={int(g_wrong.sum())}")
r, c = np.where(g_wrong > 0)
print(f"  cells: {list(zip(r.tolist(), c.tolist()))}")

# CORRECT seed: [[0,0],[0,1],[1,1]] at center (128,128)
g_correct = np.zeros((GS, GS), dtype=np.uint8)
for dr, dc in [[0,0],[0,1],[1,1]]:
    g_correct[128+dr, 128+dc] = 1
for t in range(300):
    g_correct = step(g_correct)
print(f"CORRECT seed [[0,0],[0,1],[1,1]] at (128,128): bits={int(g_correct.sum())}")
r, c = np.where(g_correct > 0)
print(f"  cells: {list(zip(r.tolist(), c.tolist()))}")
