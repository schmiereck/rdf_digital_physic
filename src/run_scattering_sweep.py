#!/usr/bin/env python3
"""
src/run_scattering_sweep.py

Runs a 2D hexagonal CA collision sweep to characterize classical soliton scattering.
Parameters swept:
  - Transverse spatial offset delta_y: [-4, -3, -2, -1, 0, 1, 2, 3, 4]
  - Relative temporal phase delay delta_t: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Total configurations: 9 * 13 = 117.

Outputs results to:
  - archive/iter_239/results/scattering_sweep_results.json
  - archive/iter_239/results/scattering_sweep_results.csv
"""

import csv
import json
import math
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"
OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_239" / "results"

GRID_SIZE = 256
STEPS = 200


def load_rule(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return {int(k): int(v) for k, v in data["rule_dict"].items()}


def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    # Under hex rules:
    # 0: center, 1: E, 2: SE, 3: SW, 4: W, 5: NW, 6: NE
    # Wait, let's verify if the roll offsets in analyze_collision_dynamics are:
    # e  = np.roll(grid, -1, axis=0) # wait, row is axis 0, col is axis 1
    # Actually, let's copy the step_grid function exactly as verified in analyze_collision_dynamics.py!
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]


def find_toroidal_clusters(grid: np.ndarray, threshold: int = 3) -> list[list[tuple[int, int]]]:
    coords = [tuple(map(int, c)) for c in np.argwhere(grid)]
    if not coords:
        return []
    
    adj = {c: [] for c in coords}
    for i, c1 in enumerate(coords):
        for c2 in coords[i+1:]:
            dr = abs(c1[0] - c2[0])
            dr = min(dr, GRID_SIZE - dr)
            dc = abs(c1[1] - c2[1])
            dc = min(dc, GRID_SIZE - dc)
            if max(dr, dc) <= threshold:
                adj[c1].append(c2)
                adj[c2].append(c1)
                
    visited = set()
    clusters = []
    for c in coords:
        if c not in visited:
            q = [c]
            visited.add(c)
            comp = []
            while q:
                curr = q.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            clusters.append(comp)
    return clusters


def compute_cluster_com(cluster: list[tuple[int, int]]) -> tuple[float, float]:
    if not cluster:
        return (0.0, 0.0)
    
    ref_r, ref_c = cluster[0]
    unwrapped_rows = []
    unwrapped_cols = []
    for r, c in cluster:
        dr = r - ref_r
        if dr > GRID_SIZE / 2:
            r_unwrapped = r - GRID_SIZE
        elif dr < -GRID_SIZE / 2:
            r_unwrapped = r + GRID_SIZE
        else:
            r_unwrapped = r
            
        dc = c - ref_c
        if dc > GRID_SIZE / 2:
            c_unwrapped = c - GRID_SIZE
        elif dc < -GRID_SIZE / 2:
            c_unwrapped = c + GRID_SIZE
        else:
            c_unwrapped = c
            
        unwrapped_rows.append(r_unwrapped)
        unwrapped_cols.append(c_unwrapped)
        
    mean_r = float(np.mean(unwrapped_rows)) % GRID_SIZE
    mean_c = float(np.mean(unwrapped_cols)) % GRID_SIZE
    return (mean_r, mean_c)


