#!/usr/bin/env python3
"""
visualize_rule.py

Visualize the dynamics of the Gen-3 champion rule (rule_021) from iter_153.
Generates an animated GIF of 1000 simulation steps.

Steps:
1. Load Gen-3 population from archive/iter_153/results/population_gen3.json
   (already produced by evolve.py --generation 3).
   Provenance: Gen-1 seed=150 -> Gen-2 breeding_seed=152 -> Gen-3 breeding_seed=153.
2. Select rule_021 (composite_fitness=3.465, the champion).
3. Initialise a 150x150 grid with density=0.25, seed=21  (rule index convention).
4. Run 1000 steps, collecting frames every FRAME_STRIDE steps.
5. Save animated GIF to archive/iter_154/results/rule_021_dynamics.gif.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

PROJECT_ROOT = Path(__file__).parent.parent
POP_JSON     = PROJECT_ROOT / "archive" / "iter_153" / "results" / "population_gen3.json"
OUT_DIR      = PROJECT_ROOT / "archive" / "iter_154" / "results"
OUT_GIF      = OUT_DIR / "rule_021_dynamics.gif"

GRID_SIZE    = 150
DENSITY      = 0.25
RULE_SEED    = 21    # same seed as rule index → same initial condition as fitness eval
TOTAL_STEPS  = 1000
FRAME_STRIDE = 5     # capture every N steps
GIF_FPS      = 20


# ── CA helpers (identical to evolve.py) ───────────────────────────────────────

def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def _make_initial_grid(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return (rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Load Gen-3 population ──────────────────────────────────────────────
    print(f"Loading Gen-3 population from {POP_JSON} ...", flush=True)
    with open(POP_JSON) as f:
        pop_data = json.load(f)

    rule_id = "rule_021"
    if rule_id not in pop_data:
        print(f"[error] {rule_id} not found in {POP_JSON}", file=sys.stderr)
        return 1

    rule_dict = pop_data[rule_id]
    lut = _rule_to_lut(rule_dict)
    print(f"  {rule_id}: {len(rule_dict)} rule entries loaded.", flush=True)

    # ── 2. Initialise grid ────────────────────────────────────────────────────
    print(f"\nInitialising {GRID_SIZE}x{GRID_SIZE} grid "
          f"(density={DENSITY}, seed={RULE_SEED}) ...", flush=True)
    grid = _make_initial_grid(RULE_SEED)
    initial_bits = int(grid.sum())
    print(f"  Initial live cells: {initial_bits}", flush=True)

    # ── 3. Run simulation ─────────────────────────────────────────────────────
    print(f"\nRunning {TOTAL_STEPS} steps "
          f"(frame every {FRAME_STRIDE} steps = "
          f"{TOTAL_STEPS // FRAME_STRIDE + 1} frames) ...", flush=True)

    frames    = [grid.copy()]
    com_track = [_center_of_mass(grid)]
    bit_track = [initial_bits]

    for step in range(1, TOTAL_STEPS + 1):
        grid = _step_grid(grid, lut)
        if step % FRAME_STRIDE == 0:
            frames.append(grid.copy())
            com_track.append(_center_of_mass(grid))
            bit_track.append(int(grid.sum()))
        if step % 100 == 0:
            cq, cr = com_track[-1]
            bits   = bit_track[-1]
            print(f"  step {step:4d}: bits={bits:6d}  COM=({cq:.1f},{cr:.1f})",
                  flush=True)

    # ── 4. Displacement analysis ──────────────────────────────────────────────
    com_arr = np.array(com_track)
    step_disps = [
        math.sqrt((com_arr[i, 0] - com_arr[i-1, 0])**2
                  + (com_arr[i, 1] - com_arr[i-1, 1])**2)
        for i in range(1, len(com_arr))
    ]
    total_disp = sum(step_disps)

    # COM displacement over quarter-windows (250 steps = 50 frames)
    window_steps = 250
    window_frames = window_steps // FRAME_STRIDE
    window_disps = []
    for w in range(4):
        i0 = w * window_frames
        i1 = min(i0 + window_frames, len(com_arr) - 1)
        if i0 >= len(com_arr) - 1:
            break
        dq = com_arr[i1, 0] - com_arr[i0, 0]
        dr = com_arr[i1, 1] - com_arr[i0, 1]
        window_disps.append(math.sqrt(dq**2 + dr**2))

    print(f"\n=== Dynamics Summary ===", flush=True)
    print(f"  Initial live cells:    {initial_bits}", flush=True)
    print(f"  Final live cells:      {bit_track[-1]}", flush=True)
    print(f"  Total COM displacement: {total_disp:.4f}", flush=True)
    for i, d in enumerate(window_disps):
        print(f"  Window {i+1} displacement (steps {i*window_steps}–{(i+1)*window_steps}): {d:.4f}",
              flush=True)

    # ── 5. Build animated GIF ─────────────────────────────────────────────────
    print(f"\nBuilding animated GIF ({len(frames)} frames @ {GIF_FPS} fps) ...",
          flush=True)

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    plt.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.08)

    im    = ax.imshow(frames[0], cmap='binary', interpolation='nearest',
                      vmin=0, vmax=1, animated=True)
    ttl   = ax.set_title(
        f'{rule_id}  t=0  bits={bit_track[0]}', fontsize=10)
    ax.set_xlabel('r (col)', fontsize=8)
    ax.set_ylabel('q (row)', fontsize=8)
    ax.tick_params(labelsize=7)

    def _update(i: int):
        step = i * FRAME_STRIDE
        im.set_data(frames[i])
        cq, cr = com_track[i]
        ttl.set_text(
            f'{rule_id}  t={step}  '
            f'bits={bit_track[i]}  '
            f'COM=({cq:.0f},{cr:.0f})')
        return im, ttl

    ani = FuncAnimation(fig, _update, frames=len(frames),
                        interval=int(1000 / GIF_FPS), blit=True)

    writer = PillowWriter(fps=GIF_FPS)
    ani.save(str(OUT_GIF), writer=writer)
    plt.close(fig)

    size_kb = OUT_GIF.stat().st_size / 1024
    print(f"\nSaved: {OUT_GIF}  ({size_kb:.0f} KB)", flush=True)

    # ── 6. Final report ───────────────────────────────────────────────────────
    final_bits   = bit_track[-1]
    bit_ratio    = final_bits / initial_bits if initial_bits > 0 else 0.0
    is_explosive = bit_ratio > 3.0
    is_puffer    = bool(bit_ratio > 1.2 and total_disp > 5.0)
    is_glider    = bool(
        0.8 < bit_ratio < 1.25 and total_disp > 10.0
        and max(step_disps) < 3 * min(d for d in step_disps if d > 0.0)
    )

    print(f"\n=== Classification ===", flush=True)
    print(f"  bit_ratio (final/initial): {bit_ratio:.3f}", flush=True)
    print(f"  is_glider:                 {is_glider}", flush=True)
    print(f"  is_puffer:                 {is_puffer}", flush=True)
    print(f"  is_explosive:              {is_explosive}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
