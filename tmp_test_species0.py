import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.engine_3d import stream, collide
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent

# Test species 0 from iter_248
with open('archive/iter_248/results/search_results.json') as f:
    data = json.load(f)
sp = data['novel_species'][0]
particle = [tuple(c) for c in sp['canon']]
print('Species 0 particle:', particle)
print('LUT:', sp['lut'])

# Need to load/generate the right LUT
from src.search_3d_gliders import generate_symmetric_lut, get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers
perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbitdata = compute_orbits(action)
orbs = orbitdata[0]
stabs = compute_all_stabilizers(action)
lut = generate_symmetric_lut(seed=42, perms=perms, action=action, orbits=orbs, stabs=stabs)

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
print(f"Full velocity: {full_vel}, norm={np.linalg.norm(full_vel)}")

# Single-bit
for idx, bit in enumerate(particle):
    grid = seed_grid(L, [bit])
    for _ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
    # Get displacement
    grid_final = grid
    bits = np.argwhere(grid_final > 0)
    if len(bits) == 0:
        print(f'Bit {idx} died!')
        continue
    print(f"Bit {idx} {bit} at final: cell=({bits[0][0]},{bits[0][1]},{bits[0][2]}) ch={bits[0][3]}")
    
    # Compute full trajectory velocity
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
    print(f"  vel={vel}")
