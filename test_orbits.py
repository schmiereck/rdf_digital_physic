#!/usr/bin/env python3
import json
import numpy as np
from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine
from src.explore_two_body_attraction_v3 import run_simulation

glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
with open(glider_path, "r") as f:
    glider_data = json.load(f)
particle = glider_data["particle"]
lut_seed = glider_data["lut_seed"]

# Let's test a lower threshold or higher eta to see if we get deflection
alphas = [2.0, 2.5, 3.0]
thresholds = [0.03, 0.04, 0.05, 0.06]
gammas = [0.90, 0.95]
etas = [2.0, 3.0, 4.0]
sigma = 2.5

found = False
for alpha, threshold, gamma, eta in [(a, t, g, e) for a in alphas for t in thresholds for g in gammas for e in etas]:
    res = run_simulation(particle, lut_seed, alpha, threshold, gamma, eta, sigma, steps=80)
    if res["stable"] and res["deflection"] != 0.0:
        print(f"FOUND ACTIVE STABLE CFG: alpha={alpha}, threshold={threshold}, gamma={gamma}, eta={eta}, deflection={res['deflection']:.6f}, final_sep={res['final_separation']:.4f}")
        found = True

if not found:
    print("No stable active configuration found.")
