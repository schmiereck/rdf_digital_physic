#!/usr/bin/env python3
"""
run_iter_171_viz.py  —  1000-step simulation + visualization of Gen-3 top rule

Loads the best rule from archive/iter_171/results/gen3_population/top_rule.json,
runs it for 1000 steps, and saves:
  - a GIF animation of the grid state
  - a time-series plot of displacement and bit count
"""

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

sys.path.insert(0, str(Path(__file__).parent))

from evolution import (
    LTROMINO_CELLS,
    GRID_SIZE,
    make_ltromino_grid,
    rule_dict_to_lut,
    step_grid,
    center_of_mass,
)

PROJECT_ROOT = Path(__file__).parent.parent
TOP_RULE_PATH = PROJECT_ROOT / "archive" / "iter_171" / "results" / "gen3_population" / "top_rule.json"
OUTPUT_DIR    = PROJECT_ROOT / "archive" / "iter_171" / "results" / "visualization"

STEPS       = 1000
RECORD_EVERY = 5   # record frame every N steps -> 200 frames total
GIF_FPS     = 15

# Zoom window around the particle (cells)
WINDOW_HALF = 40


def run_simulation(rule_dict: dict, steps: int):
    """Run simulation and record grid snapshots + metrics."""
    lut   = rule_dict_to_lut(rule_dict)
    grid  = make_ltromino_grid()
    com0  = center_of_mass(grid)

    frames      = []
    com_x       = []
    com_y       = []
    bit_counts  = []
    displacements = []

    com_cur = com0
    for t in range(steps + 1):
        com_cur = center_of_mass(grid)
        bits    = int(grid.sum())
        dx      = com_cur[0] - com0[0]
        dy      = com_cur[1] - com0[1]
        disp    = math.sqrt(dx * dx + dy * dy)

        com_x.append(com_cur[0])
        com_y.append(com_cur[1])
        bit_counts.append(bits)
        displacements.append(disp)

        if t % RECORD_EVERY == 0:
            frames.append(grid.copy())

        if t < steps:
            grid = step_grid(grid, lut)

    return frames, com_x, com_y, bit_counts, displacements, com0


