#!/usr/bin/env python3
"""Debug test"""
import json, numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.engine_3d import stream, collide
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent

with open('archive/iter_224/results/glider_00_lut08_sub03.json') as f:
    ref = json.load(f)
lut = np.array(ref["lut"], dtype=np.uint16)
particle = [tuple(c) for c in ref["particle"]]
print("Reference particle:", particle)

L = 32
grid = seed_grid(L, particle)
print("Initial bits:", int(grid.sum()))
print("Initial extent:", bounding_extent(grid))

for step in range(5):
    bits = np.argwhere(grid > 0)
    cells = set((int(b[0]), int(b[1]), int(b[2])) for b in bits)
    print(f"step {step}: {len(bits)} bits, {len(cells)} cells, multi_cells={len(bits)-len(cells)}")
    com, _ = compute_com_circular(grid)
    print(f"  COM: {com}")
    grid = stream(grid)
    grid = collide(grid, lut)
