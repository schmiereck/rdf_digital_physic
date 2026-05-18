#!/usr/bin/env python3
"""
run_iter_216_1_characterize.py

Characterize the iter_215 champion glider on a 256x256 toroidal grid:
  - 2000 simulation steps
  - Track centre-of-mass (CoM) at every step with toroidal unwrapping
  - Determine velocity vector (cells/step) via linear regression
  - Detect shape period (exact) or estimate from velocity
  - Write JSON summary and 500-step GIF animation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evolution import rule_dict_to_lut, step_grid

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_215" / "results" / "champion_rule.json"
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_216" / "results"

# ── Constants ──────────────────────────────────────────────────────────────────
GRID_SIZE  = 256
NUM_STEPS  = 2000
ANIM_STEPS = 500
LTROMINO   = [(0, 0), (0, 1), (1, 1)]   # (dr, dc) offsets from grid centre
ZOOM       = 32                           # half-size of zoom window for animation


# ── Grid / CoM helpers ─────────────────────────────────────────────────────────

def make_particle_grid(offsets: list = LTROMINO, grid_size: int = GRID_SIZE) -> np.ndarray:
    grid   = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in offsets:
        grid[(centre + dr) % grid_size, (centre + dc) % grid_size] = 1
    return grid


def torus_com(grid: np.ndarray, grid_size: int) -> tuple[float, float]:
    """Circular-mean CoM; handles particles that straddle the toroidal boundary."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0)
    twopi = 2.0 * np.pi
    angles_r = twopi * rows.astype(float) / grid_size
    com_r = (np.arctan2(np.sin(angles_r).mean(), np.cos(angles_r).mean()) % twopi) * grid_size / twopi
    angles_c = twopi * cols.astype(float) / grid_size
    com_c = (np.arctan2(np.sin(angles_c).mean(), np.cos(angles_c).mean()) % twopi) * grid_size / twopi
    return (float(com_r), float(com_c))


