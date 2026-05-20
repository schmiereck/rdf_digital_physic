#!/usr/bin/env python3
"""
src/analyze_collision_dynamics.py

Analyzes the final states of the sub-light glider collisions at step 200 for offsets -4 to +4.
Loads champion_rule_perfect.json from archive/iter_222/results/.
Classifies the outcomes into:
  a) Two independent moving gliders (NW and SE, or changed trajectories).
  b) A single 8-bit stationary still life or oscillator (no net motion).
  c) Chaotic / annihilated / other.

Saves detailed findings to archive/iter_223/results/collision_dynamics_analysis.json
and prints a clean text summary.
"""

import json
import math
import sys
from pathlib import Path
import numpy as np

# Setup Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"
OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_223" / "results"
OUTPUT_JSON_PATH = OUTPUT_DIR / "collision_dynamics_analysis.json"

GRID_SIZE = 128
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


def init_glider_a() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    # Glider A (moves NW)
    glider_a = [(80, 48), (81, 48), (81, 49)]
    for r, c in glider_a:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


def init_glider_b(offset: int) -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    # Glider B (moves SE)
    r_b = 48 + offset
    c_b = 80 + offset
    glider_b = [(r_b, c_b), (r_b - 1, c_b), (r_b - 1, c_b - 1)]
    for r, c in glider_b:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


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
        # Unwrap row
        dr = r - ref_r
        if dr > GRID_SIZE / 2:
            r_unwrapped = r - GRID_SIZE
        elif dr < -GRID_SIZE / 2:
            r_unwrapped = r + GRID_SIZE
        else:
            r_unwrapped = r
            
        # Unwrap col
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


def toroidal_displacement(p1: tuple[float, float], p2: tuple[float, float]) -> tuple[float, float]:
    dr = p2[0] - p1[0]
    if dr > GRID_SIZE / 2:
        dr -= GRID_SIZE
    elif dr < -GRID_SIZE / 2:
        dr += GRID_SIZE
        
    dc = p2[1] - p1[1]
    if dc > GRID_SIZE / 2:
        dc -= GRID_SIZE
    elif dc < -GRID_SIZE / 2:
        dc += GRID_SIZE
        
    return (dr, dc)


def get_displacement_direction(dr: float, dc: float) -> str:
    # A moves NW (dr < 0, dc > 0)
    # B moves SE (dr > 0, dc < 0)
    if abs(dr) < 0.1 and abs(dc) < 0.1:
        return "Stationary"
    
    # Analyze angle
    angle = math.atan2(dr, dc) # in radians, range [-pi, pi]
    # NW is around angle = 3*pi/4 or -3*pi/4?
    # dr < 0 is upward, dc > 0 is rightward. In row-col, row increases downward, col increases rightward.
    # So row decreasing, col increasing means dr < 0, dc > 0.
    # If dr < 0 and dc > 0, angle is in [-pi/2, 0] or specifically math.atan2(dr, dc) will be negative.
    # Let's just use quadrant sign-based rules which are clearer:
    if dr < -0.1 and dc > 0.1:
        return "NW"
    elif dr > 0.1 and dc < -0.1:
        return "SE"
    elif dr < -0.1 and dc < -0.1:
        return "SW"
    elif dr > 0.1 and dc > 0.1:
        return "NE"
    else:
        return f"Other ({dr:+.2f}, {dc:+.2f})"


