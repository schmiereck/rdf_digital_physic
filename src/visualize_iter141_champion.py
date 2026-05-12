#!/usr/bin/env python3
"""
Visualize long-term dynamics of iter_140 champion rule (rule_049).

Loads the ash pattern on a 200x200 grid, identifies the two closest oscillator
objects, runs 1000 steps, and saves 40x40 window snapshots centered on the
target pair's initial COM.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_140" / "population" / "rule_049.json"
ASH_PATH     = Path(__file__).parent / "ash_pattern.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_141" / "results"

GRID_SIZE   = 200
TOTAL_STEPS = 1000
SNAP_STEPS  = [0, 100, 200, 500, 1000]
WIN_SIZE    = 40

HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def rule_to_lut(rule_dict):
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid, lut):
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


def get_components(grid):
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited = set()
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


def normalize_shape(cells):
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    mq, mr = min(qs), min(rs)
    return frozenset((q - mq, r - mr) for q, r in cells)


def characterize(cells, lut, max_steps=120, padding=25):
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


def cells_com(cells):
    return (sum(c[0] for c in cells) / len(cells),
            sum(c[1] for c in cells) / len(cells))


def extract_window(grid, cq, cr):
    half = WIN_SIZE // 2
    q0 = int(round(cq)) - half
    r0 = int(round(cr)) - half
    rows = np.arange(q0, q0 + WIN_SIZE) % GRID_SIZE
    cols = np.arange(r0, r0 + WIN_SIZE) % GRID_SIZE
    return grid[np.ix_(rows, cols)].copy(), q0, r0


def window_abs_com(window, q0, r0):
    xs, ys = np.where(window > 0)
    if len(xs) == 0:
        return None, None
    aq = (q0 + float(np.mean(xs))) % GRID_SIZE
    ar = (r0 + float(np.mean(ys))) % GRID_SIZE
    return aq, ar


def save_snapshot(window, step, q0, r0, target_set, outpath):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(window, cmap='binary', interpolation='nearest', vmin=0, vmax=1)

    if step == 0 and target_set:
        ty, tx = [], []
        for q, r in target_set:
            qi = (q - q0) % GRID_SIZE
            ri = (r - r0) % GRID_SIZE
            if 0 <= qi < WIN_SIZE and 0 <= ri < WIN_SIZE:
                ty.append(qi)
                tx.append(ri)
        if tx:
            ax.scatter(tx, ty, c='red', s=55, marker='^', alpha=0.85,
                       zorder=5, label='target pair')
            ax.legend(fontsize=8, loc='upper right')

    bits = int(window.sum())
    ax.set_title(f'rule_049   t={step}   ({bits} bits in window)', fontsize=11)
    ax.set_xlabel('r (col)', fontsize=9)
    ax.set_ylabel('q (row)', fontsize=9)
    ax.set_xlim(-0.5, WIN_SIZE - 0.5)
    ax.set_ylim(WIN_SIZE - 0.5, -0.5)
    plt.tight_layout(pad=0.4)
    plt.savefig(str(outpath), dpi=120, bbox_inches='tight')
    plt.close(fig)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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
    nbits = int(grid.sum())
    print(f"  Ash: {nbits} bits on {GRID_SIZE}x{GRID_SIZE} grid", flush=True)

    print("\n=== Finding initial connected components ===", flush=True)
    comps = get_components(grid)
    print(f"  {len(comps)} components", flush=True)

    print("\n=== Characterizing each component with rule_049 ===", flush=True)
    objects = []
    for i, cells in enumerate(comps):
        status, period = characterize(cells, lut)
        cq, cr = cells_com(cells)
        objects.append({
            'i': i, 'cells': cells, 'status': status,
            'period': period, 'bits': len(cells), 'cq': cq, 'cr': cr,
        })
        print(f"  [{i+1:3d}/{len(comps)}] {status:<12s} p={period:3d}  "
              f"bits={len(cells):2d}  COM=({cq:.1f},{cr:.1f})", flush=True)

    print("\n=== Identifying target pair (two closest oscillators) ===", flush=True)
    osc = [o for o in objects if o['status'] in ('oscillator', 'still_life')]
    print(f"  {len(osc)} oscillator/still-life objects", flush=True)
    if len(osc) < 2:
        print("  WARNING: fewer than 2 oscillators found; using all objects", flush=True)
        osc = objects

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
    print(f"  Target A: obj[{A['i']}]  {A['status']}  p={A['period']}  "
          f"bits={A['bits']}  COM=({A['cq']:.1f},{A['cr']:.1f})", flush=True)
    print(f"  Target B: obj[{B['i']}]  {B['status']}  p={B['period']}  "
          f"bits={B['bits']}  COM=({B['cq']:.1f},{B['cr']:.1f})", flush=True)
    print(f"  Pairwise distance: {best_d:.3f}", flush=True)

    target_cells = A['cells'] + B['cells']
    target_set   = set(map(tuple, target_cells))
    tcq, tcr     = cells_com(target_cells)
    initial_bits = len(target_cells)
    print(f"  Combined COM: ({tcq:.2f}, {tcr:.2f})", flush=True)
    print(f"  Initial target bits: {initial_bits}", flush=True)

    print(f"\n=== Simulating {TOTAL_STEPS} steps + snapshots ===", flush=True)
    snap = {}

    def do_snapshot(step, g):
        win, q0, r0 = extract_window(g, tcq, tcr)
        bits = int(win.sum())
        aq, ar = window_abs_com(win, q0, r0)
        snap[step] = {'bits': bits, 'aq': aq, 'ar': ar}
        fname = RESULTS_DIR / f"snapshot_t{step}.png"
        save_snapshot(win, step, q0, r0, target_set if step == 0 else set(), fname)
        com_str = f"({aq:.2f},{ar:.2f})" if aq is not None else "None"
        print(f"  t={step:4d}: window_bits={bits:5d}  abs_com={com_str}  -> {fname.name}",
              flush=True)

    do_snapshot(0, grid)

    for s in range(1, TOTAL_STEPS + 1):
        grid = step_grid(grid, lut)
        if s in SNAP_STEPS:
            do_snapshot(s, grid)
        elif s % 100 == 0:
            print(f"  step {s:4d}: global_bits={int(grid.sum())}", flush=True)

    print("\n=== Analysis ===", flush=True)
    b200  = snap[200]['bits']
    b1000 = snap[1000]['bits']

    c200  = (snap[200]['aq'],  snap[200]['ar'])
    c1000 = (snap[1000]['aq'], snap[1000]['ar'])

    if c200[0] is not None and c1000[0] is not None:
        dq   = c1000[0] - c200[0]
        dr   = c1000[1] - c200[1]
        disp = math.sqrt(dq ** 2 + dr ** 2)
    else:
        disp = 0.0

    # glider: bit count within 20% of initial AND window COM moves substantially
    is_glider = bool(
        b1000 > 0 and
        abs(b1000 - initial_bits) / max(initial_bits, 1) < 0.20 and
        disp > 10.0
    )

    print(f"  initial_target_bits:   {initial_bits}", flush=True)
    print(f"  bits_at_t200:          {b200}", flush=True)
    print(f"  bits_at_t1000:         {b1000}", flush=True)
    print(f"  displacement_200_1000: {disp:.4f}", flush=True)
    print(f"  is_glider:             {is_glider}", flush=True)

    # Build per-snapshot summary for log
    snap_summary = "\n".join(
        f"  t={s:4d}: bits={snap[s]['bits']}  COM=({snap[s]['aq']},{snap[s]['ar']})"
        for s in SNAP_STEPS
    )
    print(f"\n=== Snapshot summary ===\n{snap_summary}", flush=True)

    return 0, {
        'initial_bits': initial_bits,
        'b200': b200,
        'b1000': b1000,
        'disp': disp,
        'is_glider': is_glider,
        'snap': snap,
        'target_A': A,
        'target_B': B,
        'best_d': best_d,
    }


if __name__ == "__main__":
    rc, _ = main()
    sys.exit(rc)
