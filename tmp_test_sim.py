import json, sys, numpy as np
sys.path.insert(0, 'src')
from evolution import rule_dict_to_lut, step_grid, make_ltromino_grid

with open('archive/iter_222/results/champion_rule_perfect.json') as f:
    data = json.load(f)
rule_dict = {int(k): int(v) for k, v in data['rule_dict'].items()}
lut = rule_dict_to_lut(rule_dict)

grid = make_ltromino_grid(128, [(63,63),(64,63),(64,64)])
print('Initial:', list(zip(*np.where(grid > 0))))

for t in range(5):
    grid = step_grid(grid, lut)
    cells = list(zip(*np.where(grid > 0)))
    print(f't={t+1}: {len(cells)} bits, cells={cells}')