def toroidal_dist(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    dr = abs(p1[0] - p2[0])
    dr = min(dr, GRID_SIZE - dr)
    dc = abs(p1[1] - p2[1])
    dc = min(dc, GRID_SIZE - dc)
    return math.sqrt(dr*dr + dc*dc)


def run_simulation(lut: np.ndarray, delta_y: int, delta_t: int, mode: str) -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    
    # Glider A initial cells (NW glider, starts at 160, 96)
    glider_a_cells = [(160, 96), (161, 96), (161, 97)]
    
    # Glider B initial cells (SE glider, starts at 96 + dy, 160 + dy)
    r_b = 96 + delta_y
    c_b = 160 + delta_y
    glider_b_cells = [
        (r_b % GRID_SIZE, c_b % GRID_SIZE),
        ((r_b - 1) % GRID_SIZE, c_b % GRID_SIZE),
        ((r_b - 1) % GRID_SIZE, (c_b - 1) % GRID_SIZE)
    ]
    
    # Initialize grid at step 0
    if mode == "active" or mode == "control_a":
        for r, c in glider_a_cells:
            grid[r, c] = 1
            
    if (mode == "active" or mode == "control_b") and delta_t == 0:
        for r, c in glider_b_cells:
            grid[r, c] = 1
            
    for t in range(1, STEPS + 1):
        if (mode == "active" or mode == "control_b") and t == delta_t:
            for r, c in glider_b_cells:
                grid[r, c] = 1
        grid = step_grid(grid, lut)
        
    return grid


def classify_outcome(active_grid: np.ndarray, control_a_grid: np.ndarray, control_b_grid: np.ndarray) -> str:
    active_bits = int(active_grid.sum())
    control_a_bits = int(control_a_grid.sum())
    control_b_bits = int(control_b_grid.sum())
    
    if active_bits == 0:
        return "Annihilation"
        
    if active_bits > 12:
        return "Chaos"
        
    # Check for Transmission: both survive without path deviation or bit change (active bits exactly 8)
    if active_bits == 8 and control_a_bits == 4 and control_b_bits == 4:
        # Check clusters in the active grid
        clusters = find_toroidal_clusters(active_grid, threshold=3)
        if len(clusters) == 2:
            if len(clusters[0]) == 4 and len(clusters[1]) == 4:
                # Find CoMs of the active clusters
                coms = [compute_cluster_com(c) for c in clusters]
                
                # Compute CoMs of controls
                control_a_coords = np.argwhere(control_a_grid)
                com_control_a = compute_cluster_com([tuple(map(int, c)) for c in control_a_coords])
                
                control_b_coords = np.argwhere(control_b_grid)
                com_control_b = compute_cluster_com([tuple(map(int, c)) for c in control_b_coords])
                
                # Verify distance of each active cluster to expected control glider CoMs
                d0_a = toroidal_dist(coms[0], com_control_a)
                d1_b = toroidal_dist(coms[1], com_control_b)
                d0_b = toroidal_dist(coms[0], com_control_b)
                d1_a = toroidal_dist(coms[1], com_control_a)
                
                # If they matched perfectly with extremely low deviation (e.g. within 2.0 distance)
                if (d0_a < 2.0 and d1_b < 2.0) or (d0_b < 2.0 and d1_a < 2.0):
                    return "Transmission"
                    
    # Surviving but with altered paths/states (or modified bit counts like 4, 6, 8 but deflected, 10, etc.)
    return "Scattering/Deflection"


def main():
    print("=== Sub-light Glider Classical Soliton Scattering Sweep ===")
    print(f"Loading champion rule from: {RULE_PATH}")
    
    rule_dict = load_rule(RULE_PATH)
    lut = rule_to_lut(rule_dict)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ranges
    delta_y_range = list(range(-4, 5))
    delta_t_range = list(range(0, 13))
    
    results_list = []
    outcome_counts = {
        "Annihilation": 0,
        "Transmission": 0,
        "Scattering/Deflection": 0,
        "Chaos": 0
    }
    
    print(f"Sweeping delta_y in [-4, 4] and delta_t in [0, 12] (total 117 configurations)...")
    
    # To avoid repeating control runs unnecessarily, we can cache them by (delta_y, delta_t).
    # Since Control A only depends on delta_t (actually Control A doesn't depend on delta_y or delta_t! It starts at 0 and doesn't care about Glider B)
    # Wait, Control A is independent of both delta_y and delta_t, because only Glider A is run, starting at t=0.
    # So we can run Control A once and cache it!
    print("Pre-running Control A...")
    control_a_grid = run_simulation(lut, delta_y=0, delta_t=0, mode="control_a")
    control_a_bits = int(control_a_grid.sum())
    print(f"Control A completed. Active cells at step 200: {control_a_bits}")
    
    for dy in delta_y_range:
        for dt in delta_t_range:
            # Run Control B (only depends on dy and dt)
            control_b_grid = run_simulation(lut, delta_y=dy, delta_t=dt, mode="control_b")
            control_b_bits = int(control_b_grid.sum())
            
            # Run Active
            active_grid = run_simulation(lut, delta_y=dy, delta_t=dt, mode="active")
            active_bits = int(active_grid.sum())
            
            # Linear superposition check
            linear_sum = control_a_grid | control_b_grid
            is_linear = bool((active_grid == linear_sum).all())
            
            # Classification
            outcome = classify_outcome(active_grid, control_a_grid, control_b_grid)
            outcome_counts[outcome] += 1
            
            # Record
            results_list.append({
                "delta_y": dy,
                "delta_t": dt,
                "active_bits": active_bits,
                "control_a_bits": control_a_bits,
                "control_b_bits": control_b_bits,
                "linear_superposition": is_linear,
                "outcome": outcome
            })
            
    # Save to JSON
    json_path = OUTPUT_DIR / "scattering_sweep_results.json"
    with open(json_path, "w") as f:
        json.dump({
            "experiment": "2D hexagonal CA collision sweep",
            "rule": "champion_rule_perfect.json",
            "grid_size": GRID_SIZE,
            "steps": STEPS,
            "sweep_size": len(results_list),
            "outcome_summary": outcome_counts,
            "results": results_list
        }, f, indent=2)
    print(f"Saved JSON results to {json_path}")
    
    # Save to CSV
    csv_path = OUTPUT_DIR / "scattering_sweep_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "delta_y", "delta_t", "active_bits", "control_a_bits", "control_b_bits", "linear_superposition", "outcome"
        ])
        writer.writeheader()
        for row in results_list:
            writer.writerow(row)
    print(f"Saved CSV results to {csv_path}")
    
    print("\nSweep Complete!")
    print("Outcome Counts:")
    for k, v in outcome_counts.items():
        print(f"  {k}: {v}")
    
    # Hypothesis and Falsification analysis
    print("\n=== Hypothesis and Falsification Analysis ===")
    
    # 1. Linear superposition check
    any_non_linear = any(not r["linear_superposition"] for r in results_list)
    print(f"Evidence of non-linear interaction: {any_non_linear}")
    if any_non_linear:
        print("  - The hypothesis is not refuted by the linear superposition check: the active state is not a simple superposition of the controls.")
    else:
        print("  - The hypothesis is refuted: all runs are trivial linear superpositions.")
        
    # 2. Phase-dependency check
    # Check if for any delta_y, changing delta_t changes the outcome
    outcomes_by_dy = {}
    for r in results_list:
        outcomes_by_dy.setdefault(r["delta_y"], set()).add(r["outcome"])
    
    has_phase_dependence = any(len(outcomes) > 1 for outcomes in outcomes_by_dy.values())
    print(f"Evidence of phase-dependent outcome change: {has_phase_dependence}")
    if has_phase_dependence:
        print("  - The hypothesis is consistent with phase-dependent soliton-like scattering (outcome changes with delta_t).")
    else:
        print("  - The hypothesis is refuted: changing delta_t has no effect on collision outcomes.")


if __name__ == "__main__":
    main()
