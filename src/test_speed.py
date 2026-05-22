#!/usr/bin/env python3
import time
import json
import numpy as np
from src.engine_d4_closed_loop import ClosedLoopLatchingEngine

def seed_gliders(engine: ClosedLoopLatchingEngine, particle: list):
    L = engine.L
    cx1, cy1, cz1 = 16, 13, 16
    for dx, dy, dz, ch in particle:
        engine.temporal_grid[(cx1 + dx) % L, (cy1 + dy) % L, (cz1 + dz) % L, ch] = 1
    cx2, cy2, cz2 = 16, 19, 16
    for dx, dy, dz, ch in particle:
        engine.temporal_grid[(cx2 + dx) % L, (cy2 + dy) % L, (cz2 + dz) % L, ch] = 1

def main():
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    L = 32
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=0.1,
        kappa=0.05,
        eta=0.1,
        threshold=1.5,
        alpha=2.0,
        cutoff_radius=4,
        lut_seed=lut_seed,
        use_12_channels=True
    )
    
    seed_gliders(engine, particle)
    
    t0 = time.time()
    for t in range(1, 121):
        engine.step()
    t1 = time.time()
    print(f"Time for 120 steps: {t1 - t0:.4f} seconds (i.e., {120 / (t1 - t0):.1f} steps/sec)")

if __name__ == "__main__":
    main()
