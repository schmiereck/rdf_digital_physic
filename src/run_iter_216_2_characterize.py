#!/usr/bin/env python3
"""
run_iter_216_2_characterize.py

500-step characterization of the iter_215 champion glider.
Logs bit count and centre-of-mass at every step.
Calculates displacement and velocity over the window [250, 500].
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_215" / "results" / "champion_rule.json"
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_216" / "results"

GRID_SIZE  = 256
NUM_STEPS  = 500
LTROMINO   = [(0, 0), (0, 1), (1, 1)]


def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


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


def torus_com(grid: np.ndarray) -> tuple[float, float]:
    """Circular-mean CoM; handles particles straddling toroidal boundary."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0)
    twopi = 2.0 * np.pi
    angles_r = twopi * rows.astype(float) / GRID_SIZE
    com_r = (np.arctan2(np.sin(angles_r).mean(), np.cos(angles_r).mean()) % twopi) * GRID_SIZE / twopi
    angles_c = twopi * cols.astype(float) / GRID_SIZE
    com_c = (np.arctan2(np.sin(angles_c).mean(), np.cos(angles_c).mean()) % twopi) * GRID_SIZE / twopi
    return (float(com_r), float(com_c))


def main() -> int:
    t0 = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CHAMP_PATH) as f:
        champ = json.load(f)
    rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
    lut       = rule_dict_to_lut(rule_dict)
    print(f"Champion rule: {len(rule_dict)} custom LUT entries  fitness={champ['fitness']}")

    # Initialise grid — L-tromino at grid centre
    grid   = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    centre = GRID_SIZE // 2
    for dr, dc in LTROMINO:
        grid[(centre + dr) % GRID_SIZE, (centre + dc) % GRID_SIZE] = 1

    initial_bits = int(grid.sum())
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}  Steps: {NUM_STEPS}  Seed bits: {initial_bits}")
    print(f"Seed offsets: {LTROMINO}  placed at centre={centre}")

    # Per-step log
    step_log = []

    # Toroidal unwrapped CoM tracking
    prev_circ     = np.array(torus_com(grid))
    unwrapped_com = prev_circ.copy()

    # Step 0
    step_log.append({
        "step":      0,
        "bit_count": initial_bits,
        "com_raw":   list(prev_circ),
        "com_unwrapped": list(unwrapped_com),
    })

    for step in range(NUM_STEPS):
        grid = step_grid(grid, lut)
        bits = int(grid.sum())

        curr_circ = np.array(torus_com(grid))
        delta     = curr_circ - prev_circ
        for dim in range(2):
            if delta[dim] >  GRID_SIZE / 2:
                delta[dim] -= GRID_SIZE
            elif delta[dim] < -GRID_SIZE / 2:
                delta[dim] += GRID_SIZE
        unwrapped_com = unwrapped_com + delta
        prev_circ     = curr_circ

        step_log.append({
            "step":          step + 1,
            "bit_count":     bits,
            "com_raw":       [round(float(curr_circ[0]), 6), round(float(curr_circ[1]), 6)],
            "com_unwrapped": [round(float(unwrapped_com[0]), 6), round(float(unwrapped_com[1]), 6)],
        })

        if (step + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  Step {step+1:4d}: bits={bits}  "
                  f"CoM_unw=({unwrapped_com[0]:.3f}, {unwrapped_com[1]:.3f})  "
                  f"elapsed={elapsed:.2f}s")

    final_bits = int(grid.sum())
    elapsed    = time.time() - t0

    # Metrics
    com_250 = step_log[250]["com_unwrapped"]
    com_500 = step_log[500]["com_unwrapped"]
    disp_r  = com_500[0] - com_250[0]
    disp_c  = com_500[1] - com_250[1]
    disp_mag = float(np.sqrt(disp_r**2 + disp_c**2))
    window   = 250  # steps 250 → 500
    vel_r    = disp_r / window
    vel_c    = disp_c / window
    vel_mag  = disp_mag / window

    print(f"\nSimulation done in {elapsed:.2f}s")
    print(f"Initial bits: {initial_bits}  Final bits: {final_bits}  "
          f"Conserved: {initial_bits == final_bits}")
    print(f"CoM at step 250: ({com_250[0]:.4f}, {com_250[1]:.4f})")
    print(f"CoM at step 500: ({com_500[0]:.4f}, {com_500[1]:.4f})")
    print(f"Net displacement [250->500]: row={disp_r:.4f}  col={disp_c:.4f}  mag={disp_mag:.4f}")
    print(f"Average velocity [250->500]: v_row={vel_r:.6f}  v_col={vel_c:.6f}  |v|={vel_mag:.6f} cells/step")

    result = {
        "rule_source":   "archive/iter_215/results/champion_rule.json",
        "grid_size":     GRID_SIZE,
        "num_steps":     NUM_STEPS,
        "seed":          "3-bit L-tromino",
        "seed_offsets":  LTROMINO,
        "initial_bits":  initial_bits,
        "final_bits":    final_bits,
        "bit_conserved": bool(initial_bits == final_bits),
        "metrics": {
            "com_at_step_250":  com_250,
            "com_at_step_500":  com_500,
            "net_displacement_row_250_to_500": round(disp_r, 6),
            "net_displacement_col_250_to_500": round(disp_c, 6),
            "net_displacement_magnitude":      round(disp_mag, 6),
            "window_steps":  window,
            "avg_velocity_row":  round(vel_r, 8),
            "avg_velocity_col":  round(vel_c, 8),
            "avg_velocity_magnitude": round(vel_mag, 8),
        },
        "runtime_seconds": round(elapsed, 3),
        "step_log": step_log,
    }

    out_path = OUTPUT_DIR / "characterization.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
