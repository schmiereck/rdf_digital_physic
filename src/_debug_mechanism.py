import json
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, 'src')
from evolution import rule_dict_to_lut, step_grid

# Load rule
with open('archive/iter_222/results/champion_rule_perfect.json') as f:
    data = json.load(f)
rule_dict = {int(k): int(v) for k, v in data['rule_dict'].items()}
lut = rule_dict_to_lut(rule_dict)

# Helper to run one step and show details
def show_step(name, seed_cells):
    grid = np.zeros((128, 128), dtype=np.uint8)
    for r, c in seed_cells:
        grid[r, c] = 1
    print(f'\n=== {name} ===')
    print(f't=0: cells={seed_cells}')
    
    # Compute neighborhoods for active cells
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
    states = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    
    for r, c in seed_cells:
        s = int(states[r, c])
        out = rule_dict.get(s, s)
        print(f'  Cell ({r},{c}): state={s:3d} (0b{s:07b}) -> out={out:3d} (0b{out:07b}), center_bit={int(lut[s])}')
    
    grid2 = step_grid(grid, lut)
    new_cells = sorted((int(r), int(c)) for r, c in zip(*np.where(grid2 > 0)))
    print(f't=1: cells={new_cells}')
    
    # Show neighborhoods for new cells
    e2  = np.roll(grid2, -1, axis=0)
    w2  = np.roll(grid2,  1, axis=0)
    ne2 = np.roll(grid2, -1, axis=1)
    sw2 = np.roll(grid2,  1, axis=1)
    se2 = np.roll(e2,    1, axis=1)
    nw2 = np.roll(w2,   -1, axis=1)
    states2 = (
        (grid2.astype(np.uint16) << 6)
        | (e2.astype(np.uint16)  << 5)
        | (se2.astype(np.uint16) << 4)
        | (sw2.astype(np.uint16) << 3)
        | (w2.astype(np.uint16)  << 2)
        | (nw2.astype(np.uint16) << 1)
        |  ne2.astype(np.uint16)
    ).astype(np.uint8)
    
    for r, c in new_cells:
        s = int(states2[r, c])
        out = rule_dict.get(s, s)
        print(f'  Cell ({r},{c}): state={s:3d} (0b{s:07b}) -> out={out:3d} (0b{out:07b}), center_bit={int(lut[s])}')
    
    return grid2

# Run for different seeds
show_step('Single bit (64,64)', [(64, 64)])
show_step('Pair (64,63)+(64,64)', [(64, 63), (64, 64)])
show_step('Full L-tromino', [(63, 63), (64, 63), (64, 64)])
