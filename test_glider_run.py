import json
import numpy as np
from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine

glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
with open(glider_path, "r") as f:
    glider_data = json.load(f)

particle = glider_data["particle"]
lut_seed = glider_data["lut_seed"]

engine = ClosedLoopLatchingEngine(
    L=64,
    gamma=0.9,
    eta=1.0,
    threshold=999.0,
    alpha=2.0,
    sigma=1.5,
    lut_seed=lut_seed
)

for dl, dr, dc, ch in particle:
    engine.temporal_grid[(32+dl)%64, (32+dr)%64, (32+dc)%64, ch] = 1

print("Initial active bits:", engine.temporal_grid.sum())

for t in range(1, 61):
    engine.step()
    active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
    idx = np.argwhere(active_mask)
    if idx.size > 0:
        com = np.mean(idx[:, :3], axis=0)
        if t % 10 == 0:
            print(f"Step {t:2d}: active bits = {active_mask.sum()}, center = {com}")
    else:
        print(f"Step {t:2d}: NO ACTIVE BITS!")
