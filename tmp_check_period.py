import json, numpy as np
from src.rigorous_glider_audit import seed_grid, compute_com_circular, grid_cells, is_translate
from src.engine_3d import stream, collide

with open('archive/iter_224/results/glider_00_lut08_sub03.json') as f:
    d = json.load(f)
lut = np.array(d['lut'], np.uint16)
part = [tuple(c) for c in d['particle']]

L = 64
grid = seed_grid(L, part, center=(32,32,32))
shapes = [grid_cells(grid)]
for step in range(1, 33):
    grid = stream(grid)
    grid = collide(grid, lut)
    shapes.append(grid_cells(grid))

for p in range(1, 17):
    ok = True
    for j in range(p, 33 - p):
        if not is_translate(shapes[j], shapes[j-p], L):
            ok = False
            break
    if ok:
        print('Detected period:', p)
        break
else:
    print('No period detected')
