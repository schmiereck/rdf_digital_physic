#!/usr/bin/env python3
"""Debug simulation of iter_218 champion rule with correct seed."""
import json
import numpy as np

with open(r'archive/iter_218/results/champion_rule.json') as f:
    rule_data = json.load(f)
rule_dict = rule_data['rule_dict']
seed_particles = rule_data['seed_particle']
print(f"Seed particles from champion_rule.json: {seed_particles}")

lut = np.arange(128, dtype=np.uint8)
for k, v in rule_dict.items():
    lut[int(k)] = int(v)
lut = ((lut >> 6) & 1).astype(np.uint8)

# Test both grid sizes
for GRID_SIZE in [128, 256]:
    print(f"\n--- Grid size: {GRID_SIZE}x{GRID_SIZE} ---")
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_particles:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1

    positions_history = []
    for t in range(300):
        e = np.roll(grid, -1, axis=0)
        w = np.roll(grid, 1, axis=0)
        ne = np.roll(grid, -1, axis=1)
        sw = np.roll(grid, 1, axis=1)
        se = np.roll(e, 1, axis=1)
        nw = np.roll(w, -1, axis=1)
        state = ((grid.astype(np.uint16)<<6)|(e.astype(np.uint16)<<5)|(se.astype(np.uint16)<<4)|(sw.astype(np.uint16)<<3)|(w.astype(np.uint16)<<2)|(nw.astype(np.uint16)<<1)|ne.astype(np.uint16)).astype(np.uint8)
        grid = lut[state]

        rows, cols = np.where(grid > 0)
        positions = sorted(zip(rows.tolist(), cols.tolist()))
        positions_history.append(positions)
        
        com_r = float(np.mean(rows)) if len(rows) > 0 else 0
        com_c = float(np.mean(cols)) if len(cols) > 0 else 0
        
        if t < 10 or t % 50 == 0 or t == 299:
            out = f"Step {t:4d}: bits={int(grid.sum()):3d}, CoM=({com_r:.2f}, {com_c:.2f}), positions={positions}"
            print(out)
    
    # Check if periodic at step 299
    print(f"\nFinal positions at step 299: {positions_history[-1]}")
    print(f"Total live cells: {int(grid.sum())}")
