#!/usr/bin/env python3
"""
run_iter_188_head_on_collision.py

Visualize the iter_187.2 champion rule running the head-on two-L-tromino
collision for 400 steps on a 128x128 toroidal grid.

Saves: archive/iter_188/results/head_on_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import rule_dict_to_lut, step_grid
from fitness_functions import _GLIDER_A, _GLIDER_B, GRID_SIZE, _make_collision_grid

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_188" / "results"

# Try champion_rule.json first (as the task specifies), fall back to best_elastic_rule.json
RULE_PATH_PRIMARY  = PROJECT_ROOT / "archive" / "iter_187" / "results" / "champion_rule.json"
RULE_PATH_FALLBACK = PROJECT_ROOT / "archive" / "iter_187" / "results" / "best_elastic_rule.json"
GIF_PATH = RESULTS_DIR / "head_on_collision.gif"

SIM_STEPS  = 400
FRAME_STEP = 2       # record every Nth step to keep GIF size reasonable
FRAME_MS   = 60      # ms between frames


def load_rule() -> tuple[dict, Path]:
    if RULE_PATH_PRIMARY.exists():
        path = RULE_PATH_PRIMARY
    else:
        path = RULE_PATH_FALLBACK
    with open(path) as f:
        payload = json.load(f)
    rule_dict = {int(k): int(v) for k, v in payload["rule_dict"].items()}
    return rule_dict, path


def compute_center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (float("nan"), float("nan"))
    return float(np.mean(rows)), float(np.mean(cols))


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_dict, rule_path = load_rule()
    print(f"Loaded rule from: {rule_path}")
    print(f"Rule entries: {len(rule_dict)}")
    print(f"Rule dict: {rule_dict}")

    lut  = rule_dict_to_lut(rule_dict)
    grid = _make_collision_grid(GRID_SIZE)

    initial_bits = int(grid.sum())
    initial_com  = compute_center_of_mass(grid)
    print(f"Initial bits: {initial_bits}, initial CoM: {initial_com}")
    print(f"Glider A cells: {_GLIDER_A}")
    print(f"Glider B cells: {_GLIDER_B}")

    frames: list[tuple[int, np.ndarray]] = [(0, grid.copy())]

    # Track CoM over time to detect motion
    com_history = [initial_com]
    bit_history = [initial_bits]

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bits = int(grid.sum())
        com  = compute_center_of_mass(grid)
        bit_history.append(bits)
        com_history.append(com)
        if step % FRAME_STEP == 0:
            frames.append((step, grid.copy()))

    final_bits = bit_history[-1]
    final_com  = com_history[-1]
    print(f"\nFinal bit count:  {final_bits}")
    print(f"Final CoM:        {final_com}")

    # Diagnostic: report bit counts at key checkpoints
    for checkpoint in [50, 100, 150, 200, 300, 400]:
        if checkpoint <= SIM_STEPS:
            print(f"  step {checkpoint:3d}: bits={bit_history[checkpoint]}, "
                  f"CoM=({com_history[checkpoint][0]:.2f}, {com_history[checkpoint][1]:.2f})")

    # Check if CoM moved significantly (motion indicator)
    r0, c0 = initial_com
    r_final, c_final = final_com
    dr = r_final - r0
    dc = c_final - c0
    print(f"\nCoM displacement (dr={dr:.3f}, dc={dc:.3f})")

    # Check if bits are conserved throughout
    min_bits = min(bit_history)
    max_bits = max(bit_history)
    print(f"Bit range over simulation: min={min_bits}, max={max_bits}")

    # ── Animation ─────────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    print(f"\nGenerating animation ({len(frames)} frames) ...")

    # Zoom in on the collision region: rows 30-100, cols 50-80
    ROW_LO, ROW_HI = 30, 100
    COL_LO, COL_HI = 50, 80

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=100)

    ax_full = axes[0]
    ax_zoom = axes[1]

    ax_full.set_title("Full grid (128×128)")
    ax_full.set_xlabel("col")
    ax_full.set_ylabel("row")

    ax_zoom.set_title("Collision region (zoom)")
    ax_zoom.set_xlabel("col")
    ax_zoom.set_ylabel("row")

    img_full = ax_full.imshow(
        frames[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    img_zoom = ax_zoom.imshow(
        frames[0][1][ROW_LO:ROW_HI, COL_LO:COL_HI],
        origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    ax_zoom.set_xlim(-0.5, (COL_HI - COL_LO) - 0.5)
    ax_zoom.set_ylim((ROW_HI - ROW_LO) - 0.5, -0.5)

    step_text = fig.suptitle(
        f"iter_187 Champion — step=0  bits={initial_bits}",
        fontsize=11,
    )

    def update(frame_idx):
        step, g = frames[frame_idx]
        bits = bit_history[step]
        img_full.set_data(g)
        img_zoom.set_data(g[ROW_LO:ROW_HI, COL_LO:COL_HI])
        step_text.set_text(
            f"iter_187 Champion — step={step}  bits={bits}"
        )
        return img_full, img_zoom, step_text

    ani = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=FRAME_MS,
        blit=True,
    )

    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print("\n=== Summary ===")
    print(f"Rule file:         {rule_path.name}")
    print(f"Initial bits:      {initial_bits}")
    print(f"Final bits:        {final_bits}")
    print(f"Bit conservation:  {'perfect' if min_bits == max_bits == initial_bits else 'imperfect'}")
    print(f"CoM displacement:  dr={dr:.3f}, dc={dc:.3f}")
    print(f"GIF:               {GIF_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
