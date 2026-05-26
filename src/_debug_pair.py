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

def run(name, seed_cells, steps=10):
    grid = np.zeros((128, 128), dtype=np.uint8)
    for r, c in seed_cells:
        grid[r, c] = 1
    print(f'\n=== {name} ===')
    for t in range(steps + 1):
        cells = sorted((int(r), int(c)) for r, c in zip(*np.where(grid > 0)))
        print(f't={t}: {len(cells)} bits, cells={cells}')
        grid = step_grid(grid, lut)

run('Pair (64,63)+(64,64)', [(64, 63), (64, 64)], steps=10)
run('Full L-tromino', [(63, 63), (64, 63), (64, 64)], steps=10)
