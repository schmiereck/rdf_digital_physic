#!/usr/bin/env python3
"""Check single-bit velocities for LUT-08 reference."""
import json, numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.engine_3d import stream, collide
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent

with open('archive/iter_224/results/glider_00_lut08_sub03.json') as f:
    ref = json.load(f)
lut = np.array(ref["lut"], dtype=np.uint16)
particle = [tuple(c) for c in ref["particle"]]
print("Full particle:", particle)

L = 32
steps = 32

# Full particle velocity
grid = seed_grid(L, particle)
coms = [compute_com_circular(grid)[0]]
for _ in range(steps):
    grid = stream(grid)
    grid = collide(grid, lut)
    coms.append(compute_com_circular(grid)[0])
cd = np.zeros(3)
for i in range(1, len(coms)):
    d = coms[i] - coms[i-1]
    for a in range(3):
        if d[a] > L/2: d[a] -= L
        elif d[a] < -L/2: d[a] += L
    cd += d
full_vel = cd / steps
print(f"Full velocity: {full_vel}")

# Each bit individually
for idx, bit in enumerate(particle):
    grid = seed_grid(L, [bit])
    coms = [compute_com_circular(grid)[0]]
    for _ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
        coms.append(compute_com_circular(grid)[0])
    cd = np.zeros(3)
    for i in range(1, len(coms)):
        d = coms[i] - coms[i-1]
        for a in range(3):
            if d[a] > L/2: d[a] -= L
            elif d[a] < -L/2: d[a] += L
        cd += d
    vel = cd / steps
    print(f"Bit {idx} {bit}: vel={vel}, match={np.allclose(vel, full_vel, atol=0.01)}")
