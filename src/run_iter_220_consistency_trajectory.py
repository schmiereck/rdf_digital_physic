#!/usr/bin/env python3
"""
run_iter_220_consistency_trajectory.py

Full 500-step simulation of the consistency champion rule from iter_220
with L-tromino seed on a 128x128 grid.
"""

import json
import math
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, center_of_mass

# -- Configuration --

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_vc_rule_consistency.json"
OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_220" / "results"
TRAJECTORY_LOG = OUTPUT_DIR / "trajectory_log_consistency.txt"
GIF_PATH = OUTPUT_DIR / "champion_vc_rule_consistency.gif"

GRID_SIZE = 128
STEPS = 500
L_TROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]

# Steps at which to report center of mass
REPORT_STEPS = [0, 100, 200, 300, 400, 500]


# -- Helpers --

def make_grid():
    """Create a 128x128 grid with the L-tromino seed."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in L_TROMINO_CELLS:
        grid[r, c] = 1
    return grid


def get_active_cells(grid):
    """Return sorted list of (row, col) positions of all active cells."""
    rows, cols = np.where(grid > 0)
    return sorted(zip(rows.tolist(), cols.tolist()))


def get_canonical_shape(active_cells):
    """Get a canonical relative pattern (translation-invariant)."""
    if not active_cells:
        return ()
    # Use first cell as anchor
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


def unwrap_trajectory(raw_active_cells_history):
    """
    Robustly unwrap the cell positions step-by-step to calculate true,
    continuous unwrapped coordinates and Center of Mass on a toroidal grid.
    """
    if not raw_active_cells_history:
        return []

    unwrapped_history = []
    
    # Step 0
    cells_0 = raw_active_cells_history[0]
    if not cells_0:
        return []
    
    unwrapped_cells_prev = [np.array(cell, dtype=float) for cell in cells_0]
    com_0 = np.mean(unwrapped_cells_prev, axis=0)
    
    unwrapped_history.append({
        "unwrapped_cells": [tuple(c) for c in unwrapped_cells_prev],
        "com": (float(com_0[0]), float(com_0[1])),
    })
    
    for t in range(1, len(raw_active_cells_history)):
        cells_t = raw_active_cells_history[t]
        if not cells_t:
            unwrapped_history.append({
                "unwrapped_cells": [],
                "com": (0.0, 0.0),
            })
            continue
        
        cells_prev = raw_active_cells_history[t - 1]
        
        # Find the pair of cells (one from prev step, one from curr step)
        # that are closest toroidally to align the unwrapped coordinate systems.
        best_dist = float('inf')
        best_pair = None
        for p_idx, prev_c in enumerate(cells_prev):
            for c_idx, curr_c in enumerate(cells_t):
                dr = (curr_c[0] - prev_c[0] + 64) % 128 - 64
                dc = (curr_c[1] - prev_c[1] + 64) % 128 - 64
                dist = dr**2 + dc**2
                if dist < best_dist:
                    best_dist = dist
                    best_pair = (p_idx, c_idx, dr, dc)
                    
        p_idx, c_idx, dr, dc = best_pair
        
        # Unwrapped position of the current anchor cell
        curr_unwrapped_anchor = np.array(unwrapped_cells_prev[p_idx]) + np.array([dr, dc])
        
        # Find unwrapped positions of all other cells in cells_t relative to this anchor
        anchor_grid = cells_t[c_idx]
        unwrapped_cells_t = []
        for curr_c in cells_t:
            dr_rel = (curr_c[0] - anchor_grid[0] + 64) % 128 - 64
            dc_rel = (curr_c[1] - anchor_grid[1] + 64) % 128 - 64
            curr_unwrapped = curr_unwrapped_anchor + np.array([dr_rel, dc_rel])
            unwrapped_cells_t.append(curr_unwrapped)
            
        com_t = np.mean(unwrapped_cells_t, axis=0)
        unwrapped_cells_prev = unwrapped_cells_t
        
        unwrapped_history.append({
            "unwrapped_cells": [tuple(c) for c in unwrapped_cells_t],
            "com": (float(com_t[0]), float(com_t[1])),
        })
        
    return unwrapped_history


# -- Main --

def main():
    print("=" * 70)
    print("ITER 220 CONSISTENCY CHAMPION RULE -- TRAJECTORY ANALYSIS")
    print("=" * 70)

    # Load champion rule
    with open(CHAMPION_JSON) as f:
        champ = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)

    print(f"\nFitness:          {champ.get('fitness', 0.0):.6f}")
    print(f"Fitness function: {champ.get('fitness_function', 'Unknown')}")
    print(f"Grid size:        {GRID_SIZE}x{GRID_SIZE}")
    print(f"Seed:             {champ.get('seed_particle', 'L_TROMINO_3bit')}")
    print(f"Seed cells:       {L_TROMINO_CELLS}")
    print(f"Rule entries:     {len(rule_dict)} (of 128 possible)")
    print()

    # Run simulation and collect raw cell active cells at each step
    grid = make_grid()
    raw_history = []  # list of list of cells
    
    for t in range(STEPS + 1):
        raw_history.append(get_active_cells(grid))
        if t < STEPS:
            grid = step_grid(grid, lut)

    # Perform robust unwrapping of the trajectory
    unwrapped_history = unwrap_trajectory(raw_history)

    # Re-evaluate metrics using the unwrapped trajectory
    history = []
    com_start = unwrapped_history[0]["com"]

    for t in range(STEPS + 1):
        active_cells = raw_history[t]
        active_count = len(active_cells)
        com_raw = center_of_mass(make_grid() if t == 0 else step_grid(make_grid(), lut)) # dummy grid to avoid re-running step_grid, wait
        # Let's just compute simple raw com from active_cells directly!
        if active_cells:
            com_raw = (float(np.mean([c[0] for c in active_cells])), float(np.mean([c[1] for c in active_cells])))
        else:
            com_raw = (0.0, 0.0)
            
        com_unwrapped = unwrapped_history[t]["com"]
        shape = get_canonical_shape(active_cells)

        if t == 0:
            step_vel = 0.0
            dx_step = 0.0
            dy_step = 0.0
        else:
            prev_com_unwrapped = unwrapped_history[t-1]["com"]
            dx_step = com_unwrapped[0] - prev_com_unwrapped[0]
            dy_step = com_unwrapped[1] - prev_com_unwrapped[1]
            step_vel = math.sqrt(dx_step**2 + dy_step**2)

        disp = math.sqrt((com_unwrapped[0] - com_start[0])**2 + (com_unwrapped[1] - com_start[1])**2)

        history.append({
            "step": t,
            "com_raw": com_raw,
            "com_unwrapped": com_unwrapped,
            "active_count": active_count,
            "active_cells": active_cells,
            "shape": shape,
            "displacement": disp,
            "step_velocity": step_vel,
            "dx_step": dx_step,
            "dy_step": dy_step
        })

    # -- Analysis --

    # 1. Period of oscillation of canonical shapes & distinct shapes
    shapes = [h["shape"] for h in history]
    unique_shapes = sorted(list(set(shapes)))
    
    shape_period = None
    for p in range(1, len(shapes) // 2):
        match = True
        for idx in range(len(shapes) - p):
            if shapes[idx] != shapes[idx + p]:
                match = False
                break
        if match:
            shape_period = p
            break

    # 2. Velocity and Displacement
    com_end = history[STEPS]["com_unwrapped"]
    total_dx = com_end[0] - com_start[0]
    total_dy = com_end[1] - com_start[1]
    total_dist = math.sqrt(total_dx**2 + total_dy**2)
    avg_velocity = total_dist / STEPS

    # 3. Size conservation
    counts = [h["active_count"] for h in history]
    max_count = max(counts)
    min_count = min(counts)
    is_conserved = (max_count == 3 and min_count == 3)

    # 4. Classification of motion
    velocities = [h["step_velocity"] for h in history[1:]]
    max_vel = max(velocities) if velocities else 0.0
    mean_vel = np.mean(velocities) if velocities else 0.0
    non_zero_steps = sum(1 for v in velocities if v > 1e-6)
    zero_steps = STEPS - non_zero_steps

    if avg_velocity < 1e-6:
        classification = "STATIONARY"
    elif zero_steps > STEPS * 0.7:
        classification = "OSCILLATING"
    else:
        classification = "MOVING/GLIDER"

    # 5. True v<c glider verification
    # Speed of light is c=1.0 in this model.
    # So if average velocity is < 1.0, it is sublight.
    is_sublight_glider = "No"
    if classification == "MOVING/GLIDER" and is_conserved:
        if avg_velocity < 1.0 - 1e-7:
            is_sublight_glider = "Yes"
        else:
            is_sublight_glider = f"No (it is a speed-of-light v=c glider since v = {avg_velocity:.6f})"

    # Output Center of Mass Report
    print("=" * 70)
    print("CENTER OF MASS REPORT (UNWRAPPED)")
    print("=" * 70)
    for t in REPORT_STEPS:
        h = history[t]
        com = h["com_unwrapped"]
        print(f"  Step {t:4d}: CoM = ({com[0]:>12.6f}, {com[1]:>12.6f}), "
              f"active cells = {h['active_count']}, shape = {h['shape']}")
    print()

    print("=" * 70)
    print("VELOCITY & MOTION ANALYSIS")
    print("=" * 70)
    print(f"  Initial CoM:             ({com_start[0]:.6f}, {com_start[1]:.6f})")
    print(f"  Final CoM (Unwrapped):   ({com_end[0]:.6f}, {com_end[1]:.6f})")
    print(f"  Total Unwrapped Delta:   ({total_dx:+.6f}, {total_dy:+.6f})")
    print(f"  Total unwrapped distance: {total_dist:.6f} cells")
    print(f"  Steps:                   {STEPS}")
    print(f"  Avg velocity v:          {avg_velocity:.6f} cells/step")
    print(f"  Max step velocity:       {max_vel:.6f}")
    print(f"  Mean step velocity:      {mean_vel:.6f}")
    print(f"  Steps with motion:       {non_zero_steps} / {STEPS}")
    print(f"  Steps stationary:        {zero_steps} / {STEPS}")
    print(f"  Classification:          {classification}")
    print()
    print(f"  Canonical Shapes detected: {len(unique_shapes)}")
    for s_idx, sh in enumerate(unique_shapes):
        print(f"    Shape {s_idx + 1}: {sh}")
    print(f"  Period of shape oscillation: {shape_period} step(s)")
    print(f"  Perfect size conservation (3 cells): {is_conserved} (min={min_count}, max={max_count})")
    print(f"  True stable v<c glider:  {is_sublight_glider}")
    print()

    # -- Write detailed trajectory analysis --
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append(f"TRAJECTORY LOG -- iter_220 consistency champion rule")
    log_lines.append(f"Source JSON: {CHAMPION_JSON.name}")
    log_lines.append(f"Seed: {champ.get('seed_particle', 'L_TROMINO_3bit')} at {L_TROMINO_CELLS}")
    log_lines.append(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Steps: {STEPS}")
    log_lines.append(f"Rule entries: {len(rule_dict)}")
    log_lines.append("")
    log_lines.append("Rule dictionary:")
    for k in sorted(rule_dict.keys()):
        log_lines.append(f"  {k:3d} (0b{k:07b}) -> {rule_dict[k]}")
    log_lines.append("")
    log_lines.append("=" * 80)
    log_lines.append(f"STEP | CoM_row_raw | CoM_col_raw | CoM_row_unwrapped | CoM_col_unwrapped | Active | Displacement | Step Velocity")
    log_lines.append("-" * 125)

    for t in range(STEPS + 1):
        h = history[t]
        com_r = h["com_raw"]
        com_u = h["com_unwrapped"]
        marker = " ***" if t in REPORT_STEPS else ""
        log_lines.append(
            f"{t:4d} | {com_r[0]:11.6f} | {com_r[1]:11.6f} | {com_u[0]:17.6f} | {com_u[1]:17.6f} | "
            f"{h['active_count']:6d} | {h['displacement']:12.6f} | {h['step_velocity']:13.6f}{marker}"
        )

    log_lines.append("-" * 125)
    log_lines.append("")
    log_lines.append("SUMMARY")
    log_lines.append("=" * 80)
    log_lines.append(f"Classification:              {classification}")
    log_lines.append(f"Avg velocity v:              {avg_velocity:.8f} cells/step")
    log_lines.append(f"Total displacement (unwrapped): ({total_dx:.6f}, {total_dy:.6f})")
    log_lines.append(f"Total unwrapped distance:    {total_dist:.6f} cells")
    log_lines.append(f"Canonical shapes count:      {len(unique_shapes)}")
    for s_idx, sh in enumerate(unique_shapes):
        log_lines.append(f"  Shape {s_idx + 1}: {sh}")
    log_lines.append(f"Period of shape oscillation: {shape_period} step(s)")
    log_lines.append(f"Perfect size conservation:   {is_conserved} (min={min_count}, max={max_count})")
    log_lines.append(f"True stable v<c glider:      {is_sublight_glider}")
    log_lines.append(f"Max step speed:              {max_vel:.6f}")
    log_lines.append(f"Mean step speed:             {mean_vel:.6f}")
    log_lines.append(f"Motion steps:                {non_zero_steps}/{STEPS}")
    log_lines.append(f"Stationary steps:            {zero_steps}/{STEPS}")
    log_lines.append("")
    log_lines.append("=" * 80)
    log_lines.append("ACTIVE CELL COORDINATES (selected steps)")
    log_lines.append("-" * 80)
    for t in REPORT_STEPS:
        h = history[t]
        log_lines.append(f"Step {t}:")
        for r, c in h["active_cells"]:
            log_lines.append(f"  ({r:3d}, {c:3d})")
        log_lines.append("")
    log_lines.append("=" * 80)

    TRAJECTORY_LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"Trajectory log saved to: {TRAJECTORY_LOG}")

    # -- Animated GIF generation --
    print(f"\nRendering smooth propagation GIF to {GIF_PATH}...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    # We want to show a complete traversal across the toroidal grid.
    # Since speed is exactly 1 cell/step along the col-axis, a 128-step animation
    # shows the glider moving across the entire grid and returning to its initial position.
    gif_steps = 128
    grid_gif = make_grid()

    frames_gif = [(0, grid_gif.copy())]
    for step in range(1, gif_steps + 1):
        grid_gif = step_grid(grid_gif, lut)
        frames_gif.append((step, grid_gif.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title("Consistency Champion Glider (iter 220)", fontsize=12, fontweight="bold")
    
    img_display = ax.imshow(
        frames_gif[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    txt_display = ax.text(
        0.02, 0.97, f"step={frames_gif[0][0]}", transform=ax.transAxes,
        color="white", fontsize=10, fontweight="bold", va="top",
    )
    ax.axis("off")
    fig.tight_layout()

    def update_gif(i):
        step, g = frames_gif[i]
        img_display.set_data(g)
        txt_display.set_text(f"step={step}")
        return img_display, txt_display

    ani = animation.FuncAnimation(
        fig, update_gif, frames=len(frames_gif), interval=40, blit=True,
    )
    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(GIF_PATH), writer="pillow", fps=25)
    plt.close(fig)
    print(f"GIF successfully rendered and saved to: {GIF_PATH} ({GIF_PATH.stat().st_size/1024:.1f} KB)")
    print("=" * 70)
    print("DONE")

if __name__ == "__main__":
    main()
