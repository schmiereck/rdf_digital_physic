#!/usr/bin/env python3
"""Cooperative survival mechanism extraction for the 2D hex v=0.469c glider (iter_252)."""
import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from evolution import rule_dict_to_lut, step_grid, LTROMINO_CELLS

GRID, STEPS = 128, 200

def canonical_shape(grid):
    """Return a canonical representation of a binary pattern (shifted to origin)."""
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0, 0, np.array([]))
    return (len(xs), len(ys), tuple(sorted(zip(xs - xs.min(), ys - ys.min()))))

def trace_glider(grid, lut, steps):
    """Run glider, detect period by matching canonical shapes to the seed."""
    seed_shape = canonical_shape(grid)
    com_0 = np.array([seed_shape[0]/2.0, seed_shape[1]/2.0], dtype=float)
    histories = []
    grids = []
    coms = []
    com = np.array([float(np.mean(np.where(grid>0)[0])), float(np.mean(np.where(grid>0)[1]))])
    for t in range(steps + 1):
        shapes = canonical_shape(grid)
        coms.append(com.copy())
        grids.append(grid.copy())
        histories.append((t, shapes))
        if t < steps:
            grid = step_grid(grid, lut)
            xs, ys = np.where(grid > 0)
            com = np.array([np.mean(xs), np.mean(ys)]) if len(xs) > 0 else np.array([0.0, 0.0])

    # Find speed and period by matching shapes
    period = None
    period_detections = []
    for p in range(1, len(histories) // 2):
        matches = 0
        for t in range(len(histories) - p):
            if histories[t][1] == histories[t + p][1]:
                matches += 1
        period_detections.append({"period": p, "matches": matches})
        if matches == len(histories) - p and period is None:
            period = p

    # Speed from first period displacement
    if period is not None and len(coms) > period:
        dx = coms[period][0] - coms[0][0]
        dy = coms[period][1] - coms[0][1]
        speed = np.sqrt(dx**2 + dy**2) / period
    elif len(coms) > 1:
        dx = coms[-1][0] - coms[0][0]
        dy = coms[-1][1] - coms[0][1]
        speed = np.sqrt(dx**2 + dy**2) / STEPS
    else:
        speed = 0.0
    return histories, grids, coms, speed, period, period_detections

def compute_neighborhood_state(grid, r, c):
    """Compute hex neighborhood state int for cell (r,c)."""
    e  = grid[r, (c-1) % GRID]
    w  = grid[r, (c+1) % GRID]
    ne = grid[(r-1) % GRID, c]
    sw = grid[(r+1) % GRID, c]
    se = grid[(r-1) % GRID, (c-1) % GRID]
    nw = grid[(r+1) % GRID, (c+1) % GRID]
    center = grid[r, c]
    return center*64 + e*32 + se*16 + sw*8 + w*4 + nw*2 + ne

def main():
    rule_path = Path("archive/iter_222/results/champion_rule_perfect.json")
    with open(rule_path) as f:
        data = json.load(f)
    rule_dict = {str(k): str(v) for k, v in data["rule_dict"].items()}
    lut = rule_dict_to_lut(data["rule_dict"])

    # Full glider
    full_grid = np.zeros((GRID, GRID), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        full_grid[r, c] = 1
    full_history, full_grids, full_coms, speed, period, period_detections = trace_glider(full_grid, lut, STEPS)
    full_bit_counts = [int(g.sum()) for g in full_grids]

    # Individual seeds
    single_final_bits = []
    single_grids_all = []
    for i, cell in enumerate(LTROMINO_CELLS):
        sg = np.zeros((GRID, GRID), dtype=np.uint8)
        sg[cell[0], cell[1]] = 1
        grids = [sg.copy()]
        g = sg.copy()
        for _ in range(STEPS):
            g = step_grid(g, lut)
            grids.append(g.copy())
        single_grids_all.append(grids)
        single_final_bits.append(int(grids[-1].sum()))

    # OR-superposition mismatches
    or_mismatch_count = 0
    mismatch_steps = []
    binding_lut_entries = {}
    first_mismatch_found = False
    for t in range(STEPS + 1):
        or_grid = np.zeros((GRID, GRID), dtype=np.uint8)
        for sg in single_grids_all:
            or_grid = np.maximum(or_grid, sg[t])
        full_g = full_grids[t]
        if not np.array_equal(full_g, or_grid):
            or_mismatch_count += 1
            mismatch_steps.append(t)
            if not first_mismatch_found:
                first_mismatch_found = True
                # Extract LUT entries at first mismatch step
                diff_coords = np.argwhere(full_g != or_grid)
                for r, c in diff_coords:
                    state = compute_neighborhood_state(full_g, r, c)
                    lut_out = int(lut[state])
                    center_val = int(full_g[r, c])
                    binding_lut_entries[int(state)] = (int(state), lut_out, f"full={center_val}, or={int(or_grid[r, c])}")

    result = {
        "glider_speed": float(speed),
        "glider_period": period,
        "full_glider_bit_counts": full_bit_counts,
        "single_bit_final_bits": single_final_bits,
        "or_mismatch_count": or_mismatch_count,
        "binding_lut_entries": binding_lut_entries,
        "full_rule_dict": rule_dict,
        "period_detections": period_detections,
    }
    out_path = Path("archive/iter_252/results/hex_mechanism.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {out_path}")
    print(f"Speed: {speed:.4f}, Period: {period}, OR-mismatches: {or_mismatch_count}/{STEPS+1}")
    print(f"Final bits (full): {full_bit_counts[-1]}, Singles: {single_final_bits}")
    print(f"Binding LUT entries: {len(binding_lut_entries)}")

if __name__ == "__main__":
    main()
