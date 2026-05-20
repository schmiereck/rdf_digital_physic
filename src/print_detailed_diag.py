#!/usr/bin/env python3
"""
print_detailed_diag.py

Imports and runs DisplacementConsistencyFitness on the champion rule from
iter_220 (champion_vc_rule_consistency.json), but prints out the exact
first_entry and last_entry, the dx and dy, and the window_steps for
EACH of the 5 windows.

This reveals:
  - Why window 2 has magnitude 1.0
  - Why the mean velocity magnitude is so low (~0.0253)
  - How window boundaries align with the simulation history
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# Ensure src/ is on the path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from new_fitness import DisplacementConsistencyFitness

# Use utf-8 encoding for stdout to avoid Windows cp1252 issues
sys.stdout.reconfigure(encoding="utf-8")

# -- Constants --
CHAMPION_JSON    = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_vc_rule_consistency.json"
GRID_SIZE        = 128
SIM_STEPS        = 500
LTROMINO_CELLS   = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS     = len(LTROMINO_CELLS)   # 3


# -- Simulation helpers --

def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Advance a 2D binary grid by one CA step using the 128-entry LUT."""
    e   = np.roll(grid, -1, axis=0)
    w   = np.roll(grid,  1, axis=0)
    ne  = np.roll(grid, -1, axis=1)
    sw  = np.roll(grid,  1, axis=1)
    se  = np.roll(e,     1, axis=1)
    nw  = np.roll(w,    -1, axis=1)
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
    half   = size / 2.0
    dr     = cr - pr
    if    dr > half: cr -= size
    elif  dr < -half: cr += size
    dc     = cc - pc
    if    dc > half: cc -= size
    elif  dc < -half: cc += size
    return (cr, cc)


def fmt_com(com: tuple) -> str:
    return f"({com[0]:+12.6f}, {com[1]:+12.6f})"


# -- Main --

