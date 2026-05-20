#!/usr/bin/env python3
"""
iter_223: Probe contiguous 3-bit and 4-bit seeds against two champion rules.
- Rule A: sub-light glider champion (iter_222, DisplacementConsistencyFitness)
- Rule B: elastic collision champion (iter_193/iter_002, RecessionBiasedFitness)

For each contiguous N-bit seed (N in {3, 4}), placed near grid center on a
128x128 hex toroidal grid, simulate 200 steps and classify the asymptotic
behavior using trigonometric toroidal CoM, period detection, and mean
speed measurements over five 40-step windows.
"""

import json
import sys
from pathlib import Path

import numpy as np

GRID_SIZE = 128
STEPS = 200
WINDOWS = 5
WINDOW_LEN = STEPS // WINDOWS  # 40
STABLE_START = 150
STABLE_END = 200
MAX_PERIOD = 20

HEX_DIRS = [
    ( 1,  0),  # E
    ( 1, -1),  # SE
    ( 0, -1),  # SW
    (-1,  0),  # W
    (-1,  1),  # NW
    ( 0,  1),  # NE
]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_A_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"
RULE_B_PATH = PROJECT_ROOT / "archive" / "iter_193" / "iter_002" / "results" / "champion_rule.json"
RESULTS_PATH = PROJECT_ROOT / "archive" / "iter_223" / "results" / "glider_probe_results.json"


