import json, sys, numpy as np
sys.path.insert(0, 'src')
from evolution import rule_dict_to_lut, step_grid, make_ltromino_grid

with open('archive/iter_222/results/champion_rule_perfect.json') as f:
    data = json.load(f)
rule_dict = {int(k): int(v) for k, v in data['rule_dict'].items()}
lut = rule_dict_to_lut(rule_dict)

grid = make_ltromino_grid(128, [(63,63),(64,63),(64,64)])
grids = [grid.copy()]
for t in range(500):
    grid = step_grid(grid, lut)
    grids.append(grid.copy())

# Find period by tracking canonical patterns (normalized to origin)
def canonical(cells):
    if not cells:
        return None
    cells = sorted(cells)
    # Normalize to COM-centered
    avg_r = sum(c[0] for c in cells) / len(cells)
    avg_c = sum(c[1] for c in cells) / len(cells)
    # Shift so COM is near integer half-values
    # Use min shift for canonical form
    min_r = min(c[0] for c in cells)
    min_c = min(c[1] for c in cells)
    return tuple(sorted((c[0]-min_r, c[1]-min_c) for c in cells))

# Trace for 50 steps, look for period
seen = {}
for t in range(80):
    g = grids[t]
    cells = list(zip(*np.where(g > 0)))
    pattern = canonical(cells)
    # Also track COM direction to distinguish
    if cells:
        avg_r = sum(c[0] for c in cells) / len(cells)
        avg_c = sum(c[1] for c in cells) / len(cells)
    else:
        avg_r, avg_c = 0, 0
    key = (pattern, round(avg_r*2)/2, round(avg_c*2)/2)
    if t > 0 and pattern in seen:
        t_prev, prev_cells = seen[pattern]
        print(f't={t_prev} -> t={t}: pattern repeat, delta={t-t_prev}')
        print(f'  prev cells: {prev_cells}')
        print(f'  curr cells: {cells}')
    seen[pattern] = (t, cells)

# Let me just manually look at the COM drift
print("\nCOM tracking (first 30 steps):")
for t in range(30):
    g = grids[t]
    cells = list(zip(*np.where(g > 0)))
    if cells:
        avgr = sum(c[0] for c in cells) / len(cells)
        avgc = sum(c[1] for c in cells) / len(cells)
        print(f't={t:3d}: {len(cells)} bits, COM=({avgr:.2f}, {avgc:.2f}), cells={cells}')
