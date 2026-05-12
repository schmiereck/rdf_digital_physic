#!/usr/bin/env python3
"""
run_iter141_long_run_analysis.py

Long-run (1000-step) analysis of the iter_140 champion rule (rule_049).
Determines whether its high fitness score corresponds to sustained coherent
motion or a chaotic explosion.

Outputs:
  archive/iter_141/results/motion_log.csv
  archive/iter_141/results/frames/frame_XXXX.txt
"""

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_140" / "population" / "rule_049.json"
ASH_PATH     = Path(__file__).parent / "ash_pattern.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_141" / "results"
FRAMES_DIR   = RESULTS_DIR / "frames"
LOG_CSV      = RESULTS_DIR / "motion_log.csv"

GRID_SIZE   = 200
TOTAL_STEPS = 1000
LOG_INTERVAL = 20
SNAP_STEPS  = [0, 200, 400, 600, 800, 1000]
WIN_SIZE    = 60  # text window around target COM for snapshots

HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def get_components(grid: np.ndarray) -> list:
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    comps = []
    for start in sorted(live):
        if start in visited:
            continue
        comp = []
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            comp.append(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % GRID_SIZE, (r + dr) % GRID_SIZE)
                if nb in live and nb not in visited:
                    stack.append(nb)
        comps.append(comp)
    return comps


def normalize_shape(cells: list) -> frozenset:
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    mq, mr = min(qs), min(rs)
    return frozenset((q - mq, r - mr) for q, r in cells)


def characterize(cells: list, lut: np.ndarray, max_steps: int = 120, padding: int = 25):
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    h = max(qs) - min(qs) + 1 + 2 * padding
    w = max(rs) - min(rs) + 1 + 2 * padding
    iso = np.zeros((h, w), dtype=np.uint8)
    for q, r in cells:
        iso[q - min(qs) + padding, r - min(rs) + padding] = 1
    seen = {}
    for s in range(max_steps + 1):
        live = list(map(tuple, np.argwhere(iso == 1)))
        if not live:
            return 'decayed', 0
        norm = normalize_shape(live)
        if norm in seen:
            p = s - seen[norm]
            return ('still_life' if p == 1 else 'oscillator'), p
        seen[norm] = s
        iso = step_grid(iso, lut)
    return 'unknown', 0


def cells_com(cells: list) -> tuple:
    return (sum(c[0] for c in cells) / len(cells),
            sum(c[1] for c in cells) / len(cells))


