import json
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, center_of_mass

def get_active_cells(grid):
    rows, cols = np.where(grid > 0)
    return sorted(zip(rows.tolist(), cols.tolist()))

def get_canonical_shape(active_cells):
    if not active_cells:
        return ()
    r_anchor, c_anchor = active_cells[0]
    rel_cells = []
    for r, c in active_cells:
        dr = (r - r_anchor + 64) % 128 - 64
        dc = (c - c_anchor + 64) % 128 - 64
        rel_cells.append((dr, dc))
    min_dr = min(dr for dr, dc in rel_cells)
    min_dc = min(dc for dr, dc in rel_cells)
    canonical = sorted((dr - min_dr, dc - min_dc) for dr, dc in rel_cells)
    return tuple(canonical)

def main():
    json_path = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_vc_rule_consistency.json"
    with open(json_path) as f:
        data = json.load(f)
    
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)
    
    grid = np.zeros((128, 128), dtype=np.uint8)
    for r, c in data["seed_cells"]:
        grid[r, c] = 1
        
    print("Step | Active Count | CoM | Canonical Shape")
    print("-" * 60)
    
    for step in range(30):
        active_cells = get_active_cells(grid)
        com = center_of_mass(grid)
        shape = get_canonical_shape(active_cells)
        print(f"{step:4d} | {len(active_cells):12d} | ({com[0]:.4f}, {com[1]:.4f}) | {shape}")
        grid = step_grid(grid, lut)

if __name__ == "__main__":
    main()
