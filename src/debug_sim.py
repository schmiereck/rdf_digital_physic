#!/usr/bin/env python3
"""Debug simulation of iter_218 champion rule."""
import json
import numpy as np

with open(r'archive/iter_218/results/champion_rule.json') as f:
    rule_data = json.load(f)
rule_dict = rule_data['rule_dict']

lut = np.arange(128, dtype=np.uint8)
for k, v in rule_dict.items():
    lut[int(k)] = int(v)
lut = ((lut >> 6) & 1).astype(np.uint8)

GRID_SIZE = 128
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
for r, c in SEED_CELLS:
    grid[r, c] = 1

for t in range(200):
    e = np.roll(grid, -1, axis=0)
    w = np.roll(grid, 1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid, 1, axis=1)
    se = np.roll(e, 1, axis=1)
    nw = np.roll(w, -1, axis=1)
    state = ((grid.astype(np.uint16)<<6)|(e.astype(np.uint16)<<5)|(se.astype(np.uint16)<<4)|(sw.astype(np.uint16)<<3)|(w.astype(np.uint16)<<2)|(nw.astype(np.uint16)<<1)|ne.astype(np.uint16)).astype(np.uint8)
    grid = lut[state]

    if t % 50 == 0 or t == 199:
        rows, cols = np.where(grid > 0)
        positions = list(zip(rows.tolist(), cols.tolist()))
        com_r = float(np.mean(rows)) if len(rows) > 0 else 0
        com_c = float(np.mean(cols)) if len(cols) > 0 else 0
        out = f"Step {t:3d}: bits={int(grid.sum()):3d}, CoM=({com_r:.2f}, {com_c:.2f}), positions={positions}"
        with open("debug_output.txt", "a") as f:
            f.write(out + "\n")
        print(out)
