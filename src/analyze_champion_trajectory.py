#!/usr/bin/env python3
"""
Trajectory Analysis for the Champion Rule (iter_221)

Simulates the champion rule for 500 steps on a 128x128 grid with the L_TROMINO_3bit seed,
then characterises:
  - Bit count evolution (final & max)
  - Bounding box (max width / height)
  - Unwrapped centre-of-mass at t = 0, 100, 200, 300, 400, 500
  - Velocity vectors & speed
  - Period detection (shape repeat with translation)

Saves the report to archive/iter_221/results/trajectory_analysis.txt.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from copy import deepcopy

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, make_ltromino_grid, GRID_SIZE


# ──────────────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────────────

def bounding_box(grid: np.ndarray) -> tuple[int, int, int, int]:
    """Return (min_r, max_r, min_c, max_c) or None if empty."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return None
    return int(rows.min()), int(rows.max()), int(cols.min()), int(cols.max())


def grid_shape(grid: np.ndarray) -> np.ndarray:
    """Return a binary (0/1) copy of the grid, for period comparison."""
    return (grid > 0).astype(np.uint8)


def find_labeled_patterns(grid: np.ndarray):
    """
    Return the pattern as a minimal sub-grid (cropped to bounding box),
    and the top-left of the bounding box.
    """
    bb = bounding_box(grid)
    if bb is None:
        return None, (0, 0)
    r0, r1, c0, c1 = bb
    return grid[r0:r1+1, c0:c1+1].copy(), (r0, c0)


def wrap_com(com_unwrapped: list, grid_size: int) -> tuple[float, float]:
    """Map an unwrapped COM coordinate back into [0, grid_size) range."""
    r, c = com_unwrapped
    return (r % grid_size, c % grid_size)


# ──────────────────────────────────────────────────────────────────────────────
# simulation
# ──────────────────────────────────────────────────────────────────────────────

def simulate(rule_dict: dict, steps: int, grid_size: int, seed_cells: list) -> list[dict]:
    """Run the CA simulation, recording full state at every step."""
    lut = rule_dict_to_lut(rule_dict)
    grid = make_ltromino_grid(grid_size, seed_cells)

    history = []

    def snapshot(g, t):
        rows, cols = np.where(g > 0)
        com = (float(np.mean(rows)), float(np.mean(cols))) if len(rows) else (0.0, 0.0)
        bit_count = int(g.sum())
        bb = bounding_box(g)
        return {
            "step": t,
            "com": com,
            "bit_count": bit_count,
            "grid": g.copy(),
            "shape": grid_shape(g),
        }

    history.append(snapshot(grid, 0))

    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        history.append(snapshot(grid, t))

    return history


# ──────────────────────────────────────────────────────────────────────────────
# period detection
# ──────────────────────────────────────────────────────────────────────────────