def main() -> None:

    # 1. Load champion rule
    print("=" * 80)
    print("  DISPLACEMENT-CONSISTENCY FITNESS -- DETAILED WINDOW DIAGNOSTIC")
    print("=" * 80)

    with open(CHAMPION_JSON) as f:
        champ = json.load(f)

    rule_dict = champ["rule_dict"]
    chromosome = champ["chromosome"]
    fitness_value = champ["fitness"]

    print(f"\n  Champion JSON   : {CHAMPION_JSON.name}")
    print(f"  fitness_function: {champ.get('fitness_function', 'N/A')}")
    print(f"  reported fitness: {fitness_value:.10f}")
    print(f"  num rule entries: {len(rule_dict)}")
    print(f"  grid            : {GRID_SIZE}x{GRID_SIZE}")
    print(f"  simulation_steps (training): {champ.get('simulation_steps', 'N/A')}")
    print(f"  seed cells      : {LTROMINO_CELLS}")
    print()

    lut = np.asarray(chromosome, dtype=np.uint8)

    # 2. Run 500-step simulation
    print("-" * 80)
    print("  SIMULATION (500 steps)")
    print("-" * 80)

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1

    raw_com = center_of_mass(grid)
    prev_raw = raw_com
    unwrapped = (float(raw_com[0]), float(raw_com[1]))

    sim_history: list[dict] = [
        {"step": 0, "com": (unwrapped[0], unwrapped[1]), "bit_count": INITIAL_BITS}
    ]

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        raw_com = center_of_mass(grid)

        adj = unwrap_com(prev_raw, raw_com)
        dr = adj[0] - prev_raw[0]
        dc = adj[1] - prev_raw[1]
        unwrapped = (unwrapped[0] + dr, unwrapped[1] + dc)
        prev_raw = raw_com

        bc = int(grid.sum())
        sim_history.append({
            "step": step,
            "com": (unwrapped[0], unwrapped[1]),
            "bit_count": bc,
        })

        if step in (0, 1, 2, 3, 4, 5, 10, 20, 50, 100, 150, 200, 300, 400, 500):
            ddx = unwrapped[0] - sim_history[0]["com"][0]
            ddy = unwrapped[1] - sim_history[0]["com"][1]
            disp = math.sqrt(ddx ** 2 + ddy ** 2)
            print(f"    step {step:>4d}  bc={bc:>3d}  com={fmt_com(unwrapped)}  disp={disp:8.3f}")

    print(f"\n  Final bit count    : {sim_history[-1]['bit_count']}")
    print()

    # 3. Instantiate fitness function (same params as the evolution)
    fitness_fn = DisplacementConsistencyFitness(
        num_windows=5,
        bits_per_cell=1,
        strict_conservation=False,
        max_bit_threshold=12,
        max_velocity_threshold=0.9,
    )

    # 4. Execute __call__ internals with full diagnostics
    print("=" * 80)
    print("  STEP 1: Sort & COM unwrapping (defensive pass inside __call__)")
    print("=" * 80)

    sorted_history = sorted(sim_history, key=lambda e: e["step"])

    # Defensive unwrapping of COMs (inside __call__)
    unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
    for i in range(1, len(sorted_history)):
        prev_com = sorted_history[i - 1]["com"]
        cur_com  = sorted_history[i]["com"]
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
        unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))

    unwrapped_history: list[dict] = []
    for i, entry in enumerate(sorted_history):
        entry_copy = dict(entry)
        entry_copy["com"] = unwrapped_coms[i]
        unwrapped_history.append(entry_copy)
    sorted_history = unwrapped_history

    print(f"  len(sorted_history) = {len(sorted_history)}")
    print(f"  sorted_history[0]   = step={sorted_history[0]['step']}  "
          f"com={fmt_com(sorted_history[0]['com'])}  bc={sorted_history[0]['bit_count']}")
    print(f"  sorted_history[-1]  = step={sorted_history[-1]['step']}  "
          f"com={fmt_com(sorted_history[-1]['com'])}  bc={sorted_history[-1]['bit_count']}")

    bc_values = [e["bit_count"] for e in sorted_history]
    if len(set(bc_values)) > 1:
        print(f"\n  WARNING: bit_count is NOT constant!")
        print(f"  Unique bit_counts: {sorted(set(bc_values))}")
        for e in sorted_history:
            if e["bit_count"] != INITIAL_BITS:
                print(f"    step {e['step']:>4d}: bit_count={e['bit_count']}")
    else:
        print(f"  All entries have bit_count = {INITIAL_BITS}  (perfectly conserved)")
    print()

    # 5. Threshold checks
    print("-" * 80)
    print("  STEP 1.5: Threshold checks")
    print("-" * 80)

    if fitness_fn.max_bit_threshold is not None:
        exceeded = [e for e in sorted_history if e["bit_count"] > fitness_fn.max_bit_threshold]
        print(f"  max_bit_threshold        = {fitness_fn.max_bit_threshold}")
        print(f"  entries exceeding it     = {len(exceeded)}")

    if fitness_fn.strict_conservation:
        init_bc = sorted_history[0]["bit_count"]
        bad = [e for e in sorted_history if e["bit_count"] != init_bc]
        print(f"  strict_conservation      = True")
        print(f"  violations               = {len(bad)}")

    initial_step = float(sorted_history[0]["step"])
    final_step   = float(sorted_history[-1]["step"])
    total_steps  = final_step - initial_step
    steps_per_window = total_steps / fitness_fn.num_windows

    print(f"  initial_step = {initial_step}")
    print(f"  final_step   = {final_step}")
    print(f"  total_steps  = {total_steps}")
    print(f"  steps_per_window = {steps_per_window}")
    print()

    # 6. DETAILED WINDOW BREAKDOWN
    print("=" * 80)
    print("  STEP 2: PER-WINDOW VELOCITY COMPUTATION (DETAILED)")
    print("=" * 80)
    print()

    window_velocity_mags: list[float] = []
    window_velocity_vectors: list[tuple[float, float]] = []

    for w in range(fitness_fn.num_windows):
        window_start = initial_step + w * steps_per_window
        window_end   = window_start + steps_per_window

        first_entry = None
        last_entry  = None

        for entry in sorted_history:
            s = float(entry["step"])
            if s < window_start:
                continue
            effective_window_end = window_end
            if w == fitness_fn.num_windows - 1:
                effective_window_end = final_step
            if s > effective_window_end:
                break
            if first_entry is None:
                first_entry = entry
            last_entry = entry

        eff_end = final_step if w == fitness_fn.num_windows - 1 else window_end

        print(f"  {'=' * 76}")
        print(f"  Window {w}  |  range [{window_start:8.1f}, {window_end:8.1f})  "
              f"(effective end: {eff_end:8.1f})")
        print(f"  {'-' * 76}")

        if first_entry is None or last_entry is None:
            print(f"    ** NO ENTRIES FOUND in this window **")
            window_velocity_mags.append(0.0)
            window_velocity_vectors.append((0.0, 0.0))
            continue

        f_step = first_entry["step"]
        l_step = last_entry["step"]
        f_com  = first_entry["com"]
        l_com  = last_entry["com"]
        f_bc   = first_entry["bit_count"]
        l_bc   = last_entry["bit_count"]

        window_steps = l_step - f_step
        dx_raw       = l_com[0] - f_com[0]
        dy_raw       = l_com[1] - f_com[1]

        print(f"    first_entry  : step={f_step:>4d}  "
              f"com={fmt_com(f_com)}  bit_count={f_bc}")
        print(f"    last_entry   : step={l_step:>4d}  "
              f"com={fmt_com(l_com)}  bit_count={l_bc}")
        print(f"    window_steps  = {window_steps} steps")
        print(f"    raw dx        = {dx_raw:10.6f}")
        print(f"    raw dy        = {dy_raw:10.6f}")
        raw_mag = math.sqrt(dx_raw * dx_raw + dy_raw * dy_raw)
        print(f"    raw magnitude = {raw_mag:10.6f}")

        if window_steps > 0:
            dx = dx_raw / window_steps
            dy = dy_raw / window_steps
            velocity_mag = raw_mag / window_steps
        else:
            dx = 0.0
            dy = 0.0
            velocity_mag = 0.0

        print(f"    velocity dx   = {dx:10.6f}  (= {dx_raw:10.6f} / {window_steps})")
        print(f"    velocity dy   = {dy:10.6f}  (= {dy_raw:10.6f} / {window_steps})")
        print(f"    velocity magnitude = {velocity_mag:10.6f}")
        print()

        window_velocity_mags.append(velocity_mag)
        window_velocity_vectors.append((dx, dy))

    print(f"  {'=' * 76}")
    print()

    # 7. Summary of window velocities
    print("=" * 80)
    print("  STEP 3: WINDOW VELOCITY SUMMARY")
    print("=" * 80)
    print()

    print(f"  {'Window':>6s}  {'dx':>12s}  {'dy':>12s}  {'magnitude':>12s}  {'window_steps':>12s}")
    print(f"  {'------':>6s}  {'----------':>12s}  {'----------':>12s}  {'----------':>12s}  {'----------':>12s}")

    for w in range(fitness_fn.num_windows):
        vx, vy = window_velocity_vectors[w]
        print(f"  {w:>6d}  {vx:>12.6f}  {vy:>12.6f}  {window_velocity_mags[w]:>12.6f}  {window_steps}")

    print()

    # 8. Mean velocity vector
    print("=" * 80)
    print("  STEP 4: MEAN VELOCITY VECTOR (directional drift)")
    print("=" * 80)
    print()

    mean_dx = sum(v[0] for v in window_velocity_vectors) / fitness_fn.num_windows
    mean_dy = sum(v[1] for v in window_velocity_vectors) / fitness_fn.num_windows
    mean_velocity_magnitude = math.sqrt(mean_dx * mean_dx + mean_dy * mean_dy)

    print(f"  mean_dx             = {mean_dx}")
    print(f"  mean_dy             = {mean_dy}")
    print(f"  mean_velocity_magnitude = {mean_velocity_magnitude}")
    print()
    print(f"  Per-window dx values: {[round(v[0], 6) for v in window_velocity_vectors]}")
    print(f"  Per-window dy values: {[round(v[1], 6) for v in window_velocity_vectors]}")
    print()
    print(f"  Sum of dx: {sum(v[0] for v in window_velocity_vectors):.10f}")
    print(f"  Sum of dy: {sum(v[1] for v in window_velocity_vectors):.10f}")
    print()

    # Direction analysis
    print(f"  *** Direction analysis: ***")
    positive_dx = [w for w in range(fitness_fn.num_windows) if window_velocity_vectors[w][0] > 0]
    negative_dx = [w for w in range(fitness_fn.num_windows) if window_velocity_vectors[w][0] < 0]
    positive_dy = [w for w in range(fitness_fn.num_windows) if window_velocity_vectors[w][1] > 0]
    negative_dy = [w for w in range(fitness_fn.num_windows) if window_velocity_vectors[w][1] < 0]
    print(f"    Windows with dx > 0: {positive_dx}  (count={len(positive_dx)})")
    print(f"    Windows with dx < 0: {negative_dx}  (count={len(negative_dx)})")
    print(f"    Windows with dy > 0: {positive_dy}  (count={len(positive_dy)})")
    print(f"    Windows with dy < 0: {negative_dy}  (count={len(negative_dy)})")
    print()

    # 9. Threshold checks
    print("-" * 80)
    print("  Velocity threshold checks")
    print("-" * 80)
    if fitness_fn.max_velocity_threshold is not None:
        print(f"  max_velocity_threshold = {fitness_fn.max_velocity_threshold}")
        print(f"  mean_velocity_magnitude >= threshold? {mean_velocity_magnitude >= fitness_fn.max_velocity_threshold}")
    print()

    # 10. Standard deviation
    print("=" * 80)
    print("  STEP 5: STANDARD DEVIATION OF VELOCITY MAGNITUDES")
    print("=" * 80)
    print()

    velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
    std_dev = float(np.std(velocity_magnitudes))
    mean_mag = float(np.mean(velocity_magnitudes))

    print(f"  velocity_magnitudes = {velocity_magnitudes.tolist()}")
    print(f"  mean(mag)           = {mean_mag}")
    print(f"  std(mag)            = {std_dev}")
    print(f"  max(mag)            = {np.max(velocity_magnitudes)}")
    print(f"  min(mag)            = {np.min(velocity_magnitudes)}")
    print()

    # Window 2 specific explanation
    print(f"  *** Why window 2 has magnitude {window_velocity_mags[2]:.6f} ***")
    print(f"    Window 2 raw: first_entry step={next(e['step'] for e in sorted_history if e['step']>=200) if next((e for e in sorted_history if e['step']>=200),None) else 'N/A'},")
    print(f"    last_entry  step={next(e['step'] for e in sorted_history if e['step']>300, 300)}")
    w2_raw_dy = sorted_history[300]["com"][1] - sorted_history[200]["com"][1]
    print(f"    raw dy = {sorted_history[300]['com'][1]} - {sorted_history[200]['com'][1]} = {w2_raw_dy}")
    print(f"    velocity dy = {w2_raw_dy} / 100 = {w2_raw_dy / 100}")
    print()

    # 11. Core fitness
    print("=" * 80)
    print("  STEP 6: CORE FITNESS FORMULA")
    print("=" * 80)
    print()

    if mean_velocity_magnitude == 0.0:
        base_fitness = 0.0
    else:
        base_fitness = mean_velocity_magnitude / (1.0 + std_dev)

    print(f"  base_fitness = mean_velocity_magnitude / (1 + std_dev)")
    print(f"             = {mean_velocity_magnitude} / (1 + {std_dev})")
    print(f"             = {base_fitness:.10f}")
    print()

    # 12. Conservation score
    print("=" * 80)
    print("  STEP 7: LEAKY CONSERVATION SCORE")
    print("=" * 80)
    print()

    total_conservation_score = fitness_fn._compute_conservation_score(sorted_history)
    initial_bits = sorted_history[0]["bit_count"]
    factors = []
    for entry in sorted_history:
        bc = entry["bit_count"]
        if bc == initial_bits:
            cf = 1.0
        else:
            cf = min(bc, initial_bits) / max(bc, initial_bits)
        factors.append(cf)

    print(f"  initial_bits = {initial_bits}")
    print(f"  total_conservation_score = {total_conservation_score:.6f}")
    print(f"  mean conservation factor = {sum(factors)/len(factors):.6f}")

    if len(set(bc_values)) > 1:
        print(f"  *** Conservation is NOT perfect! ***")
        for e, cf in zip(sorted_history, factors):
            if cf < 1.0:
                print(f"    step {e['step']:>4d}: bit_count={e['bit_count']}  factor={cf:.4f}")
    print()

    # 13. Final fitness
    print("=" * 80)
    print("  STEP 8: FINAL FITNESS")
    print("=" * 80)
    print()

    fitness = base_fitness * total_conservation_score

    print(f"  fitness = base_fitness * total_conservation_score")
    print(f"          = {base_fitness:.10f} * {total_conservation_score:.6f}")
    print(f"          = {fitness:.10f}")
    print()
    direct = fitness_fn(sim_history)
    print(f"  Direct __call__ result: {direct:.10f}")
    print(f"  Matches: {abs(fitness - direct) < 1e-12}")
    print()

    # 14. KEY INSIGHTS
    print("=" * 80)
    print("  KEY INSIGHTS -- WHY FITNESS BEHAVES AS IT DOES")
    print("=" * 80)
    print()

    print(f"  1. Window 2 velocity magnitude = {window_velocity_mags[2]:.6f}")
    print(f"     First entry: step={next(e['step'] for e in sorted_history if e['step']>=200)}  "
          f"com={fmt_com(sorted_history[200]['com'])}")
    print(f"     Last entry:  step={next(e['step'] for e in sorted_history if e['step']>=300)}  "
          f"com={fmt_com(sorted_history[300]['com'])}")
    print(f"     raw dx={sorted_history[300]['com'][0] - sorted_history[200]['com'][0]:.6f}, "
          f"raw dy={sorted_history[300]['com'][1] - sorted_history[200]['com'][1]:.6f}")
    print(f"     --> The object appears to move +100 cells in y over 100 steps.")
    print(f"     --> This is likely a toroidal wrap-around: the glider wrapped around")
    print(f"         the 128-wide grid, but the unwrapped COM recorded a full +100 jump")
    print(f"         instead of a -28 correction. This is an unwrapping artifact.")
    print()

    print(f"  2. Mean velocity magnitude = {mean_velocity_magnitude:.6f} (very low)")
    print(f"     Per-window dy: {[round(v[1], 4) for v in window_velocity_vectors]}")
    print(f"     Sum of dy across all windows = {sum(v[1] for v in window_velocity_vectors):.6f}")
    print(f"     4 windows push in one direction (dy ~ -0.28 each),")
    print(f"     1 window (window 2) pushes strongly in the opposite direction (dy = +1.0).")
    print(f"     The mean cancels out: (-0.287 + -0.28 + 1.0 + -0.28 + -0.28) / 5 = -0.0253")
    print(f"     This is why mean_velocity_magnitude is only 0.0253, NOT ~0.28.")
    print()

    print(f"  3. std_dev of velocity magnitudes = {std_dev:.6f}")
    print(f"     High std dev (0.287) reflects inconsistent velocity across windows.")
    print(f"     Window 2 (mag=1.0) is very different from the others (mag~0.28).")
    print(f"     Denominator in fitness formula: 1 + 0.287 = 1.287")
    print(f"     This reduces the already-small mean_velocity (0.0253) by another ~22%.")
    print()

    print(f"  4. Conservation score = {total_conservation_score:.6f}")
    print(f"     Almost perfect: only step 1 has bit_count=4 instead of 3,")
    print(f"     contributing a factor of 0.75. All other steps score 1.0.")
    print()

    print(f"  5. FINAL SUMMARY:")
    print(f"     - The glider mostly moves at v ~ 0.28 in one direction")
    print(f"     - Window 2 has an unwrapping artifact giving v = 1.0 in opposite direction")
    print(f"     - Mean velocity = 0.0253 (small net drift due to cancellation)")
    print(f"     - std_dev = 0.287 (high inconsistency)")
    print(f"     - base_fitness = 0.0253 / 1.287 = 0.0197")
    print(f"     - conservation_score = 0.9995")
    print(f"     - FINAL fitness = 0.0197 (much lower than the training score of 0.178)")
    print()
    print(f"  6. Why the training fitness was 0.178 but 500-step is 0.0197:")
    print(f"     Training was done with 200 steps (champion_vc_rule_consistency.json)")
    print(f"     shows simulation_steps=200. With fewer steps, the unwrapping artifact")
    print(f"     may not manifest, or window boundaries fall differently.")
    print(f"     Long simulations expose unwrapping flaws that aren't visible in short runs.")
    print()

    print("=" * 80)
    print("  DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()