def build_gif(frames, com_x_all, com_y_all, output_path: Path):
    """Build a GIF animation with a zoomed view centred on the particle."""
    n_frames = len(frames)
    frame_steps = [i * RECORD_EVERY for i in range(n_frames)]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0)

    # Infer zoom centre trajectory from recorded COM
    com_x_rec = [com_x_all[t] for t in frame_steps]
    com_y_rec = [com_y_all[t] for t in frame_steps]

    im = ax.imshow(
        np.zeros((2 * WINDOW_HALF, 2 * WINDOW_HALF), dtype=np.float32),
        cmap="binary",
        vmin=0, vmax=1,
        origin="lower",
        interpolation="nearest",
    )
    title = ax.set_title("t=0", fontsize=9)

    def update(i):
        grid = frames[i]
        cx = int(round(com_x_rec[i]))
        cy = int(round(com_y_rec[i]))
        # Clamp window
        r0 = max(0, cx - WINDOW_HALF)
        r1 = min(GRID_SIZE, cx + WINDOW_HALF)
        c0 = max(0, cy - WINDOW_HALF)
        c1 = min(GRID_SIZE, cy + WINDOW_HALF)
        crop = grid[r0:r1, c0:c1].astype(np.float32)
        im.set_data(crop.T)
        im.set_extent([c0, c1, r0, r1])
        ax.set_xlim(c0, c1)
        ax.set_ylim(r0, r1)
        title.set_text(f"t={frame_steps[i]}")
        return im, title

    anim = FuncAnimation(fig, update, frames=n_frames, blit=True, interval=1000 // GIF_FPS)
    writer = PillowWriter(fps=GIF_FPS)
    anim.save(str(output_path), writer=writer)
    plt.close(fig)
    print(f"  Saved GIF: {output_path}")


def plot_timeseries(bit_counts, displacements, output_path: Path):
    """Plot bit count and displacement over 1000 steps."""
    steps_arr = np.arange(len(bit_counts))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax1.plot(steps_arr, bit_counts, color="steelblue", linewidth=0.8)
    ax1.set_ylabel("Bit Count")
    ax1.set_title("Particle Bit Count over 1000 Steps (Gen-3 Top Rule)")
    ax1.grid(True, alpha=0.3)
    ax1.axhline(bit_counts[0], color="grey", linestyle="--", linewidth=0.6, label=f"t=0: {bit_counts[0]}")
    ax1.legend(fontsize=8)

    ax2.plot(steps_arr, displacements, color="darkorange", linewidth=0.8)
    ax2.set_ylabel("Displacement (cells)")
    ax2.set_xlabel("Step")
    ax2.set_title("Centre-of-Mass Displacement over 1000 Steps")
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(str(output_path), dpi=120)
    plt.close(fig)
    print(f"  Saved plot: {output_path}")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading top rule from {TOP_RULE_PATH}")
    with open(TOP_RULE_PATH) as f:
        top_rule_data = json.load(f)

    rule_id   = top_rule_data["rule_id"]
    rule_dict = {int(k): int(v) for k, v in top_rule_data["rule"].items()}

    print(f"Rule: {rule_id}")
    print(f"  Fitness (200-step): {top_rule_data['fitness']:.4f}")
    print(f"  Displacement:       {top_rule_data['displacement']:.4f}")
    print(f"  Final bit count:    {top_rule_data['final_bit_count']}")
    print(f"\nRunning {STEPS}-step simulation on {GRID_SIZE}x{GRID_SIZE} grid ...")

    frames, com_x, com_y, bit_counts, displacements, com0 = run_simulation(rule_dict, STEPS)

    print(f"  Done. Frames recorded: {len(frames)}")
    print(f"  Initial COM:   ({com0[0]:.2f}, {com0[1]:.2f})")
    print(f"  Final COM:     ({com_x[-1]:.2f}, {com_y[-1]:.2f})")
    print(f"  Final bits:    {bit_counts[-1]}")
    print(f"  Max disp:      {max(displacements):.4f}")
    print(f"  Final disp:    {displacements[-1]:.4f}")
    print(f"  Min bit count: {min(bit_counts)}")
    print(f"  Max bit count: {max(bit_counts)}")

    # Motion stability checks
    disp_last100 = displacements[900:]
    disp_delta   = max(disp_last100) - min(disp_last100)
    bits_last100 = bit_counts[900:]
    bits_mean    = float(np.mean(bits_last100))
    bits_std     = float(np.std(bits_last100))
    print(f"  Steps 900-1000 disp range: {disp_delta:.4f}")
    print(f"  Steps 900-1000 bits mean:  {bits_mean:.1f} ± {bits_std:.1f}")

    gif_path  = OUTPUT_DIR / "simulation.gif"
    plot_path = OUTPUT_DIR / "timeseries.png"

    print(f"\nGenerating GIF ({len(frames)} frames @ {GIF_FPS} fps) ...")
    build_gif(frames, com_x, com_y, gif_path)

    print("Generating time-series plot ...")
    plot_timeseries(bit_counts, displacements, plot_path)

    # Save summary JSON
    summary = {
        "rule_id":          rule_id,
        "steps":            STEPS,
        "initial_com":      [round(com0[0], 4), round(com0[1], 4)],
        "final_com":        [round(com_x[-1], 4), round(com_y[-1], 4)],
        "initial_bits":     bit_counts[0],
        "final_bits":       bit_counts[-1],
        "max_bits":         max(bit_counts),
        "min_bits":         min(bit_counts),
        "final_displacement": round(displacements[-1], 6),
        "max_displacement":   round(max(displacements), 6),
        "late_disp_range":    round(disp_delta, 6),
        "late_bits_mean":     round(bits_mean, 2),
        "late_bits_std":      round(bits_std, 2),
    }
    summary_path = OUTPUT_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved summary: {summary_path}")

    print("\n=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
