import json
import numpy as np
from pathlib import Path

# Load original rule
champion_path = Path("archive/iter_179/results/champion_rule.json")
with open(champion_path, "r") as f:
    champion = json.load(f)

rule_dict = champion["rule_dict"]
chrom = np.array(champion["chromosome"], dtype=np.uint8)

# Simulation functions
def step_grid_get_states(grid: np.ndarray, lut: np.ndarray):
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state], state

# Initialise grid
grid = np.zeros((128, 128), dtype=np.uint8)
for r, c in [(63, 63), (64, 63), (64, 64)]:
    grid[r, c] = 1

visited_states = set()
for step in range(200):
    next_grid, state_grid = step_grid_get_states(grid, chrom)
    # find all cells in grid or next_grid that are active, and collect their neighborhood states
    # Actually, any cell whose state is non-zero (i.e. has active cells in its neighborhood)
    rows, cols = np.where(state_grid > 0)
    for r, col in zip(rows, cols):
        visited_states.add((int(state_grid[r, col]), int(chrom[state_grid[r, col]])))
    grid = next_grid

print(f"Total visited states with non-zero neighborhoods: {len(visited_states)}")
print("Visited states (state, next_center_bit):")
for s, bit in sorted(visited_states):
    print(f"  {s:3d} (center {(s>>6)&1}) -> center {bit}")