def get_shape_key(grid: np.ndarray, grid_size: int) -> frozenset:
    """Canonical (rotation-free) shape: sorted relative offsets from the first live cell."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return frozenset()
    idx = np.argsort(rows * grid_size + cols)
    rows, cols = rows[idx], cols[idx]
    r0, c0 = int(rows[0]), int(cols[0])
    half = grid_size // 2
    return frozenset(
        (int((int(r) - r0 + half) % grid_size - half),
         int((int(c) - c0 + half) % grid_size - half))
        for r, c in zip(rows, cols)
    )


# ── Animation helper ───────────────────────────────────────────────────────────

def render_frame(cells: list, com: tuple, grid_size: int, zoom: int = ZOOM) -> np.ndarray:
    """64×64 binary image centred on *com* with live cells marked."""
    r_c = int(round(com[0])) % grid_size
    c_c = int(round(com[1])) % grid_size
    size  = 2 * zoom
    frame = np.zeros((size, size), dtype=np.float32)
    half  = grid_size // 2
    for r, c in cells:
        dr = (int(r) - r_c + half) % grid_size - half
        dc = (int(c) - c_c + half) % grid_size - half
        if -zoom <= dr < zoom and -zoom <= dc < zoom:
            frame[dr + zoom, dc + zoom] = 1.0
    return frame


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load champion rule
    with open(CHAMP_PATH) as f:
        champ = json.load(f)
    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut       = rule_dict_to_lut(rule_dict)
    print(f"Champion rule: {len(rule_dict)} custom LUT entries  (fitness={champ['fitness']})")

    # Initialise grid
    grid          = make_particle_grid()
    initial_bits  = int(grid.sum())
    initial_shape = get_shape_key(grid, GRID_SIZE)
    print(f"Grid: {GRID_SIZE}×{GRID_SIZE}  Steps: {NUM_STEPS}  Seed bits: {initial_bits}")

    # ── Simulation loop ────────────────────────────────────────────────────────
    prev_circ      = np.array(torus_com(grid, GRID_SIZE))
    unwrapped_com  = prev_circ.copy()
    com_raw_hist   = [prev_circ.tolist()]
    com_unw_hist   = [unwrapped_com.tolist()]
    shape_hist     = [initial_shape]

    # Store cell positions for first ANIM_STEPS+1 frames only
    rows0, cols0 = np.where(grid > 0)
    anim_cells   = [list(zip(rows0.tolist(), cols0.tolist()))]

    period         = None
    bit_fail_step  = None

    for step in range(NUM_STEPS):
        grid = step_grid(grid, lut)
        bits = int(grid.sum())

        if bits != initial_bits and bit_fail_step is None:
            bit_fail_step = step + 1
            print(f"  WARNING: bit count changed to {bits} at step {step + 1}")

        # Incremental toroidal-unwrapped CoM
        curr_circ = np.array(torus_com(grid, GRID_SIZE))
        delta     = curr_circ - prev_circ
        for dim in range(2):
            if delta[dim] >  GRID_SIZE / 2:
                delta[dim] -= GRID_SIZE
            elif delta[dim] < -GRID_SIZE / 2:
                delta[dim] += GRID_SIZE
        unwrapped_com = unwrapped_com + delta
        prev_circ     = curr_circ
        com_raw_hist.append(curr_circ.tolist())
        com_unw_hist.append(unwrapped_com.tolist())

        # Shape for period detection
        shp = get_shape_key(grid, GRID_SIZE)
        shape_hist.append(shp)
        if period is None and step > 0 and shp == initial_shape:
            period = step + 1
            print(f"  Exact period found: {period} steps  (at step {step + 1})")

        # Collect animation frames
        if step < ANIM_STEPS:
            rs, cs = np.where(grid > 0)
            anim_cells.append(list(zip(rs.tolist(), cs.tolist())))

        if (step + 1) % 500 == 0:
            print(f"  Step {step+1:4d}: CoM(unwrapped)=({unwrapped_com[0]:.4f}, {unwrapped_com[1]:.4f})"
                  f"  bits={bits}")

    final_bits = int(grid.sum())
    print(f"\nSimulation done.  Final bits: {final_bits}  Bit-conserved: {final_bits == initial_bits}")

    # ── Velocity ───────────────────────────────────────────────────────────────
    com_arr   = np.array(com_unw_hist)          # shape (2001, 2)
    steps_arr = np.arange(len(com_arr))
    coeff_r   = np.polyfit(steps_arr, com_arr[:, 0], 1)
    coeff_c   = np.polyfit(steps_arr, com_arr[:, 1], 1)
    v_r       = float(coeff_r[0])
    v_c       = float(coeff_c[0])
    speed     = float(np.sqrt(v_r**2 + v_c**2))

    print(f"\nVelocity  : v_r={v_r:.8f}  v_c={v_c:.8f}  |v|={speed:.8f} cells/step")

    # ── Period estimation ──────────────────────────────────────────────────────
    period_estimated = False
    if period is None:
        from fractions import Fraction
        # Use dominant non-zero component
        dominant_v = v_r if abs(v_r) >= abs(v_c) else v_c
        if abs(dominant_v) > 1e-10:
            frac = Fraction(dominant_v).limit_denominator(500)
            period = frac.denominator
            period_estimated = True
            print(f"Period estimated from v={frac} ({float(frac):.8f}): {period} steps")
        else:
            print("Period: indeterminate (velocity ≈ 0)")
    else:
        print(f"Period exact: {period} steps")

    # ── Final displacement ─────────────────────────────────────────────────────
    disp_r   = float(com_arr[-1, 0] - com_arr[0, 0])
    disp_c   = float(com_arr[-1, 1] - com_arr[0, 1])
    disp_mag = float(np.sqrt(disp_r**2 + disp_c**2))
    print(f"Displacement over {NUM_STEPS} steps: ({disp_r:.4f}, {disp_c:.4f})  magnitude={disp_mag:.4f}")

    # ── Save characterization JSON ─────────────────────────────────────────────
    result = {
        "rule_source":            "archive/iter_215/results/champion_rule.json",
        "grid_size":              GRID_SIZE,
        "num_steps":              NUM_STEPS,
        "seed":                   "3-bit L-tromino",
        "seed_offsets":           LTROMINO,
        "velocity_cells_per_step": {
            "row":   round(v_r, 8),
            "col":   round(v_c, 8),
            "speed": round(speed, 8),
        },
        "period_steps":       period,
        "period_is_estimated": period_estimated,
        "final_displacement": {
            "row":       round(disp_r, 4),
            "col":       round(disp_c, 4),
            "magnitude": round(disp_mag, 4),
        },
        "initial_bits":   initial_bits,
        "final_bits":     final_bits,
        "bit_conserved":  bool(final_bits == initial_bits),
        "bit_fail_step":  bit_fail_step,
    }

    json_path = OUTPUT_DIR / "characterization.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {json_path}")

    # ── CoM trajectory plot ────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.plot(steps_arr, com_arr[:, 0], lw=0.5, alpha=0.7, label="row (unwrapped)")
    ax1.plot(steps_arr, coeff_r[0] * steps_arr + coeff_r[1],
             "--", lw=1.5, color="red", label=f"fit: v_r={v_r:.6f}")
    ax1.set_xlabel("Step"); ax1.set_ylabel("Row (cells)")
    ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

    ax2.plot(steps_arr, com_arr[:, 1], lw=0.5, alpha=0.7, color="orange", label="col (unwrapped)")
    ax2.plot(steps_arr, coeff_c[0] * steps_arr + coeff_c[1],
             "--", lw=1.5, color="red", label=f"fit: v_c={v_c:.6f}")
    ax2.set_xlabel("Step"); ax2.set_ylabel("Col (cells)")
    ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)

    fig.suptitle(f"iter_215 Champion Glider — v=({v_r:.5f}, {v_c:.5f}) cells/step  period={period}")
    fig.tight_layout()
    plot_path = OUTPUT_DIR / "com_trajectory.png"
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"Saved: {plot_path}")

    # ── GIF animation ──────────────────────────────────────────────────────────
    print(f"Generating GIF ({ANIM_STEPS + 1} frames)…")
    fig_g, ax_g = plt.subplots(figsize=(4, 4), dpi=80)
    fig_g.subplots_adjust(0, 0, 1, 1)
    ax_g.set_axis_off()

    frame0 = render_frame(anim_cells[0], com_raw_hist[0], GRID_SIZE)
    im  = ax_g.imshow(frame0, cmap="binary", vmin=0, vmax=1,
                      interpolation="nearest", origin="upper")
    txt = ax_g.text(0.02, 0.97, "Step 0", transform=ax_g.transAxes,
                    color="red", fontsize=7, va="top",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6))

    def _update(i: int):
        fr  = render_frame(anim_cells[i], com_raw_hist[i], GRID_SIZE)
        im.set_data(fr)
        com = com_raw_hist[i]
        txt.set_text(f"Step {i}  ({com[0]:.1f}, {com[1]:.1f})")
        return [im, txt]

    anim     = FuncAnimation(fig_g, _update, frames=ANIM_STEPS + 1, interval=50, blit=True)
    gif_path = OUTPUT_DIR / "vc_glider_trajectory.gif"
    anim.save(str(gif_path), writer=PillowWriter(fps=20))
    plt.close(fig_g)
    print(f"Saved: {gif_path}")

    return result


if __name__ == "__main__":
    res = main()
    print("\n=== Characterization Results ===")
    print(json.dumps(res, indent=2))
