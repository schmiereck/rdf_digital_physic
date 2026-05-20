import json
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_rule.json"

with open(CHAMPION_JSON) as f:
    champ = json.load(f)

rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
lut = rule_dict_to_lut(rule_dict)

size = 256
grid = np.zeros((size, size), dtype=np.uint8)
grid[128, 128] = 1
grid[129, 128] = 1
grid[129, 129] = 1

def get_relative_state(g):
    rows, cols = np.where(g > 0)
    if len(rows) == 0:
        return None
    min_r, min_c = np.min(rows), np.min(cols)
    relative_cells = sorted([(int(r - min_r), int(c - min_c)) for r, c in zip(rows, cols)])
    return tuple(relative_cells), (min_r, min_c)

states = {}
for t in range(256):
    res = get_relative_state(grid)
    if res is None:
        print(f"Died out at step {t}")
        break
    shape, origin = res
    if shape in states:
        prev_t, prev_origin = states[shape]
        p = t - prev_t
        dr = origin[0] - prev_origin[0]
        dc = origin[1] - prev_origin[1]
        print(f"Shape match: step {t} is identical to step {prev_t}!")
        print(f"  Period: {p}")
        print(f"  Translation: ({dr}, {dc})")
        # break
    else:
        states[shape] = (t, origin)
    grid = step_grid(grid, lut)
