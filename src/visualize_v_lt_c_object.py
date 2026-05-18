#!/usr/bin/env python3
"""
visualize_v_lt_c_object.py

Visualize the period-4 oscillator produced by the iter_200 champion rule.
Runs 16 steps (four full cycles) and saves a zoomed GIF animation.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evolution import rule_dict_to_lut, step_grid

PROJECT_ROOT = Path(__file__).parent.parent
GRID_SIZE = 128
STEPS = 16
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]

# Zoom window: 10x10 cells centred on the oscillator (cells live in rows 63-65, cols 63-64)
ZOOM_ROW_MIN = 60
ZOOM_ROW_MAX = 70
ZOOM_COL_MIN = 60
ZOOM_COL_MAX = 70


def load_rule() -> dict:
    base = PROJECT_ROOT / "archive"
    candidates = [
        base / "iter_200" / "results" / "champion_v_lt_c_rule.json",
        base / "iter_200.1" / "results" / "champion_v_lt_c_rule.json",
        base / "iter_200" / "results" / "champion_vc_rule.json",
    ]
    for p in candidates:
        if p.exists():
            print(f"Loaded rule from: {p}")
            with open(p) as f:
                return json.load(f)
    print("ERROR: champion rule JSON not found", file=sys.stderr)
    sys.exit(1)


def make_grid() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


def main() -> int:
    rule_data = load_rule()
    rule_dict = {int(k): int(v) for k, v in rule_data["rule_dict"].items()}
    fitness = rule_data.get("fitness", float("nan"))
    print(f"Rule mappings: {len(rule_dict)},  stored fitness: {fitness:.6f}")

    lut = rule_dict_to_lut(rule_dict)

    grid = make_grid()
    frames = [grid.copy()]
    for _ in range(STEPS):
        grid = step_grid(grid, lut)
        frames.append(grid.copy())

    print(f"Simulated {STEPS} steps ({len(frames)} frames).")

    # Zoom each frame
    zoomed = [f[ZOOM_ROW_MIN:ZOOM_ROW_MAX, ZOOM_COL_MIN:ZOOM_COL_MAX] for f in frames]

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    ax.set_title("iter_200 champion: period-4 oscillator", fontsize=11)
    ax.set_xlabel("col")
    ax.set_ylabel("row")

    img = ax.imshow(
        zoomed[0],
        origin="upper",
        interpolation="nearest",
        cmap="binary",
        vmin=0, vmax=1,
        extent=[ZOOM_COL_MIN, ZOOM_COL_MAX, ZOOM_ROW_MAX, ZOOM_ROW_MIN],
    )
    step_text = ax.text(
        0.02, 0.97, "step=0  (phase 0)",
        transform=ax.transAxes,
        color="black", fontsize=9, va="top",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7),
    )

    def update(i):
        img.set_data(zoomed[i])
        step_text.set_text(f"step={i}  (phase {i % 4})")
        return img, step_text

    ani = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=250,
        blit=True,
    )

    out_dir = PROJECT_ROOT / "archive" / "iter_201" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "oscillator.gif"
    ani.save(str(out_path), writer="pillow", fps=4)
    plt.close(fig)
    print(f"Saved: {out_path}")

    # Print the four distinct states
    print("\nOscillator phases (bit counts and active cells):")
    for phase in range(4):
        f = frames[phase]
        rows, cols = np.where(f > 0)
        bits = int(f.sum())
        cells = sorted(zip(rows.tolist(), cols.tolist()))
        print(f"  phase {phase}: bits={bits}, cells={cells}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
