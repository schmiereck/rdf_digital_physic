#!/usr/bin/env python3
"""
run_simulation.py — Reproducibility check for the v=1c glider from iter_179.

1. Load champion rule g10_rule_001 from archive/iter_179/results/champion_rule.json
   (falls back to final_population.json if champion_rule.json does not exist,
   and saves the extracted rule as champion_rule.json for future use).
2. Initialize 128x128 hexagonal grid with L-tromino seed at center.
3. Run 400 steps.
4. Verify: displacement ≈ 400 cells, bit count = 3 throughout.
5. Save GIF to archive/iter_181/results/reproducibility_check.gif.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
ITER179_DIR  = PROJECT_ROOT / "archive" / "iter_179" / "results"
ITER181_DIR  = PROJECT_ROOT / "archive" / "iter_181" / "results"
CHAMP_PATH   = ITER179_DIR / "champion_rule.json"
POP_PATH     = ITER179_DIR / "final_population.json"
GIF_PATH     = ITER181_DIR / "reproducibility_check.gif"

GRID_SIZE      = 128
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS   = len(LTROMINO_CELLS)
SIM_STEPS      = 400

FRAME_EVERY = 4   # 100 frames total for 400 steps
FRAME_MS    = 60


# ── Rule loading ──────────────────────────────────────────────────────────────

def load_champion_rule() -> list:
    """Return the 128-element chromosome for g10_rule_001."""
    if CHAMP_PATH.exists():
        print(f"Loading champion rule from {CHAMP_PATH.name}")
        with open(CHAMP_PATH) as f:
            data = json.load(f)
        return data["chromosome"]

    print(f"champion_rule.json not found — extracting g10_rule_001 from final_population.json")
    with open(POP_PATH) as f:
        pop = json.load(f)

    for entry in pop["population"]:
        if entry["rule_id"] == "g10_rule_001":
            champ = {
                "rule_id":    entry["rule_id"],
                "fitness":    entry["fitness"],
                "chromosome": entry["chromosome"],
                "rule_dict":  entry["rule_dict"],
                "source":     str(POP_PATH),
            }
            with open(CHAMP_PATH, "w") as f:
                json.dump(champ, f, indent=2)
            print(f"Saved champion_rule.json  (fitness={entry['fitness']})")
            return entry["chromosome"]

    raise RuntimeError("g10_rule_001 not found in final_population.json")


# ── Simulation primitives ─────────────────────────────────────────────────────

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


def unwrap_com(prev_com: tuple, curr_com: tuple, size: int = GRID_SIZE) -> tuple:
    """Adjust curr_com for torus wrapping relative to prev_com."""
    pr, pc = prev_com
    cr, cc = curr_com
    half = size / 2.0
    dr = cr - pr
    if dr > half:
        cr -= size
    elif dr < -half:
        cr += size
    dc = cc - pc
    if dc > half:
        cc -= size
    elif dc < -half:
        cc += size
    return (cr, cc)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=== iter_181 Reproducibility Check — v=1c glider from iter_179 ===")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}  Seed: L-tromino at {LTROMINO_CELLS}")
    print(f"Steps: {SIM_STEPS}\n")

    # 1. Load rule
    chrom = load_champion_rule()
    lut   = np.asarray(chrom, dtype=np.uint8)
    print(f"LUT loaded ({len(lut)} entries)  non-zero: {int(lut.sum())}\n")

    # 2. Initialize grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1

    initial_com = center_of_mass(grid)
    prev_raw    = initial_com
    unwrapped   = initial_com

    frames     = [(0, grid.copy())]
    bit_error  = False

    # 3. Run simulation
    print(f"{'step':>6}  {'bit_count':>9}  {'raw_com':>22}  {'unwrapped':>26}  {'disp':>8}")
    print("-" * 80)

    for step in range(1, SIM_STEPS + 1):
        grid    = step_grid(grid, lut)
        raw_com = center_of_mass(grid)

        # Torus-unwrap cumulative displacement
        adj      = unwrap_com(prev_raw, raw_com)
        dr       = adj[0] - prev_raw[0]
        dc       = adj[1] - prev_raw[1]
        unwrapped = (unwrapped[0] + dr, unwrapped[1] + dc)
        prev_raw  = raw_com

        bc = int(grid.sum())
        if bc != INITIAL_BITS:
            bit_error = True

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            ddx = unwrapped[0] - initial_com[0]
            ddy = unwrapped[1] - initial_com[1]
            disp = math.sqrt(ddx * ddx + ddy * ddy)
            print(f"{step:>6}  {bc:>9}  "
                  f"({raw_com[0]:8.2f},{raw_com[1]:8.2f})  "
                  f"({unwrapped[0]:10.2f},{unwrapped[1]:10.2f})  "
                  f"{disp:8.3f}")

    # 4. Final metrics
    ddx           = unwrapped[0] - initial_com[0]
    ddy           = unwrapped[1] - initial_com[1]
    displacement  = math.sqrt(ddx * ddx + ddy * ddy)
    final_bc      = int(grid.sum())

    print()
    print(f"Final bit count:       {final_bc}")
    print(f"Bit count error:       {bit_error}")
    print(f"Final displacement:    {displacement:.4f} cells  (expected ~400 for v=1c)")
    print(f"Displacement per step: {displacement / SIM_STEPS:.4f}  (expected ~1.0)")
    glider_ok = (not bit_error) and (final_bc == INITIAL_BITS) and (displacement > 390)
    print(f"Glider verified:       {glider_ok}")

    # 5. Save GIF
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    ITER181_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating animation ({len(frames)} frames) -> {GIF_PATH.name}")

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.set_title(f"iter_179 glider — g10_rule_001 — {SIM_STEPS} steps")
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
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print(f"\n=== Summary ===")
    print(f"  displacement:    {displacement:.6f}")
    print(f"  disp_per_step:   {displacement / SIM_STEPS:.6f}")
    print(f"  final_bit_count: {final_bc}")
    print(f"  bit_error:       {bit_error}")
    print(f"  glider_verified: {glider_ok}")

    return 0 if glider_ok else 1


if __name__ == "__main__":
    sys.exit(main())