def global_com(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def displacement(cq: float, cr: float, oq: float, or_: float) -> float:
    dq = cq - oq
    dr = cr - or_
    return math.sqrt(dq * dq + dr * dr)


def save_text_frame(grid: np.ndarray, step: int, cq: float, cr: float,
                    target_set: set, path: Path) -> None:
    half = WIN_SIZE // 2
    q0 = int(round(cq)) - half
    r0 = int(round(cr)) - half

    lines = [f"rule_049  t={step:4d}  window centered at ({cq:.1f},{cr:.1f})"]
    lines.append("+" + "-" * WIN_SIZE + "+")
    for qi in range(WIN_SIZE):
        q = (q0 + qi) % GRID_SIZE
        row_chars = []
        for ri in range(WIN_SIZE):
            r = (r0 + ri) % GRID_SIZE
            cell = (q, r)
            if grid[q, r] == 1:
                row_chars.append("O" if cell in target_set else "#")
            else:
                row_chars.append(".")
        lines.append("|" + "".join(row_chars) + "|")
    lines.append("+" + "-" * WIN_SIZE + "+")
    bits_in_window = int(sum(
        grid[(q0 + qi) % GRID_SIZE, (r0 + ri) % GRID_SIZE]
        for qi in range(WIN_SIZE)
        for ri in range(WIN_SIZE)
    ))
    global_bits = int(grid.sum())
    lines.append(f"window_bits={bits_in_window}  global_bits={global_bits}")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Loading inputs ===", flush=True)
    with open(RULE_PATH) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)
    print(f"  Rule: {len(rule_dict)} non-identity state mappings", flush=True)

    with open(ASH_PATH) as f:
        ash = json.load(f)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for q, r in ash["cells"]:
        if q < GRID_SIZE and r < GRID_SIZE:
            grid[q, r] = 1
    initial_global_bits = int(grid.sum())
    print(f"  Ash pattern: {initial_global_bits} bits on {GRID_SIZE}x{GRID_SIZE} grid",
          flush=True)

    # ── Find target pair (two closest oscillators) ────────────────────────────
    print("\n=== Characterizing initial components ===", flush=True)
    comps = get_components(grid)
    print(f"  {len(comps)} connected components found", flush=True)

    objects = []
    for i, cells in enumerate(comps):
        status, period = characterize(cells, lut)
        cq, cr = cells_com(cells)
        objects.append({
            'i': i, 'cells': cells, 'status': status,
            'period': period, 'bits': len(cells), 'cq': cq, 'cr': cr,
        })

    osc = [o for o in objects if o['status'] in ('oscillator', 'still_life')]
    print(f"  {len(osc)} oscillator/still-life objects", flush=True)
    if len(osc) < 2:
        print("  WARNING: fewer than 2 oscillators found; using all components",
              flush=True)
        osc = objects

    # Find closest pair
    best_d = float('inf')
    pair = (osc[0], osc[1])
    for i in range(len(osc)):
        for j in range(i + 1, len(osc)):
            dq = osc[i]['cq'] - osc[j]['cq']
            dr = osc[i]['cr'] - osc[j]['cr']
            d = math.sqrt(dq ** 2 + dr ** 2)
            if d < best_d:
                best_d = d
                pair = (osc[i], osc[j])

    A, B = pair
    print(f"  Target A: [{A['i']}] {A['status']} p={A['period']} "
          f"bits={A['bits']} COM=({A['cq']:.1f},{A['cr']:.1f})", flush=True)
    print(f"  Target B: [{B['i']}] {B['status']} p={B['period']} "
          f"bits={B['bits']} COM=({B['cq']:.1f},{B['cr']:.1f})", flush=True)
    print(f"  Pair distance: {best_d:.3f}", flush=True)

    target_cells = A['cells'] + B['cells']
    target_set   = set(map(tuple, target_cells))
    init_cq, init_cr = cells_com(target_cells)
    initial_bits = len(target_cells)

    print(f"  Combined COM: ({init_cq:.2f}, {init_cr:.2f})", flush=True)
    print(f"  Initial target bits: {initial_bits}", flush=True)

    # ── Run simulation with logging ───────────────────────────────────────────
    print(f"\n=== Simulating {TOTAL_STEPS} steps (logging every {LOG_INTERVAL}) ===",
          flush=True)

    log_rows = []

    def log_step(step: int, g: np.ndarray) -> tuple:
        cq, cr = global_com(g)
        live_count = int(g.sum())
        disp = displacement(cq, cr, init_cq, init_cr)
        log_rows.append({
            'step': step,
            'live_cell_count': live_count,
            'com_q': round(cq, 4),
            'com_r': round(cr, 4),
            'total_displacement': round(disp, 6),
        })
        return cq, cr, live_count, disp

    # Step 0
    cq0, cr0, lc0, d0 = log_step(0, grid)
    print(f"  t={0:4d}: bits={lc0}  COM=({cq0:.2f},{cr0:.2f})  disp={d0:.4f}",
          flush=True)

    if 0 in SNAP_STEPS:
        save_text_frame(grid, 0, init_cq, init_cr, target_set,
                        FRAMES_DIR / "frame_0000.txt")
        print("  Saved frame_0000.txt", flush=True)

    for s in range(1, TOTAL_STEPS + 1):
        grid = step_grid(grid, lut)

        if s % LOG_INTERVAL == 0:
            cq, cr, lc, d = log_step(s, grid)
            if s % 100 == 0:
                print(f"  t={s:4d}: bits={lc}  COM=({cq:.2f},{cr:.2f})  disp={d:.4f}",
                      flush=True)

        if s in SNAP_STEPS:
            fname = f"frame_{s:04d}.txt"
            save_text_frame(grid, s, init_cq, init_cr, target_set,
                            FRAMES_DIR / fname)
            print(f"  Saved {fname}", flush=True)

    # ── Save motion log CSV ───────────────────────────────────────────────────
    fieldnames = ['step', 'live_cell_count', 'com_q', 'com_r', 'total_displacement']
    with open(LOG_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_rows)
    print(f"\nSaved {LOG_CSV}", flush=True)

    # ── Velocity analysis ─────────────────────────────────────────────────────
    print("\n=== Velocity analysis ===", flush=True)

    def get_disp_at(step: int) -> float:
        for row in log_rows:
            if row['step'] == step:
                return row['total_displacement']
        return 0.0

    def get_com_at(step: int) -> tuple:
        for row in log_rows:
            if row['step'] == step:
                return row['com_q'], row['com_r']
        return (0.0, 0.0)

    # velocity_early: average velocity between step 100 and 500
    cq_100, cr_100 = get_com_at(100)
    cq_500, cr_500 = get_com_at(500)
    disp_early = math.sqrt((cq_500 - cq_100)**2 + (cr_500 - cr_100)**2)
    velocity_early = disp_early / 400.0  # per step

    # velocity_late: average velocity between step 500 and 900
    cq_900, cr_900 = get_com_at(900)
    disp_late = math.sqrt((cq_900 - cq_500)**2 + (cr_900 - cr_500)**2)
    velocity_late = disp_late / 400.0  # per step

    velocity_decay_ratio = (velocity_late / velocity_early
                            if velocity_early > 1e-10 else 0.0)

    final_bits = log_rows[-1]['live_cell_count']
    final_displacement = log_rows[-1]['total_displacement']

    bit_ratio = final_bits / initial_global_bits
    sustained_motion = bool(velocity_decay_ratio > 0.8 and bit_ratio < 3.0)

    print(f"  initial_bit_count:     {initial_global_bits}", flush=True)
    print(f"  final_bit_count:       {final_bits}", flush=True)
    print(f"  bit_ratio:             {bit_ratio:.4f}", flush=True)
    print(f"  initial_target_bits:   {initial_bits}", flush=True)
    print(f"  final_displacement:    {final_displacement:.4f}", flush=True)
    print(f"  velocity_early:        {velocity_early:.8f} (steps 100-500)", flush=True)
    print(f"  velocity_late:         {velocity_late:.8f} (steps 500-900)", flush=True)
    print(f"  velocity_decay_ratio:  {velocity_decay_ratio:.6f}", flush=True)
    print(f"  sustained_motion:      {sustained_motion}", flush=True)

    # ── Print log summary ─────────────────────────────────────────────────────
    print("\n=== Motion log tail (last 10 entries) ===", flush=True)
    for row in log_rows[-10:]:
        print(f"  step={row['step']:4d}  bits={row['live_cell_count']:6d}  "
              f"COM=({row['com_q']:.2f},{row['com_r']:.2f})  "
              f"disp={row['total_displacement']:.4f}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
