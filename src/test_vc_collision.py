#!/usr/bin/env python3
"""
src/test_vc_collision.py

Implements a collision simulation between two sub-light gliders (v=0.469c) under Rule A.
Rule A is loaded from archive/iter_222/results/champion_rule_perfect.json.
The script simulates 200 steps for transverse offsets from -4 to +4, records
the quantitative results to collision_results.json, and saves the head-on (0-offset)
collision sequence as a GIF.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Setup Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_223" / "results"
RESULTS_JSON_PATH = RESULTS_DIR / "collision_results.json"
GIF_PATH = RESULTS_DIR / "head_on_collision.gif"

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


def init_grid_with_collision(offset: int) -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    
    # 3. Glider A (moves NW, row decreasing, col increasing) is placed at (80, 48):
    # cells [(80, 48), (81, 48), (81, 49)]
    glider_a = [(80, 48), (81, 48), (81, 49)]
    for r, c in glider_a:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
        
    # 4. Glider B (moves SE, row increasing, col decreasing) is placed at (48 + offset, 80 + offset):
    # cells [(r, c), (r-1, c), (r-1, c-1)] where r = 48 + offset, c = 80 + offset
    r_b = 48 + offset
    c_b = 80 + offset
    glider_b = [(r_b, c_b), (r_b - 1, c_b), (r_b - 1, c_b - 1)]
    for r, c in glider_b:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
        
    return grid


def main():
    print("=== Sub-light Glider Collision Simulation (v=0.469c) ===")
    
    # Make sure output directories exist
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load rule and convert to LUT
    print(f"Loading rule from: {RULE_PATH}")
    rule_dict = load_rule(RULE_PATH)
    lut = rule_to_lut(rule_dict)
    print(f"Loaded rule. Non-zero LUT count: {int(lut.sum())}")
    
    collision_results = {}
    
    # Simulate for transverse offsets from -4 to +4.
    head_on_frames = []
    head_on_bit_counts = []
    
    for offset in range(-4, 5):
        grid = init_grid_with_collision(offset)
        initial_bits = int(grid.sum())
        
        # We expect 6 bits since the gliders shouldn't overlap
        assert initial_bits == 6, f"Expected 6 bits for offset {offset}, but got {initial_bits}"
        
        bit_counts = [initial_bits]
        
        # Save step 0 for head-on collision GIF
        if offset == 0:
            head_on_frames.append(grid.copy())
            head_on_bit_counts.append(initial_bits)
            
        current_grid = grid.copy()
        for step in range(1, STEPS + 1):
            current_grid = step_grid(current_grid, lut)
            bc = int(current_grid.sum())
            bit_counts.append(bc)
            
            if offset == 0:
                head_on_frames.append(current_grid.copy())
                head_on_bit_counts.append(bc)
                
        final_bits = bit_counts[-1]
        max_bits = max(bit_counts)
        
        print(f"Offset {offset:2d}: Initial bits={initial_bits}, Final bits={final_bits}, Max bits={max_bits}")
        
        collision_results[str(offset)] = {
            "offset": offset,
            "initial_bits": initial_bits,
            "final_bits": final_bits,
            "max_bits": max_bits
        }
        
    # 6. Save quantitative results to JSON
    with open(RESULTS_JSON_PATH, "w") as f:
        json.dump(collision_results, f, indent=2)
    print(f"Quantitative results saved to: {RESULTS_JSON_PATH}")
    
    # 7. Save head-on collision (offset=0) to GIF
    print(f"Generating 0-offset head-on collision GIF -> {GIF_PATH}")
    
    # Let's generate a beautiful visualization with matplotlib and pillow
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title("Head-on Sub-light Glider Collision (v=0.469c)\nRule A (champion_rule_perfect.json)", color="white", fontsize=10)
    ax.set_xlabel("col", color="white", fontsize=8)
    ax.set_ylabel("row", color="white", fontsize=8)
    ax.tick_params(colors="white")
    for sp in ax.spines.values():
        sp.set_edgecolor("white")
        
    img = ax.imshow(
        head_on_frames[0], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1
    )
    info = ax.text(
        0.02, 0.97, f"step=0  bits={head_on_bit_counts[0]}",
        transform=ax.transAxes, color="white", fontsize=10, va="top"
    )
    
    def update(frame_idx):
        img.set_data(head_on_frames[frame_idx])
        info.set_text(f"step={frame_idx}  bits={head_on_bit_counts[frame_idx]}")
        return img, info
        
    ani = animation.FuncAnimation(
        fig, update, frames=len(head_on_frames), interval=80, blit=True
    )
    ani.save(str(GIF_PATH), writer="pillow", fps=12)
    plt.close(fig)
    print(f"GIF saved successfully at {GIF_PATH}")


if __name__ == "__main__":
    main()
