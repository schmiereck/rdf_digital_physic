#!/usr/bin/env python3
import os
import sys
import json
import itertools
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.inspect_sweep_v4 import run_simulation

def main():
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    alphas = [1.0, 2.0, 3.0, 4.0]
    thresholds = [0.015, 0.025, 0.035, 0.045, 0.055, 0.065]
    gammas = [0.90, 0.95]
    etas = [1.0, 2.0, 3.0, 4.0, 5.0]
    sigma = 2.5
    
    combinations = list(itertools.product(alphas, thresholds, gammas, etas))
    print(f"Scanning {len(combinations)} configurations for non-zero deflection...")
    
    found = 0
    for alpha, threshold, gamma, eta in combinations:
        res = run_simulation(particle, lut_seed, alpha, threshold, gamma, eta, sigma, steps=80)
        if res["stable"] and abs(res["deflection"]) > 1e-5:
            print(f"FOUND: alpha={alpha}, thresh={threshold:.3f}, gamma={gamma:.2f}, eta={eta:.2f} -> deflection={res['deflection']:.6f}")
            found += 1
            
    print(f"Scan complete. Found {found} configurations with non-zero deflection.")

if __name__ == "__main__":
    main()