def detect_period(history: list[dict], max_period: int = 200, max_shift: int = 20) -> dict:
    """
    Look for a repeating pattern: two configurations whose shapes match
    after translating one by (dr, dc).  Uses hashed minimal sub-grid shapes
    for efficiency.

    Returns:
        {
            "found": bool,
            "period": int | None,
            "t_a": int | None,
            "t_b": int | None,
            "translation": tuple | None,
        }
    """
    n = len(history)

    # Precompute cropped shapes and bounding-box offsets
    cropped_shapes = []
    cropped_offsets = []
    for entry in history:
        shape = entry["shape"]
        shape_crop, offset = find_labeled_pattern(shape)
        cropped_shapes.append(shape_crop)
        cropped_offsets.append(offset)

    def shape_hash(sc):
        if sc is None:
            return None
        return sc.tobytes() + struct.pack("<i", sc.shape[0], sc.shape[1])

    import struct

    def shape_hash_v2(sc):
        if sc is None:
            return None
        h = hashlib.md5(sc.tobytes()).hexdigest()
        return (h, sc.shape[0], sc.shape[1])

    import hashlib

    shape_hashes = [shape_hash_v2(s) for s in cropped_shapes]

    # Brute-force comparison within a window around expected period
    for T in range(2, min(max_period, n // 2) + 1):
        found_pair = None
        best_hash = None
        for t_a in range(n - T):
            t_b = t_a + T
            if shape_hashes[t_a] != shape_hashes[t_b]:
                continue
            # Check whether a translation can align the bounding boxes
            sc_a = cropped_shapes[t_a]
            sc_b = cropped_shapes[t_b]
            off_a = cropped_offsets[t_a]
            off_b = cropped_offsets[t_b]
            if sc_a is None or sc_b is None:
                continue
            # The translation that maps off_a -> off_b
            dr = off_b[0] - off_a[0]
            dc = off_b[1] - off_a[1]
            # Reconstruct: if we shift sc_a by (dr, dc), does it match sc_b?
            # We need a grid large enough to hold both.
            h_a, w_a = sc_a.shape
            h_b, w_b = sc_b.shape
            # Build a large-enough grid
            total_h = max(h_a, h_b, h_a + abs(dr))
            total_w = max(w_a, w_b, w_b + abs(dc)) + abs(dc)
            # Simpler: just shift sc_a by (dr, dc) on a shared large canvas
            canvas_h = max(h_a, h_b + dr)
            canvas_w = max(w_a, w_b + dc)
            if canvas_h < 1 or canvas_w < 1:
                continue
            pad_a = max(0, dr, 0)
            pad_b = max(0, -dr, 0)
            pad_l = max(0, dc, 0)
            pad_r = max(0, -dc, 0)
            ch = max(h_a + pad_a, h_b + pad_b)
            cw = max(w_a + pad_l, w_b + pad_r)
            g_a = np.zeros((ch, cw), dtype=np.uint8)
            g_b = np.zeros((ch, cw), dtype=np.uint8)
            g_a[pad_a:pad_a+h_a, pad_l:pad_l+w_a] = sc_a
            g_b[pad_b:pad_b+h_b, pad_r:pad_r+w_b] = sc_b
            if np.array_equal(g_a, g_b):
                found_pair = (t_a, t_b, (dr, dc))
                break
        if found_pair is not None:
            return {
                "found": True,
                "period": T,
                "t_a": found_pair[0],
                "t_b": found_pair[1],
                "translation": found_pair[2],
            }
    return {"found": False, "period": None, "t_a": None, "t_b": None, "translation": None}


def find_labeled_pattern(shape: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
    """Return (cropped sub-grid, top-left offset)."""
    rows, cols = np.where(shape > 0)
    if len(rows) == 0:
        return np.zeros((0, 0), dtype=np.uint8), (0, 0)
    r0, r1 = int(rows.min()), int(rows.max())
    c0, c1 = int(cols.min()), int(cols.max())
    return shape[r0:r1+1, c0:c1+1].copy(), (r0, c0)


# ──────────────────────────────────────────────────────────────────────────────
# main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # Load champion rule
    champion_path = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule.json"
    with open(champion_path) as f:
        champion = json.load(f)

    rule_dict = {int(k): int(v) for k, v in champion["rule_dict"].items()}
    seed_cells = champion["seed_cells"]
    grid_size = champion.get("grid_size", GRID_SIZE)
    steps = champion.get("horizon", 500)

    print("=" * 78)
    print("  CHAMPION RULE TRAJECTORY ANALYSIS — iter_221")
    print("=" * 78)
    print(f"  Rule dict          : {rule_dict}")
    print(f"  Seed cells         : {seed_cells}")
    print(f"  Grid size          : {grid_size}x{grid_size}")
    print(f"  Steps              : {steps}")
    print()

    # ── Run simulation ──────────────────────────────────────────────────
    print(f"Running simulation ({steps} steps) ...")
    history = simulate(rule_dict, steps, grid_size, seed_cells)
    print(f"  Done. {len(history)} snapshots recorded.\n")

    # ── Bit count ───────────────────────────────────────────────────────
    bit_counts = [e["bit_count"] for e in history]
    final_bits = bit_counts[-1]
    max_bits = max(bit_counts)
    initial_bits = bit_counts[0]
    min_bits = min(bit_counts)

    print("─── BIT COUNT ───────────────────────────────────────────────────────")
    print(f"  Initial  : {initial_bits}")
    print(f"  Final    : {final_bits}")
    print(f"  Max      : {max_bits}")
    print(f"  Min      : {min_bits}")
    if initial_bits != final_bits:
        print(f"  Δ bits   : {final_bits - initial_bits} ({'GAINED' if final_bits > initial_bits else 'LOST'})")
    print()

    # ── Bounding box ────────────────────────────────────────────────────
    widths = []
    heights = []
    for entry in history:
        bb = bounding_box(entry["grid"])
        if bb is None:
            widths.append(0)
            heights.append(0)
        else:
            r0, r1, c0, c1 = bb
            widths.append(r1 - r0 + 1)
            heights.append(c1 - c0 + 1)

    max_width = max(widths)
    max_height = max(heights)

    print("─── BOUNDING BOX ────────────────────────────────────────────────────")
    print(f"  Max width (rows)  : {max_width}")
    print(f"  Max height (cols) : {max_height}")
    print(f"  Initial box       : ({widths[0]}×{heights[0]})")
    print(f"  Final box         : ({widths[-1]}×{heights[-1]})")
    print()

    # ── Unwrapped centre-of-mass & velocity ─────────────────────────────
    # Unwrap by detecting jumps > grid_size/2
    coms = [e["com"] for e in history]
    unwrapped = [[coms[0][0], coms[0][1]]]
    for i in range(1, len(coms)):
        dr = coms[i][0] - coms[i-1][0]
        dc = coms[i][1] - coms[i-1][1]
        # unwrap row
        if dr > grid_size / 2:
            dr -= grid_size
        elif dr < -grid_size / 2:
            dr += grid_size
        # unwrap col
        if dc > grid_size / 2:
            dc -= grid_size
        elif dc < -grid_size / 2:
            dc += grid_size
        unwrapped.append([unwrapped[-1][0] + dr, unwrapped[-1][1] + dc])

    # Extract at requested time steps
    print("─── UNWRAPPED CENTRE-OF-MASS ────────────────────────────────────────")
    print(f"  {'t':>4s}  {'COM_r':>12s}  {'COM_c':>12s}")
    for t in range(0, steps + 1, 100):
        entry = history[t]
        uw = unwrapped[t]
        wrapped = wrap_com(uw, grid_size)
        bb = bounding_box(entry["grid"])
        bb_info = f"bb=({bb[1]-bb[0]+1}×{bb[3]-bb[0]+1})" if bb else "bb=(empty)"
        print(f"  {t:>4d}  {uw[0]:>12.4f}  {uw[1]:>12.4f}   (wrapped: ({wrapped[0]:.2f},{wrapped[1]:.2f}))  {bb_info}")
    print()

    # ── Velocity vectors & speed ────────────────────────────────────────
    print("─── VELOCITY ────────────────────────────────────────────────────────")
    print(f"  {'t':>4s}  {'v_r':>10s}  {'v_c':>10s}  {'speed':>10s}  {'direction°':>10s}")

    def speed_from_uw(t_idx):
        if t_idx == 0:
            return 0.0, 0.0, 0.0
        dr = unwrapped[t_idx][0] - unwrapped[t_idx-1][0]
        dc = unwrapped[t_idx][1] - unwrapped[t_idx-1][1]
        speed = math.sqrt(dr*dr + dc*dc)
        return dr, dc, speed

    # Print velocity at key time points
    for t in [0, 100, 200, 300, 400, 500]:
        dr, dc, speed = speed_from_uw(t)
        angle = math.degrees(math.atan2(dc, dr))
        print(f"  {t:>4d}  {dr:>+10.4f}  {dc:>+10.4f}  {speed:>+10.4f}  {angle:>+9.2f}°")

    # Overall average velocity
    overall_dr = unwrapped[-1][0] - unwrapped[0][0]
    overall_dc = unwrapped[-1][1] - unwrapped[0][1]
    overall_speed = math.sqrt(overall_dr**2 + overall_dc**2) / steps
    overall_angle = math.degrees(math.atan2(overall_dc, overall_dr))

    print(f"\n  Overall (t=0→500):")
    print(f"    displacement : ({overall_dr:.4f}, {overall_dc:.4f})")
    print(f"    total dist   : {math.sqrt(overall_dr**2 + overall_dc**2):.4f} cells")
    print(f"    avg speed    : {overall_speed:.6f} cells/step")
    print(f"    direction    : {overall_angle:.2f}° (from +row, CCW)")
    print()

    # ── Per-window velocity ─────────────────────────────────────────────
    print("─── PER-WINDOW VELOCITY (100-step windows) ──────────────────────────")
    print(f"  {'Window':>8s}  {'Δr':>10s}  {'Δc':>10s}  {'speed':>10s}  {'direction°':>10s}")
    for w in range(5):
        t_a = w * 100
        t_b = (w + 1) * 100
        dr = unwrapped[t_b][0] - unwrapped[t_a][0]
        dc = unwrapped[t_b][1] - unwrapped[t_a][1]
        speed = math.sqrt(dr**2 + dc**2) / 100.0
        angle = math.degrees(math.atan2(dc, dr))
        print(f"  {t_a:>4d}-{t_b:>4d}  {dr:>+10.4f}  {dc:>+10.4f}  {speed:>+10.4f}  {angle:>+9.2f}°")
    print()

    # ── Period detection ────────────────────────────────────────────────
    print("─── PERIOD DETECTION ────────────────────────────────────────────────")
    period_result = detect_period(history, max_period=200, max_shift=20)

    if period_result["found"]:
        T = period_result["period"]
        t_a = period_result["t_a"]
        t_b = period_result["t_b"]
        trans = period_result["translation"]
        print(f"  ** PERIODIC DETECTED **")
        print(f"  Period T  : {T} steps")
        print(f"  Detected at t_a={t_a}, t_b={t_b}")
        print(f"  Translation per period: ({trans[0]}, {trans[1]})")
        print(f"  This means the object repeats its shape every {T} steps,")
        print(f"  shifted by ({trans[0]}, {trans[1]}) cells.")
        # Effective velocity from period
        vx = trans[0] / T
        vy = trans[1] / T
        v_eff = math.sqrt(vx**2 + vy**2)
        print(f"  Effective velocity: ({vx:.4f}, {vy:.4f}) = {v_eff:.4f} cells/step")
    else:
        print("  No periodic pattern found (up to period=200).")
        print("  The object may be aperiodic, have a very long period,")
        print("  or slowly deform over time.")
    print()

    # ── Trajectory summary (unwrapped path) ─────────────────────────────
    print("─── TRAJECTORY SUMMARY ──────────────────────────────────────────────")
    # Report the full unwrapped path in a compact form
    path_points = [unwrapped[t] for t in [0, 100, 200, 300, 400, 500]]
    print(f"  Unwrapped COM trajectory:")
    for i, (t, p) in enumerate(zip([0,100,200,300,400,500], path_points)):
        marker = "  →  " if i > 0 else "start: "
        print(f"    {marker} t={t:>3d}  ({p[0]:>10.3f}, {p[1]:>10.3f})")

    # Is it moving in a straight line?
    if overall_speed > 0:
        # compute deviation from straight line
        straight_dist = math.sqrt(overall_dr**2 + overall_dc**2)
        # cumulative path length
        path_length = sum(
            math.sqrt((unwrapped[t][0]-unwrapped[t-1][0])**2 +
                      (unwrapped[t][1]-unwrapped[t-1][1])**2)
            for t in range(1, len(unwrapped))
        )
        linearity = straight_dist / path_length if path_length > 0 else 1.0
        print(f"\n  Linearity of trajectory: {linearity:.4f}  (1.0 = perfectly straight)")
        if linearity > 0.95:
            print("  → The object moves in an almost perfectly straight line.")
        elif linearity > 0.80:
            print("  → The object moves mostly straight with slight wobble.")
        else:
            print("  → The object's path has significant curvature/wobble.")
    print()

    # ── Bit count timeline ──────────────────────────────────────────────
    print("─── BIT COUNT TIMELINE ──────────────────────────────────────────────")
    print(f"  {'t':>4s}  {'bit_count':>10s}")
    for t in [0, 100, 200, 300, 400, 500]:
        print(f"  {t:>4d}  {bit_counts[t]:>10d}")
    # Check if bit count is stable after an initial phase
    if len(set(bit_counts[50:])) == 1:
        stable_t = min(t for t in range(50, len(bit_counts)) if all(bc == bit_counts[t] for bc in bit_counts[t:]))
        print(f"  Bit count stabilised at {bit_counts[stable_t]} at t >= {stable_t}.")
    elif max_bits == initial_bits == final_bits:
        print("  Bit count is perfectly conserved throughout.")
    else:
        print(f"  Bit count fluctuates: range [{min_bits}, {max_bits}].")
    print()

    # ── Full report for saving ──────────────────────────────────────────
    report_lines = []
    def W(line=""):
        report_lines.append(line)

    W("=" * 78)
    W("  CHAMPION RULE TRAJECTORY ANALYSIS — iter_221")
    W("=" * 78)
    W(f"  Rule dict          : {rule_dict}")
    W(f"  Seed cells         : {seed_cells}")
    W(f"  Grid size          : {grid_size}x{grid_size}")
    W(f"  Steps              : {steps}")
    W()
    W("─── BIT COUNT ───────────────────────────────────────────────────────")
    W(f"  Initial  : {initial_bits}")
    W(f"  Final    : {final_bits}")
    W(f"  Max      : {max_bits}")
    W(f"  Min      : {min_bits}")
    if initial_bits != final_bits:
        W(f"  Δ bits   : {final_bits - initial_bits} ({'GAINED' if final_bits > initial_bits else 'LOST'})")
    W()
    W("─── BOUNDING BOX ────────────────────────────────────────────────────")
    W(f"  Max width (rows)  : {max_width}")
    W(f"  Max height (cols) : {max_height}")
    W(f"  Initial box       : ({widths[0]}×{heights[0]})")
    W(f"  Final box         : ({widths[-1]}×{heights[-1]})")
    W()
    W("─── UNWRAPPED CENTRE-OF-MASS ────────────────────────────────────────")
    W(f"  {'t':>4s}  {'COM_r':>12s}  {'COM_c':>12s}")
    for t in range(0, steps + 1, 100):
        entry = history[t]
        uw = unwrapped[t]
        wrapped = wrap_com(uw, grid_size)
        bb = bounding_box(entry["grid"])
        bb_info = f"bb=({bb[1]-bb[0]+1}×{bb[3]-bb[0]+1})" if bb else "bb=(empty)"
        W(f"  {t:>4d}  {uw[0]:>12.4f}  {uw[1]:>12.4f}   (wrapped: ({wrapped[0]:.2f},{wrapped[1]:.2f}))  {bb_info}")
    W()
    W("─── VELOCITY ────────────────────────────────────────────────────────")
    W(f"  {'t':>4s}  {'v_r':>10s}  {'v_c':>10s}  {'speed':>10s}  {'direction°':>10s}")
    for t in [0, 100, 200, 300, 400, 500]:
        dr, dc, speed = speed_from_uw(t)
        angle = math.degrees(math.atan2(dc, dr))
        W(f"  {t:>4d}  {dr:>+10.4f}  {dc:>+10.4f}  {speed:>+10.4f}  {angle:>+9.2f}°")
    W()
    W(f"  Overall (t=0→500):")
    W(f"    displacement : ({overall_dr:.4f}, {overall_dc:.4f})")
    W(f"    total dist   : {math.sqrt(overall_dr**2 + overall_dc**2):.4f} cells")
    W(f"    avg speed    : {overall_speed:.6f} cells/step")
    W(f"    direction    : {overall_angle:.2f}° (from +row, CCW)")
    W()
    W("─── PERIOD DETECTION ────────────────────────────────────────────────")
    if period_result["found"]:
        T = period_result["period"]
        t_a = period_result["t_a"]
        t_b = period_result["t_b"]
        trans = period_result["translation"]
        W(f"  ** PERIODIC DETECTED **")
        W(f"  Period T  : {T} steps")
        W(f"  Detected at t_a={t_a}, t_b={t_b}")
        W(f"  Translation per period: ({trans[0]}, {trans[1]})")
        W(f"  This means the object repeats its shape every {T} steps,")
        W(f"  shifted by ({trans[0]}, {trans[1]}) cells.")
        vx = trans[0] / T
        vy = trans[1] / T
        v_eff = math.sqrt(vx**2 + vy**2)
        W(f"  Effective velocity: ({vx:.4f}, {vy:.4f}) = {v_eff:.4f} cells/step")
    else:
        W("  No periodic pattern found (up to period=200).")
        W("  The object may be aperiodic, have a very long period,")
        W("  or slowly deform over time.")
    W()
    W("─── LINEARITY ───────────────────────────────────────────────────────")
    if overall_speed > 0:
        straight_dist = math.sqrt(overall_dr**2 + overall_dc**2)
        path_length = sum(
            math.sqrt((unwrapped[t][0]-unwrapped[t-1][0])**2 +
                      (unwrapped[t][1]-unwrapped[t-1][1])**2)
            for t in range(1, len(unwrapped))
        )
        linearity = straight_dist / path_length if path_length > 0 else 1.0
        W(f"  Path length       : {path_length:.4f}")
        W(f"  Straight-line dist: {straight_dist:.4f}")
        W(f"  Linearity         : {linearity:.4f}")
        if linearity > 0.95:
            W("  → Straight-line motion (glider-like).")
        elif linearity > 0.80:
            W("  → Mostly straight with wobble.")
        else:
            W("  → Curved or meandering path.")
    W()
    W("─── CONCLUSION ──────────────────────────────────────────────────────")
    if period_result["found"]:
        W(f"  The champion rule produces a GLIDER with period T={period_result['period']},")
        W(f"  velocity ({period_result['translation'][0]/period_result['period']:.4f},")
        W(f"           {period_result['translation'][1]/period_result['period']:.4f}) cells/step.")
        if final_bits == initial_bits:
            W(f"  Bit count conserved ({initial_bits} → {final_bits}).")
        else:
            W(f"  Bit count changed: {initial_bits} → {final_bits} (max={max_bits}).")
    else:
        W("  No clean glider behaviour detected.")
    W("=" * 78)

    report = "\n".join(report_lines)

    # ── Write to file ───────────────────────────────────────────────────
    out_path = PROJECT_ROOT / "archive" / "iter_221" / "results" / "trajectory_analysis.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\n  Report saved to: {out_path}")
    print()

    # ── Print to stdout ─────────────────────────────────────────────────
    print(report)


if __name__ == "__main__":
    main()
