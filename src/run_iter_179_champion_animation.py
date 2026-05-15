#!/usr/bin/env python3
"""
run_iter_179_champion_animation.py

1. Load archive/iter_179/results/final_population.json
2. Re-evaluate all rules with CheckpointFitness (L-tromino, checkpoints 50/100/150/200,
   200 steps) and select the champion (highest score).
3. Run a 500-step simulation on 128x128 torus with L-tromino seed.
4. Generate and save an animation as archive/iter_179/results/champion_glider.gif.
5. Report net displacement between step 100 and step 500.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
POP_PATH     = PROJECT_ROOT / "archive" / "iter_179" / "results" / "final_population.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_glider.gif"

GRID_SIZE      = 128
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS   = len(LTROMINO_CELLS)
CHECKPOINTS    = {50, 100, 150, 200}
EVAL_STEPS     = 200
SIM_STEPS      = 500

# Animation parameters
FRAME_EVERY    = 5   # record every N steps → 100 frames for 500 steps
FRAME_MS       = 80  # ms per frame
VIEW_PAD       = 20  # cells of padding around the particle in the view window


# ── Simulation primitives ─────────────────────────────────────────────────────

def lut_from_chromosome(chrom: list) -> np.ndarray:
    return np.asarray(chrom, dtype=np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,     1, axis=1)
    nw = np.roll(w,    -1, axis=1)
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


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def checkpoint_fitness(chrom: list) -> float:
    """CheckpointFitness: displacement after EVAL_STEPS, 0 if bit count changes at any checkpoint."""
    lut  = lut_from_chromosome(chrom)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1
    initial_com = center_of_mass(grid)

    for step in range(1, EVAL_STEPS + 1):
        grid = step_grid(grid, lut)
        if step in CHECKPOINTS and int(grid.sum()) != INITIAL_BITS:
            return 0.0

    final_com = center_of_mass(grid)
    dx = final_com[0] - initial_com[0]
    dy = final_com[1] - initial_com[1]
    return math.sqrt(dx * dx + dy * dy)


# ── Torus-aware displacement tracking ────────────────────────────────────────

def unwrap_com(prev_com, curr_com, grid_size=GRID_SIZE):
    """Adjust curr_com for torus wrapping relative to prev_com."""
    pr, pc = prev_com
    cr, cc = curr_com
    half = grid_size / 2.0
    # Adjust row
    dr = cr - pr
    if dr > half:
        cr -= grid_size
    elif dr < -half:
        cr += grid_size
    # Adjust col
    dc = cc - pc
    if dc > half:
        cc -= grid_size
    elif dc < -half:
        cc += grid_size
    return (cr, cc)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # 1. Load population
    with open(POP_PATH) as f:
        pop_data = json.load(f)

    population = pop_data["population"]
    print(f"Loaded {len(population)} rules from {POP_PATH.name}")

    # 2. Re-evaluate all rules with CheckpointFitness and select champion
    print("Re-evaluating all rules with CheckpointFitness ...")
    best_score = -1.0
    best_rule  = None
    for i, entry in enumerate(population):
        score = checkpoint_fitness(entry["chromosome"])
        print(f"  [{i+1:3d}/{len(population)}] rule_id={entry['rule_id']}  "
              f"stored_fitness={entry['fitness']:.4f}  re-score={score:.4f}")
        if score > best_score:
            best_score = score
            best_rule  = entry

    print(f"\nChampion: {best_rule['rule_id']}  fitness={best_score:.4f}")
    lut = lut_from_chromosome(best_rule["chromosome"])

    # 3. Run 500-step simulation, recording frames and COM history
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1

    frames    = []          # (step, grid copy) for every FRAME_EVERY step
    com_hist  = []          # (step, raw_com)
    unwrapped_hist = []     # (step, unwrapped_com)

    prev_raw   = center_of_mass(grid)
    unwrapped  = prev_raw   # cumulative unwrapped position

    com_hist.append((0, prev_raw))
    unwrapped_hist.append((0, unwrapped))
    frames.append((0, grid.copy()))

    for step in range(1, SIM_STEPS + 1):
        grid     = step_grid(grid, lut)
        raw_com  = center_of_mass(grid)

        # Unwrap for displacement tracking
        adj = unwrap_com(prev_raw, raw_com)
        dr  = adj[0] - prev_raw[0]
        dc  = adj[1] - prev_raw[1]
        unwrapped = (unwrapped[0] + dr, unwrapped[1] + dc)

        prev_raw = raw_com
        com_hist.append((step, raw_com))
        unwrapped_hist.append((step, unwrapped))

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            bc = int(grid.sum())
            print(f"  step={step:4d}  bit_count={bc}  raw_com=({raw_com[0]:.2f},{raw_com[1]:.2f})  "
                  f"unwrapped=({unwrapped[0]:.2f},{unwrapped[1]:.2f})")

    # 4. Net displacement step 100 → 500
    uw_100 = next(u for s, u in unwrapped_hist if s == 100)
    uw_500 = next(u for s, u in unwrapped_hist if s == 500)
    dr     = uw_500[0] - uw_100[0]
    dc     = uw_500[1] - uw_100[1]
    net_displacement = math.sqrt(dr * dr + dc * dc)
    print(f"\nNet displacement (step 100 to 500): {net_displacement:.4f} cells")

    # 5. Generate animation
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    print(f"\nGenerating animation ({len(frames)} frames) ...")

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title(f"Champion Glider — {best_rule['rule_id']}  (fitness={best_score:.1f})")
    ax.set_xlabel("col")
    ax.set_ylabel("row")

    # Determine a fixed crop window around the initial position, wide enough
    # to show the full travel without jumping.  We show the full 128x128 grid
    # but highlight the particle with a distinct colour-map.
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
        color="white", fontsize=9, va="top",
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

    print(f"\n=== Summary ===")
    print(f"Champion rule:        {best_rule['rule_id']}")
    print(f"CheckpointFitness:    {best_score:.4f}")
    print(f"Net displacement (100 to 500): {net_displacement:.4f}")
    print(f"GIF:                  {GIF_PATH}")

    return net_displacement, best_score, best_rule["rule_id"]


if __name__ == "__main__":
    nd, fs, rid = main()
    print(f"\nnet_displacement={nd:.6f}")
    sys.exit(0)
