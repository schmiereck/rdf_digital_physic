#!/usr/bin/env python3
"""
Characterize and visualize the iter_197.2 champion.

* Re-evaluate the champion with MassiveGliderFitness (long simulation).
* Report fitness, velocity vector (vx, vy), speed.
* Render a GIF of the glider's first ~500 steps with the seed centred.

Outputs (under archive/iter_197.2/results/):
  - champion_glider.gif       (animated visualisation)
  - champion_characterisation.json  (numeric summary)
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import rule_dict_to_lut, step_grid, center_of_mass
from massive_glider_fitness import (
    MassiveGliderFitness,
    T_TROMINO_PARTICLE,
)

PROJECT_ROOT  = Path(__file__).parent.parent
OUTPUT_DIR    = PROJECT_ROOT / "archive" / "iter_197.2" / "results"
CHAMPION_JSON = OUTPUT_DIR / "champion_rule.json"
GIF_PATH      = OUTPUT_DIR / "champion_glider.gif"
SUMMARY_JSON  = OUTPUT_DIR / "champion_characterisation.json"

GRID_SIZE     = 128
ANIM_STEPS    = 500
FRAME_STRIDE  = 5


def make_grid(particle, grid_size=GRID_SIZE):
    grid   = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in particle:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid


def measure_velocity_long(rule_dict, particle, settle=200, measure=300):
    """Re-measure velocity over a longer window (300 steps) for accuracy."""
    lut = rule_dict_to_lut(rule_dict)
    grid = make_grid(particle)
    for _ in range(settle):
        grid = step_grid(grid, lut)
    com0 = center_of_mass(grid)
    bits0 = int(grid.sum())
    for _ in range(measure):
        grid = step_grid(grid, lut)
    com1 = center_of_mass(grid)
    bits1 = int(grid.sum())
    vr = (com1[0] - com0[0]) / measure
    vc = (com1[1] - com0[1]) / measure
    speed = math.sqrt(vr * vr + vc * vc)
    return {
        "com_t0": com0, "com_t1": com1,
        "bits_t0": bits0, "bits_t1": bits1,
        "vr": vr, "vc": vc, "speed": speed,
    }


def render_gif(rule_dict, particle, gif_path, steps=ANIM_STEPS, stride=FRAME_STRIDE):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut    = rule_dict_to_lut(rule_dict)
    grid   = make_grid(particle)
    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        if step % stride == 0 or step == steps:
            frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_title("iter_197.2  massive-glider champion")
    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    txt = ax.text(
        0.02, 0.97, f"step={frames[0][0]}", transform=ax.transAxes,
        color="white", fontsize=10, va="top",
    )

    def update(i):
        step, g = frames[i]
        img.set_data(g)
        txt.set_text(f"step={step}")
        return img, txt

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=80, blit=True,
    )
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=12)
    plt.close(fig)


def main():
    with open(CHAMPION_JSON) as f:
        champ = json.load(f)
    rule_dict = {int(k): int(v) for k, v in champ["rule"].items()}

    print(f"Champion fitness (from GA): {champ['fitness']:.6f}")
    print(f"Stored metrics            : {champ['metrics']}")

    # Re-run MassiveGliderFitness for full-spec validation
    fit = MassiveGliderFitness()
    m = fit.evaluate(rule_dict)
    print("\n--- Re-evaluation (MassiveGliderFitness) ---")
    for k, v in m.items():
        print(f"  {k}: {v}")

    # Long-window velocity re-measurement
    print("\n--- Long-window velocity (settle=200, measure=300) ---")
    long_v = measure_velocity_long(rule_dict, T_TROMINO_PARTICLE)
    for k, v in long_v.items():
        print(f"  {k}: {v}")

    # Render gif
    print(f"\nRendering GIF -> {GIF_PATH}")
    render_gif(rule_dict, T_TROMINO_PARTICLE, GIF_PATH)
    print(f"GIF saved ({GIF_PATH.stat().st_size/1024:.1f} KB)")

    # Save summary
    summary = {
        "champion_path":         str(CHAMPION_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "ga_fitness":            float(champ["fitness"]),
        "reeval_fitness":        float(m["fitness"]),
        "vx_col":                float(m["vc"]),
        "vy_row":                float(m["vr"]),
        "speed":                 float(m["speed"]),
        "n_valid":               int(m["n_valid"]),
        "n_checked":             int(m["n_checked"]),
        "mean_bit_count":        float(m["mean_bit_count"]),
        "reason":                m["reason"],
        "long_window_vr":        long_v["vr"],
        "long_window_vc":        long_v["vc"],
        "long_window_speed":     long_v["speed"],
        "long_window_bits_t0":   long_v["bits_t0"],
        "long_window_bits_t1":   long_v["bits_t1"],
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved -> {SUMMARY_JSON}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
