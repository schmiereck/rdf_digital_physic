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

for size in [128, 256]:
    grid = np.zeros((size, size), dtype=np.uint8)
    grid[size//2, size//2] = 1
    grid[size//2 + 1, size//2] = 1
    grid[size//2 + 1, size//2 + 1] = 1
    
    print(f"\n--- Grid size: {size} ---")
    print("Step | Active Cells | CoM")
    for t in range(70):
        rows, cols = np.where(grid > 0)
        n_cells = len(rows)
        if n_cells > 0:
            com = (float(np.mean(rows)), float(np.mean(cols)))
        else:
            com = (0.0, 0.0)
        if t in [0, 1, 63, 64, 65]:
            print(f"{t:4d} | {n_cells:12d} | ({com[0]:.4f}, {com[1]:.4f})")
        grid = step_grid(grid, lut)
