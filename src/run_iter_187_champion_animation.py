#!/usr/bin/env python3
"""
run_iter_187_champion_animation.py

Load the best elastic-collision rule from iter_187, run the head-on
two-L-tromino collision for 100 steps, and save an animation GIF.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import rule_dict_to_lut, step_grid
from fitness_functions import (
    CollisionFitness,
    _GLIDER_A,
    _GLIDER_B,
    GRID_SIZE,
    _make_collision_grid,
)


PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_187" / "results" / "best_elastic_rule.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_187" / "results" / "champion_collision.gif"

SIM_STEPS  = 100
FRAME_MS   = 80
FRAME_STEP = 1


def main() -> int:
    with open(RULE_PATH) as f:
        payload = json.load(f)

    rule_dict = {int(k): int(v) for k, v in payload["rule_dict"].items()}
    stored_fitness = float(payload.get("fitness", float("nan")))

    print(f"Loaded champion: stored fitness = {stored_fitness:.6f}")
    print(f"Rule has {len(rule_dict)} active entries.")

    # Re-evaluate to confirm
    fit_metrics = CollisionFitness().evaluate(rule_dict)
    print(
        f"Re-evaluated metrics: fitness={fit_metrics['fitness']:.6f}  "
        f"final_bits={fit_metrics['final_bit_count']}  "
        f"final_objects={fit_metrics['final_object_count']}"
    )

    # Build LUT and seed grid via the fitness module's helpers
    lut  = rule_dict_to_lut(rule_dict)
    grid = _make_collision_grid(GRID_SIZE)

    frames = [(0, grid.copy())]
    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        if step % FRAME_STEP == 0:
            frames.append((step, grid.copy()))

    final_bits = int(grid.sum())
    print(f"Final bit count after {SIM_STEPS} steps: {final_bits}")

    # Animation
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    print(f"Generating animation ({len(frames)} frames) ...")

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title(
        f"iter_187 Champion Collision  fitness={fit_metrics['fitness']:.4f}"
    )
    ax.set_xlabel("col")
    ax.set_ylabel("row")

    img = ax.imshow(
        frames[0][1],
        origin="upper",
        interpolation="nearest",
        cmap="hot",
        vmin=0, vmax=1,
    )
    step_text = ax.text(
        0.02, 0.97, f"step={frames[0][0]}",
        transform=ax.transAxes,
        color="white", fontsize=10, va="top",
    )

    def update(frame_idx):
        step, g = frames[frame_idx]
        img.set_data(g)
        step_text.set_text(f"step={step}")
        return img, step_text

    ani = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=FRAME_MS,
        blit=True,
    )

    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print("\n=== Summary ===")
    print(f"Champion fitness:    {fit_metrics['fitness']:.6f}")
    print(f"Final bit count:     {fit_metrics['final_bit_count']}")
    print(f"Final object count:  {fit_metrics['final_object_count']}")
    print(f"GIF:                 {GIF_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
