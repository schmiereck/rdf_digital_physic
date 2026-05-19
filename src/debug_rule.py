#!/usr/bin/env python3
"""Debug: check what the champion rule does with centered L-tromino."""
import json
import numpy as np

with open("archive/iter_218/results/champion_vc_rule.json") as f:
    rd = json.load(f)
rule_dict = rd["rule_dict"]

lut = np.arange(128, dtype=np.uint8)
for k, v in rule_dict.items():
    lut[int(k)] = int(v)
lut = ((lut >> 6) & 1).astype(np.uint8)
print(f"LUT non-zero: {int(lut.sum())} out of 128")

grid_size = 128
L_TROMINO = [(63, 63), (64, 63), (64, 64)]

grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
for r, c in L_TROMINO:
    grid[r, c] = 1

def step_grid(grid, lut):
    e = np.roll(grid, -1, axis=0)
    w = np.roll(grid, 1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid, 1, axis=1)
    se = np.roll(e, 1, axis=1)
    nw = np.roll(w, -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16) << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16) << 2)
        | (nw.astype(np.uint16) << 1)
        | ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]

def com(grid):
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))

print("=== Step-by-step with centered L-tromino ===")
for s in range(0, 101):
    bc = int(grid.sum())
    c = com(grid)
    print(f"Step {s:3d}: bits={bc}, CoM=({c[0]:8.2f}, {c[1]:8.2f})")
    if s < 20:
        for r in range(61, 67):
            row_str = "".join(str(grid[r, c]) for c in range(61, 67))
            print(f"  Row {r}: {row_str}")
    grid = step_grid(grid, lut)

# Now try the seed from the champion rule definition: [[0,0],[0,1],[1,1]]
# but placed at center
print("\n=== Step-by-step with L-tromino at center (seed_particle placement) ===")
grid2 = np.zeros((grid_size, grid_size), dtype=np.uint8)
# seed_particle = [[0,0],[0,1],[1,1]] — this is an offset shape
# In the champion run it was placed starting at some center position
# initial_com was (0.333, 0.667) which is very close to (0,0)
# So the seed was likely placed at grid center (63,63) as [(63,63),(63,64),(64,64)]
grid2[63, 63] = 1  # (0,0) offset -> center
grid2[63, 64] = 1  # (0,1) offset -> center+right
grid2[64, 64] = 1  # (1,1) offset -> center+down+right

for s in range(0, 101):
    bc = int(grid2.sum())
    c = com(grid2)
    print(f"Step {s:3d}: bits={bc}, CoM=({c[0]:8.2f}, {c[1]:8.2f})")
    if s < 20:
        for r in range(61, 67):
            row_str = "".join(str(grid2[r, c]) for c in range(61, 67))
            print(f"  Row {r}: {row_str}")
    grid2 = step_grid(grid2, lut)
