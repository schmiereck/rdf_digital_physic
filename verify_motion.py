import json
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(".").resolve()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_rule.json"

with open(CHAMPION_JSON) as f:
    champ = json.load(f)

rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
lut = rule_dict_to_lut(rule_dict)

GRID_SIZE = 128
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
grid[63, 63] = 1
grid[64, 63] = 1
grid[64, 64] = 1

for t in range(201):
    rows, cols = np.where(grid > 0)
    if len(rows) > 0:
        com_r, com_c = np.mean(rows), np.mean(cols)
        print(f"step={t:3d} | bits={len(rows):3d} | CoM=({com_r:.3f}, {com_c:.3f}) | bbox=({rows.min()}-{rows.max()}, {cols.min()}-{cols.max()})")
    else:
        print(f"step={t:3d} | DEAD")
    grid = step_grid(grid, lut)
