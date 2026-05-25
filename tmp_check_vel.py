import json, numpy as np
from src.engine_3d import stream, collide
from src.rigorous_glider_audit import seed_grid, compute_com_circular
from src.glider_charge_analysis import make_BT

with open('archive/iter_224/results/glider_00_lut08_sub03.json') as f:
    d = json.load(f)
lut = np.array(d['lut'], dtype=np.uint16)
particle = [tuple(c) for c in d['particle']]

L = 64
grid = seed_grid(L, particle, center=(32, 32, 32))
coms = [compute_com_circular(grid)[0]]
for step in range(1, 81):
    grid = stream(grid)
    grid = collide(grid, lut)
    coms.append(compute_com_circular(grid)[0])

cumdisp = np.zeros(3)
for i in range(1, len(coms)):
    d = coms[i] - coms[i-1]
    for axis in range(3):
        if d[axis] > L/2: d[axis] -= L
        elif d[axis] < -L/2: d[axis] += L
    cumdisp += d

v_grid = cumdisp / 80
print('v_grid =', v_grid.tolist())

BT, BT_inv = make_BT()
v_cart = v_grid @ BT_inv
print('v_cart =', v_cart.tolist())
