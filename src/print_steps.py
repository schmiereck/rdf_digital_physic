import json
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_rule.json"
GRID_SIZE = 128

with open(CHAMPION_JSON) as f:
    champ = json.load(f)

rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
lut = rule_dict_to_lut(rule_dict)

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
grid[63, 63] = 1
grid[64, 63] = 1
grid[64, 64] = 1

def get_com_and_bits(g):
    rows, cols = np.where(g > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

print("Step | CoM | Bit Count")
for t in range(130):
    com, b = get_com_and_bits(grid)
    print(f"{t:4d} | ({com[0]:.4f}, {com[1]:.4f}) | {b}")
    grid = step_grid(grid, lut)
