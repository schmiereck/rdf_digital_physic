import json
import numpy as np
from src.engine_3d import stream, collide
from src.search_3d_gliders import compute_com_circular

# Load the glider data
with open('archive/iter_224/results/glider_02_lut21_sub01.json') as f:
    d = json.load(f)

particle = d['particle']
lut = np.array(d['lut'], dtype=np.uint16)

# Create 16x16x16 grid
L = 16
grid = np.zeros((L, L, L, 12), dtype=np.uint8)
cx, cy, cz = L//2, L//2, L//2
for (dl, dr, dc, ch) in particle:
    grid[(cx + dl)%L, (cy + dr)%L, (cz + dc)%L, ch] = 1

print('Initial state active bits:', grid.sum())
for step in range(11):
    com, bc = compute_com_circular(grid)
    print(f'Step {step:2d}: COM={com}, bits={bc}')
    grid = stream(grid)
    grid = collide(grid, lut)