def main():
    print("=== Analyzing Sub-light Glider Collision Dynamics ===")
    
    # Ensure directories exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load perfect champion rule and convert to LUT
    print(f"Loading rule from: {RULE_PATH}")
    rule_dict = load_rule(RULE_PATH)
    lut = rule_to_lut(rule_dict)
    
    # Run standalone Glider A and B to have comparison states
    print("Pre-simulating individual gliders...")
    grid_a_190, grid_a_200 = None, None
    g_a = init_glider_a()
    for step in range(1, STEPS + 1):
        g_a = step_grid(g_a, lut)
        if step == 190:
            grid_a_190 = g_a.copy()
        if step == 200:
            grid_a_200 = g_a.copy()
            
    # We will simulate Glider B individually for each offset inside the loop
    analysis_results = {}
    
    print("\nStarting offset scan...")
    for offset in range(-4, 5):
        # 1. Simulate Glider B standalone
        grid_b_190, grid_b_200 = None, None
        g_b = init_glider_b(offset)
        for step in range(1, STEPS + 1):
            g_b = step_grid(g_b, lut)
            if step == 190:
                grid_b_190 = g_b.copy()
            if step == 200:
                grid_b_200 = g_b.copy()
                
        # 2. Simulate actual combined collision
        grid_both_190, grid_both_200 = None, None
        g_both = init_glider_a() | init_glider_b(offset)
        for step in range(1, STEPS + 1):
            g_both = step_grid(g_both, lut)
            if step == 190:
                grid_both_190 = g_both.copy()
            if step == 200:
                grid_both_200 = g_both.copy()
                
        bits_190 = int(grid_both_190.sum())
        bits_200 = int(grid_both_200.sum())
        
        # Check superposition match
        superposition_match_190 = np.array_equal(grid_both_190, grid_a_190 | grid_b_190)
        superposition_match_200 = np.array_equal(grid_both_200, grid_a_200 | grid_b_200)
        unaffected = superposition_match_200
        
        # Cluster Analysis
        clusters_190 = find_toroidal_clusters(grid_both_190)
        clusters_200 = find_toroidal_clusters(grid_both_200)
        
        num_clusters_190 = len(clusters_190)
        num_clusters_200 = len(clusters_200)
        
        # Match clusters from 190 to 200
        cluster_info = []
        classification = ""
        phys_summary = ""
        
        if bits_200 == 0:
            classification = "c) Chaotic / annihilated / other"
            phys_summary = "Annihilation (0 bits at step 200)"
        elif bits_200 > 20:
            classification = "c) Chaotic / annihilated / other"
            phys_summary = f"Chaotic explosion ({bits_200} bits at step 200)"
        else:
            # We have few bits. Let's analyze motion
            coms_190 = [compute_cluster_com(c) for c in clusters_190]
            coms_200 = [compute_cluster_com(c) for c in clusters_200]
            
            # Match them
            matched_indices = []
            if num_clusters_190 == 2 and num_clusters_200 == 2:
                # Two clusters at both steps
                # Try both pairings to minimize distance sum
                pair1_dist = toroidal_dist(coms_190[0], coms_200[0]) + toroidal_dist(coms_190[1], coms_200[1])
                pair2_dist = toroidal_dist(coms_190[0], coms_200[1]) + toroidal_dist(coms_190[1], coms_200[0])
                if pair1_dist <= pair2_dist:
                    pairing = [(0, 0), (1, 1)]
                else:
                    pairing = [(0, 1), (1, 0)]
            elif num_clusters_190 == 1 and num_clusters_200 == 1:
                pairing = [(0, 0)]
            else:
                pairing = []
                
            has_motion = False
            moving_directions = []
            
            for idx_190, idx_200 in pairing:
                c190 = clusters_190[idx_190]
                c200 = clusters_200[idx_200]
                com190 = coms_190[idx_190]
                com200 = coms_200[idx_200]
                
                dr, dc = toroidal_displacement(com190, com200)
                direction = get_displacement_direction(dr, dc)
                
                # Check if it matches Glider A or Glider B's cells
                matches_a = all(grid_a_200[r, c] == 1 for r, c in c200)
                matches_b = all(grid_b_200[r, c] == 1 for r, c in c200)
                
                unaffected_glider = "None"
                if matches_a:
                    unaffected_glider = "Glider A"
                elif matches_b:
                    unaffected_glider = "Glider B"
                    
                if direction != "Stationary":
                    has_motion = True
                    moving_directions.append(direction)
                    
                cluster_info.append({
                    "cluster_size_190": len(c190),
                    "cluster_size_200": len(c200),
                    "com_190": com190,
                    "com_200": com200,
                    "displacement": [dr, dc],
                    "direction": direction,
                    "unaffected_glider_match": unaffected_glider
                })
                
            if has_motion:
                # Are they two independent moving gliders in the original NW/SE directions?
                if unaffected:
                    classification = "a) Two independent moving gliders (no interaction)"
                    phys_summary = "Two independent gliders: Unaffected, continuing in original NW and SE directions"
                else:
                    classification = "a) Two independent moving gliders (trajectories changed)"
                    dirs_str = " & ".join(moving_directions)
                    phys_summary = f"Two independent gliders: Interacted, now moving in {dirs_str} directions"
            else:
                if bits_200 == 8:
                    classification = "b) A single 8-bit stationary still life or oscillator"
                    phys_summary = "A single 8-bit stationary still life or oscillator (no net motion)"
                else:
                    classification = "c) Chaotic / annihilated / other"
                    phys_summary = f"Stationary remnant or oscillator ({bits_200} bits, no net motion)"
                    
        print(f"Offset {offset:2d} Classification: {classification}")
        print(f"          Summary: {phys_summary}")
        
        analysis_results[str(offset)] = {
            "offset": offset,
            "bits_step_190": bits_190,
            "bits_step_200": bits_200,
            "classification_category": classification,
            "physical_summary": phys_summary,
            "unaffected": bool(unaffected),
            "num_clusters_190": num_clusters_190,
            "num_clusters_200": num_clusters_200,
            "cluster_details": cluster_info
        }
        
    # Save to JSON
    with open(OUTPUT_JSON_PATH, "w") as f:
        json.dump(analysis_results, f, indent=2)
    print(f"\nDetailed analysis saved to: {OUTPUT_JSON_PATH}")
    
    # Print clean readable summary
    print("\n" + "="*80)
    print("                 SUB-LIGHT GLIDER COLLISION DYNAMICS SUMMARY")
    print("="*80)
    print(f"{'Offset':^8s} | {'Step 190':^8s} | {'Step 200':^8s} | {'Physical Classification & Outcome'}")
    print("-"*80)
    for offset in range(-4, 5):
        res = analysis_results[str(offset)]
        print(f"{offset:^8d} | {res['bits_step_190']:^8d} | {res['bits_step_200']:^8d} | {res['physical_summary']}")
    print("="*80)


if __name__ == "__main__":
    main()
