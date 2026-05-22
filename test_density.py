#!/usr/bin/env python3
import json
import numpy as np
from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine

glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
with open(glider_path, "r") as f:
    glider_data = json.load(f)
particle = glider_data["particle"]
lut_seed = glider_data["lut_seed"]

L = 32
# Let's use eta = 2.0 (highest deposition in sweep)
# gamma = 0.95 (highest retention in sweep)
engine = ClosedLoopLatchingEngine(
    L=L,
    gamma=0.95,
    eta=2.0,
    threshold=0.1,
    alpha=2.0,
    sigma=2.5,
    lut_seed=lut_seed,
    use_12_channels=True
)

for dl, dr, dc, ch in particle:
    engine.temporal_grid[(16 + dl) % L, (13 + dr) % L, (16 + dc) % L, ch] = 1
    engine.temporal_grid[(16 + dl) % L, (19 + dr) % L, (16 + dc) % L, ch] = 1

for t in range(1, 21):
    engine.step()
    max_lat = np.max(engine.latency_field)
    sum_lat = np.sum(engine.latency_field)
    print(f"Step {t:2d} | Max Latency: {max_lat:.6f} | Sum Latency: {sum_lat:.6f}")