def load_rule(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return {int(k): int(v) for k, v in data["rule_dict"].items()}


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


def canonical_translate(cells):
    """Translate cells so that the lexicographically smallest cell is at (0,0)."""
    sorted_cells = sorted(cells)
    r0, c0 = sorted_cells[0]
    return tuple((r - r0, c - c0) for r, c in sorted_cells)


def generate_contiguous_seeds(n_cells: int) -> list[tuple]:
    """All contiguous n-cell hex polyominoes under translation-only canonical form."""
    # Start with a single cell at (0, 0).
    seeds = {canonical_translate([(0, 0)])}
    for _ in range(n_cells - 1):
        new_seeds = set()
        for shape in seeds:
            shape_set = set(shape)
            for cell in shape:
                for dr, dc in HEX_DIRS:
                    nb = (cell[0] + dr, cell[1] + dc)
                    if nb in shape_set:
                        continue
                    new_shape = list(shape) + [nb]
                    new_seeds.add(canonical_translate(new_shape))
        seeds = new_seeds
    return sorted(seeds)


def trigonometric_com_and_bits(grid: np.ndarray) -> tuple[tuple[float, float], int]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    grid_size = GRID_SIZE
    twopi = 2.0 * np.pi
    a_r = twopi * rows.astype(float) / grid_size
    com_r = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * grid_size / twopi
    a_c = twopi * cols.astype(float) / grid_size
    com_c = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * grid_size / twopi
    return (float(com_r), float(com_c)), int(grid.sum())


def unwrap_coms(coms):
    unwrapped = [coms[0]]
    for i in range(1, len(coms)):
        prev_com = coms[i - 1]
        cur_com = coms[i]
        dx = cur_com[0] - prev_com[0]
        dy = cur_com[1] - prev_com[1]
        if dx > 64:
            dx -= 128.0
        elif dx < -64:
            dx += 128.0
        if dy > 64:
            dy -= 128.0
        elif dy < -64:
            dy += 128.0
        last = unwrapped[-1]
        unwrapped.append((last[0] + dx, last[1] + dy))
    return unwrapped


def canonical_active_cells(grid: np.ndarray) -> tuple:
    """Toroidal canonical form: relative positions to first cell with ±64
    wraparound, then re-translated so the (toroidally) lex-min cell is at (0,0)."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return tuple()
    half = GRID_SIZE // 2
    r0_abs = int(rows[0])
    c0_abs = int(cols[0])
    rel = []
    for r, c in zip(rows.tolist(), cols.tolist()):
        dr = int(r) - r0_abs
        if dr > half:
            dr -= GRID_SIZE
        elif dr < -half:
            dr += GRID_SIZE
        dc = int(c) - c0_abs
        if dc > half:
            dc -= GRID_SIZE
        elif dc < -half:
            dc += GRID_SIZE
        rel.append((dr, dc))
    rel.sort()
    rmin, cmin = rel[0]
    return tuple((r - rmin, c - cmin) for r, c in rel)


def detect_period(canonical_history, bit_counts, t_start: int, t_end: int):
    for p in range(1, MAX_PERIOD + 1):
        ok = True
        for t in range(t_start, t_end - p + 1):
            if canonical_history[t] != canonical_history[t + p]:
                ok = False
                break
            if bit_counts[t] != bit_counts[t + p]:
                ok = False
                break
        if ok:
            return p
    return None


def simulate_seed(seed_cells, lut):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_cells:
        grid[(r + 64) % GRID_SIZE, (c + 64) % GRID_SIZE] = 1

    coms = []
    bit_counts = []
    canonical_history = []

    com, bits = trigonometric_com_and_bits(grid)
    coms.append(com)
    bit_counts.append(bits)
    canonical_history.append(canonical_active_cells(grid))

    for _ in range(STEPS):
        grid = step_grid(grid, lut)
        com, bits = trigonometric_com_and_bits(grid)
        coms.append(com)
        bit_counts.append(bits)
        canonical_history.append(canonical_active_cells(grid))

    unwrapped = unwrap_coms(coms)

    # Per-window velocity magnitudes
    window_velocities = []
    for w in range(WINDOWS):
        start = w * WINDOW_LEN
        end = start + WINDOW_LEN
        sr, sc = unwrapped[start]
        er, ec = unwrapped[end]
        dr = er - sr
        dc = ec - sc
        v = float(np.sqrt(dr * dr + dc * dc) / WINDOW_LEN)
        window_velocities.append(v)
    velocity_std = float(np.std(window_velocities))

    # Mean speed = |net displacement| / 200
    net_dr = unwrapped[-1][0] - unwrapped[0][0]
    net_dc = unwrapped[-1][1] - unwrapped[0][1]
    mean_speed = float(np.sqrt(net_dr * net_dr + net_dc * net_dc) / STEPS)

    initial_bits = bit_counts[0]
    final_bits = bit_counts[-1]

    period = detect_period(canonical_history, bit_counts, STABLE_START, STABLE_END)

    if final_bits == 0:
        classification = "extinct"
    elif period is None:
        classification = "chaotic/unstable"
    elif period == 1 and mean_speed < 0.05:
        classification = "still life"
    elif period > 1 and mean_speed < 0.05:
        classification = "stationary oscillator"
    elif mean_speed >= 0.9:
        classification = "v=1c glider"
    elif mean_speed >= 0.05:
        classification = "v<c glider"
    else:
        # Stable with very small motion but period > 1 should already be caught above.
        classification = "stationary oscillator"

    return {
        "initial_cells": [list(c) for c in seed_cells],
        "initial_bit_count": int(initial_bits),
        "final_bit_count": int(final_bits),
        "period": int(period) if period is not None else None,
        "mean_speed": mean_speed,
        "velocity_std": velocity_std,
        "window_velocities": window_velocities,
        "classification": classification,
    }


def probe_rule(rule_name: str, rule_dict: dict, all_seeds):
    lut = rule_to_lut(rule_dict)
    seed_results = []
    counts: dict[str, int] = {}
    for seed in all_seeds:
        result = simulate_seed(seed, lut)
        result["n_cells"] = len(seed)
        seed_results.append(result)
        counts[result["classification"]] = counts.get(result["classification"], 0) + 1
    return {"rule": rule_name, "counts": counts, "seeds": seed_results}


def main():
    print("Generating contiguous 3-bit seeds...")
    seeds_3 = generate_contiguous_seeds(3)
    print(f"  -> {len(seeds_3)} seeds")
    print("Generating contiguous 4-bit seeds...")
    seeds_4 = generate_contiguous_seeds(4)
    print(f"  -> {len(seeds_4)} seeds")
    all_seeds = seeds_3 + seeds_4
    print(f"Total seeds: {len(all_seeds)}")

    print("\nLoading rules...")
    rule_a = load_rule(RULE_A_PATH)
    rule_b = load_rule(RULE_B_PATH)
    print(f"  Rule A (iter_222 sub-light): {len(rule_a)} mappings")
    print(f"  Rule B (iter_193 collision): {len(rule_b)} mappings")

    print("\nProbing Rule A (DisplacementConsistencyFitness)...")
    res_a = probe_rule("iter_222_DisplacementConsistencyFitness", rule_a, all_seeds)
    print(f"  Counts: {res_a['counts']}")

    print("\nProbing Rule B (RecessionBiasedFitness)...")
    res_b = probe_rule("iter_193_RecessionBiasedFitness", rule_b, all_seeds)
    print(f"  Counts: {res_b['counts']}")

    summary = {
        "grid_size": GRID_SIZE,
        "steps": STEPS,
        "windows": WINDOWS,
        "stable_window": [STABLE_START, STABLE_END],
        "max_period": MAX_PERIOD,
        "num_3bit_seeds": len(seeds_3),
        "num_4bit_seeds": len(seeds_4),
        "rule_a_source": str(RULE_A_PATH.relative_to(PROJECT_ROOT)),
        "rule_b_source": str(RULE_B_PATH.relative_to(PROJECT_ROOT)),
        "rule_a": res_a,
        "rule_b": res_b,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWritten: {RESULTS_PATH}")

    # ── Findings report ──────────────────────────────────────────────
    def report_rule(res):
        name = res["rule"]
        print(f"\n=== {name} ===")
        print(f"  Counts: {res['counts']}")
        vc_gliders = [s for s in res["seeds"] if s["classification"] == "v<c glider"]
        c_gliders  = [s for s in res["seeds"] if s["classification"] == "v=1c glider"]
        has_vc  = len(vc_gliders) > 0
        has_c   = len(c_gliders)  > 0
        print(f"  Has v<c glider:  {has_vc}  ({len(vc_gliders)} seeds)")
        print(f"  Has v=1c glider: {has_c}  ({len(c_gliders)} seeds)")
        print(f"  Supports BOTH glider types: {has_vc and has_c}")
        if vc_gliders:
            print("  Sample v<c gliders:")
            for g in vc_gliders[:5]:
                print(f"    cells={g['initial_cells']} | period={g['period']} | "
                      f"mean_speed={g['mean_speed']:.4f} | std={g['velocity_std']:.4f} | "
                      f"bits_initial={g['initial_bit_count']} | bits_final={g['final_bit_count']}")
        if c_gliders:
            print("  Sample v=1c gliders:")
            for g in c_gliders[:5]:
                print(f"    cells={g['initial_cells']} | period={g['period']} | "
                      f"mean_speed={g['mean_speed']:.4f} | std={g['velocity_std']:.4f} | "
                      f"bits_initial={g['initial_bit_count']} | bits_final={g['final_bit_count']}")
        return has_vc and has_c, vc_gliders, c_gliders

    print("\n" + "=" * 70)
    print("FINDINGS")
    print("=" * 70)
    a_both, a_vc, a_c = report_rule(res_a)
    b_both, b_vc, b_c = report_rule(res_b)

    print("\n--- Summary answer to user's question ---")
    print(f"Rule A (iter_222 sub-light) supports BOTH v<c and v=1c gliders: {a_both}")
    print(f"Rule B (iter_193 collision) supports BOTH v<c and v=1c gliders: {b_both}")


if __name__ == "__main__":
    sys.exit(main() or 0)
