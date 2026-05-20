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

for t in range(1, 65):
    grid = step_grid(grid, lut)
    if t in [1, 63, 64]:
        rows, cols = np.where(grid > 0)
        print(f"\n--- Step {t}: {len(rows)} active cells ---")
        print("Coordinates:", list(zip(rows, cols)))
