#!/usr/bin/env python3
"""
print_diag_history.py — Diagnostic of DisplacementConsistencyFitness unwrapping.

1. Load the champion rule from archive/iter_221/results/champion_rule.json
2. Run a simulation for 500 steps with the L-tromino seed.
3. Build sim_history with RAW (toroidal) COM at each step.
4. Run DisplacementConsistencyFitness(num_windows=5) on that history.
5. Print COM at steps 0, 100, 200, 300, 400, 500 BEFORE and AFTER the
   unwrapping logic inside the fitness function.

This shows whether unwrapping actually worked, and why the velocity was
calculated as ~0.025.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from new_fitness import DisplacementConsistencyFitness


# ─── Constants ────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_221" / "results" / "champion_rule.json"
SIM_STEPS    = 500
GRID_SIZE    = 128
HALF_GRID    = GRID_SIZE / 2.0  # 64.0
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS = len(LTROMINO_CELLS)  # 3
KEY_STEPS    = [0, 100, 200, 300, 400, 500]


# ─── Simulation helpers ───────────────────────────────────────────────────────

def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Advance a 2D binary grid by one CA step using the 128-entry LUT."""
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


def center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    """Raw (toroidal) centre of mass — simple arithmetic mean of live-cell coords."""
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── 1. Load champion rule ───────────────────────────────────────────
    print("=" * 80)
    print("  LOADING CHAMPION RULE")
    print("=" * 80)
    with open(CHAMP_PATH) as f:
        champ = json.load(f)

    rule_dict = champ["rule_dict"]
    chromosome = champ["chromosome"]
    print(f"  fitness_function : {champ.get('fitness_function', 'N/A')}")
    print(f"  fitness          : {champ['fitness']:.6f}")
    print(f"  rule_dict entries: {len(rule_dict)}")
    print(f"  chromosome length: {len(chromosome)}")
    print(f"  seed_particle    : {champ.get('seed_particle', 'N/A')}")
    print(f"  seed_cells       : {champ.get('seed_cells', 'N/A')}")
    print()

    lut = np.asarray(chromosome, dtype=np.uint8)
    print(f"  LUT non-zero entries: {int(lut.sum())}/{len(lut)}")
    print()

    # ── 2. Run simulation ────────────────────────────────────────────────
    print("=" * 80)
    print("  RUNNING SIMULATION")
    print("=" * 80)
    print(f"  grid size   = {GRID_SIZE}")
    print(f"  simulation  = {SIM_STEPS} steps")
    print(f"  seed        = L-tromino at {LTROMINO_CELLS}")
    print()

    # Build grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in LTROMINO_CELLS:
        grid[r, c] = 1

    initial_com = center_of_mass(grid)
    prev_raw    = initial_com

    # ── Two histories: raw (toroidal) and unwrapped ─────────────────────
    # raw_com_history stores the raw COM for every step (needed to build sim_history)
    raw_com_history: list[tuple[float, float]] = []
    # unwrapped_com_history stores the unwrapped COM for diagnostic comparison
    unwrapped_com_history: list[tuple[float, float]] = []

    # The fitness function expects sim_history entries like:
    #   {"step": 0, "com": (r, c), "bit_count": 3}
    # We will build this from raw COMs and feed it into the fitness function.
    sim_history_raw: list[dict] = []

    unwrapped = initial_com  # cumulative unwrapped COM, starts at step 0
    unwrapped_com_history.append(unwrapped)
    sim_history_raw.append({
        "step": 0,
        "com":  (float(initial_com[0]), float(initial_com[1])),
        "bit_count": INITIAL_BITS,
    })
    raw_com_history.append(initial_com)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        raw_com = center_of_mass(grid)

        # Compute delta and apply minimum-image wrap correction
        dr = raw_com[0] - prev_raw[0]
        dc = raw_com[1] - prev_raw[1]
        # Minimum-image wrap correction
        if dr > HALF_GRID:
            dr -= GRID_SIZE
        elif dr < -HALF_GRID:
            dr += GRID_SIZE
        if dc > HALF_GRID:
            dc -= GRID_SIZE
        elif dc < -HALF_GRID:
            dc += GRID_SIZE

        unwrapped = (unwrapped[0] + dr, unwrapped[1] + dc)
        prev_raw = raw_com

        bc = int(grid.sum())

        raw_com_history.append(raw_com)
        unwrapped_com_history.append(unwrapped)
        sim_history_raw.append({
            "step": step,
            "com":  (float(raw_com[0]), float(raw_com[1])),
            "bit_count": bc,
        })

        if step in KEY_STEPS or step % 100 == 0:
            ddx = unwrapped[0] - initial_com[0]
            ddy = unwrapped[1] - initial_com[1]
            disp = math.sqrt(ddx * ddx + ddy * ddy)
            print(f"  step {step:>4}  raw_com=({raw_com[0]:10.2f},{raw_com[1]:10.2f})  "
                  f"unwrapped=({unwrapped[0]:10.2f},{unwrapped[1]:10.2f})  "
                  f"bc={bc:>2}  disp={disp:.3f}")

    print()
    total_disp = math.sqrt(
        (unwrapped_com_history[-1][0] - initial_com[0]) ** 2
        + (unwrapped_com_history[-1][1] - initial_com[1]) ** 2
    )
    print(f"  Final unwrapped COM  : ({unwrapped_com_history[-1][0]:.4f}, {unwrapped_com_history[-1][1]:.4f})")
    print(f"  Final raw COM        : ({raw_com_history[-1][0]:.4f}, {raw_com_history[-1][1]:.4f})")
    print(f"  Total displacement   : {total_disp:.4f} cells")
    print(f"  Avg velocity (raw sim): {total_disp / SIM_STEPS:.6f} cells/step")
    print()

    # ── 3. Replicate the fitness function's unwrapping logic ─────────────
    print("=" * 80)
    print("  REPLICATING FITNESS-FUNCTION UNWRAPPING ON sim_history_raw")
    print("=" * 80)
    print()

    # The fitness function does this internally:
    #   sorted_history = sorted(sim_history, key=lambda e: e["step"])
    #   unwrapped_coms = [...]  # cumulative unwrapping
    #
    # We'll do the same manually to show before/after at KEY_STEPS.

    sorted_history = sorted(sim_history_raw, key=lambda e: e["step"])

    # --- Before unwrapping: raw COMs ---
    print("  BEFORE unwrapping (raw toroidal COM from simulation):")
    print(f"  {'step':>6}  | {'com_r':>12}  | {'com_c':>12}  |  bc")
    print(f"  {'-'*6}-+-{'-'*14}-+-{'-'*14}-+-{'-'*5}")
    before_lines = []
    for entry in sorted_history:
        s = entry["step"]
        com = entry["com"]
        bc  = entry["bit_count"]
        if s in KEY_STEPS:
            line = f"  {s:>6}  | {com[0]:>12.4f}  | {com[1]:>12.4f}  |  {bc}"
            before_lines.append((s, line, com))
            print(line)
    print()

    # --- Apply the fitness function's unwrapping logic ──────────────────
    unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
    unwrap_changes: list[tuple[int, float, float]] = []  # (step, cum_dx, cum_dy from raw)

    for i in range(1, len(sorted_history)):
        prev_com = sorted_history[i - 1]["com"]
        cur_com = sorted_history[i]["com"]
        dx = cur_com[0] - prev_com[0]
        dy = cur_com[1] - prev_com[1]

        # This is the unwrapping logic from DisplacementConsistencyFitness.__call__
        if dx > 64:
            dx -= 128.0
        elif dx < -64:
            dx += 128.0
        if dy > 64:
            dy -= 128.0
        elif dy < -64:
            dy += 128.0

        new_unwrapped = (prev_com[0] + dx, prev_com[1] + dy)
        unwrapped_coms.append(new_unwrapped)

        # Track cumulative correction for key steps
        if sorted_history[i]["step"] in KEY_STEPS:
            raw_r = sorted_history[i]["com"][0]
            raw_c = sorted_history[i]["com"][1]
            corr_r = new_unwrapped[0] - raw_r
            corr_c = new_unwrapped[1] - raw_c
            if abs(corr_r) > 0.01 or abs(corr_c) > 0.01:
                unwrap_changes.append((sorted_history[i]["step"], corr_r, corr_c))

    # Build unwrapped history
    unwrapped_history: list[dict] = []
    for i, entry in enumerate(sorted_history):
        unwrapped_entry = dict(entry)
        unwrapped_entry["com"] = unwrapped_coms[i]
        unwrapped_history.append(unwrapped_entry)

    # --- After unwrapping: the COMs the fitness function actually uses ---
    print("  AFTER unwrapping (as DisplacementConsistencyFitness sees it):")
    print(f"  {'step':>6}  | {'com_r':>12}  | {'com_c':>12}  |  bc  |  correction")
    print(f"  {'-'*6}-+-{'-'*14}-+-{'-'*14}-+-{'-'*5}-+-{'-'*14}")
    after_lines = []
    for i, entry in enumerate(unwrapped_history):
        s = entry["step"]
        com = unwrapped_coms[i]
        bc  = entry["bit_count"]
        # Correction from raw to unwrapped
        raw_r, raw_c = sorted_history[i]["com"]
        corr_r = com[0] - raw_r
        corr_c = com[1] - raw_c
        corr_str = f"({corr_r:+.1f}, {corr_c:+.1f})"
        if s in KEY_STEPS:
            line = f"  {s:>6}  | {com[0]:>12.4f}  | {com[1]:>12.4f}  |  {bc}  |  {corr_str}"
            after_lines.append((s, line, com))
            print(line)
    print()

    if unwrap_changes:
        print("  Steps where unwrap correction was applied:")
        for s, cr, cc in unwrap_changes:
            print(f"    step {s:>4}: correction = ({cr:+.1f}, {cc:+.1f})")
        print()
    else:
        print("  No unwrap corrections needed at key steps.")
        print()

    # ── 4. Run DisplacementConsistencyFitness on raw sim_history ─────────
    print("=" * 80)
    print("  RUNNING DisplacementConsistencyFitness(num_windows=5)")
    print("=" * 80)
    print()

    fitness_fn = DisplacementConsistencyFitness(num_windows=5)

    # Print the fitness function's internal state
    print("  --- Inside fitness function ---")

    sh = sorted(sim_history_raw, key=lambda e: e["step"])
    initial_step = float(sh[0]["step"])
    final_step = float(sh[-1]["step"])
    total_steps = final_step - initial_step
    steps_per_window = total_steps / fitness_fn.num_windows

    print(f"  num_windows        = {fitness_fn.num_windows}")
    print(f"  total_steps        = {total_steps}")
    print(f"  steps_per_window   = {steps_per_window}")
    print()

    # Show window boundaries and which entries they cover
    print("  Window boundaries (step indices):")
    for w in range(fitness_fn.num_windows):
        w_start = initial_step + w * steps_per_window
        w_end   = initial_step + (w + 1) * steps_per_window
        print(f"    Window {w}: [{w_start:.1f}, {w_end:.1f})")
    print()

    # Show per-window velocity using the unwrapped COMs
    window_velocity_mags_unwrapped: list[float] = []
    window_velocity_vectors_unwrapped: list[tuple[float, float]] = []
    window_velocity_mags_raw: list[float] = []
    window_velocity_vectors_raw: list[tuple[float, float]] = []

    for w in range(fitness_fn.num_windows):
        window_start = initial_step + w * steps_per_window
        window_end = window_start + steps_per_window
        effective_end = window_end
        if w == fitness_fn.num_windows - 1:
            effective_end = final_step

        # Find first/last in this window (using unwrapped)
        first_u = None
        last_u = None
        first_r = None
        last_r = None
        for entry in sh:
            s = float(entry["step"])
            if s < window_start:
                continue
            if s > effective_end:
                break
            if first_u is None:
                first_u = unwrapped_history[sh.index(entry)]
                first_r = entry
            last_u = unwrapped_history[sh.index(entry)]
            last_r = entry

        if first_u is None or last_u is None:
            window_velocity_mags_unwrapped.append(0.0)
            window_velocity_vectors_unwrapped.append((0.0, 0.0))
            window_velocity_mags_raw.append(0.0)
            window_velocity_vectors_raw.append((0.0, 0.0))
            continue

        # Unwrapped displacement
        du = (
            last_u["com"][0] - first_u["com"][0],
            last_u["com"][1] - first_u["com"][1],
        )
        mag_u = math.sqrt(du[0] ** 2 + du[1] ** 2)
        w_steps = last_u["step"] - first_u["step"]
        if w_steps > 0:
            mag_u /= w_steps
            du = (du[0] / w_steps, du[1] / w_steps)
        else:
            mag_u = 0.0
        window_velocity_mags_unwrapped.append(mag_u)
        window_velocity_vectors_unwrapped.append(du)

        # Raw displacement
        dr_ = (
            last_r["com"][0] - first_r["com"][0],
            last_r["com"][1] - first_r["com"][1],
        )
        mag_r = math.sqrt(dr_[0] ** 2 + dr_[1] ** 2)
        w_steps_r = last_r["step"] - first_r["step"]
        if w_steps_r > 0:
            mag_r /= w_steps_r
            dr_ = (dr_[0] / w_steps_r, dr_[1] / w_steps_r)
        else:
            mag_r = 0.0
        window_velocity_mags_raw.append(mag_r)
        window_velocity_vectors_raw.append(dr_)

        ws_start = first_r["step"]
        ws_end = last_r["step"]
        print(f"  Window {w} [steps {ws_start:>4}–{ws_end:>4}]:")
        print(f"    raw     dx={dr_[0]:>10.6f}  dy={dr_[1]:>10.6f}  mag={mag_r:.6f}")
        print(f"    unwrapped dx={du[0]:>10.6f}  dy={du[1]:>10.6f}  mag={mag_u:.6f}")
        print()

    # Mean velocity
    mean_dx_u = sum(v[0] for v in window_velocity_vectors_unwrapped) / fitness_fn.num_windows
    mean_dy_u = sum(v[1] for v in window_velocity_vectors_unwrapped) / fitness_fn.num_windows
    mean_vel_u = math.sqrt(mean_dx_u ** 2 + mean_dy_u ** 2)

    mean_dx_r = sum(v[0] for v in window_velocity_vectors_raw) / fitness_fn.num_windows
    mean_dy_r = sum(v[1] for v in window_velocity_vectors_raw) / fitness_fn.num_windows
    mean_vel_r = math.sqrt(mean_dx_r ** 2 + mean_dy_r ** 2)

    print("  --- Mean velocity ---")
    print(f"    raw      : dx={mean_dx_r:.6f}  dy={mean_dy_r:.6f}  |vel|={mean_vel_r:.6f}")
    print(f"    unwrapped: dx={mean_dx_u:.6f}  dy={mean_dy_u:.6f}  |vel|={mean_vel_u:.6f}")
    print()

    # Std dev of magnitudes
    vel_mags_u = np.array(window_velocity_mags_unwrapped, dtype=np.float64)
    std_u = float(np.std(vel_mags_u))

    vel_mags_r = np.array(window_velocity_mags_raw, dtype=np.float64)
    std_r = float(np.std(vel_mags_r))

    print("  --- Std dev of velocity magnitudes ---")
    print(f"    raw      std = {std_r:.6f}")
    print(f"    unwrapped std = {std_u:.6f}")
    print()

    # Core fitness
    base_u = mean_vel_u / (1.0 + std_u) if mean_vel_u > 0 else 0.0
    base_r = mean_vel_r / (1.0 + std_r) if mean_vel_r > 0 else 0.0

    print("  --- Core fitness (base) ---")
    print(f"    raw      : {mean_vel_r:.6f} / (1 + {std_r:.6f}) = {base_r:.6f}")
    print(f"    unwrapped: {mean_vel_u:.6f} / (1 + {std_u:.6f}) = {base_u:.6f}")
    print()

    # Conservation score
    cons_u = fitness_fn._compute_conservation_score(unwrapped_history)
    cons_r = fitness_fn._compute_conservation_score(sorted_history)

    fitness_u = base_u * cons_u
    fitness_r = base_r * cons_r

    print("  --- Conservation score ---")
    print(f"    raw       : {cons_r:.6f}")
    print(f"    unwrapped : {cons_u:.6f}")
    print()

    print("  --- FINAL FITNESS ---")
    print(f"    raw      : {base_r:.6f} * {cons_r:.6f} = {fitness_r:.8f}")
    print(f"    unwrapped: {base_u:.6f} * {cons_u:.6f} = {fitness_u:.8f}")
    print()

    # ── 5. Call the fitness function directly and compare ────────────────
    print("=" * 80)
    print("  DIRECT fitness_fn(sim_history_raw) RESULT")
    print("=" * 80)
    direct_result = fitness_fn(sim_history_raw)
    print(f"  fitness_fn(sim_history_raw) = {direct_result}")
    print(f"  matches our unwrapped calc? {abs(direct_result - fitness_u) < 1e-12}")
    print()

    # ── 6. Summary: did unwrapping matter? ───────────────────────────────
    print("=" * 80)
    print("  SUMMARY: Did unwrapping change the result?")
    print("=" * 80)
    print()
    print(f"  Before unwrapping (raw COMs):")
    print(f"    avg velocity  = {mean_vel_r:.6f}  cells/step")
    print(f"    base fitness  = {base_r:.8f}")
    print()
    print(f"  After  unwrapping (corrected COMs):")
    print(f"    avg velocity  = {mean_vel_u:.6f}  cells/step")
    print(f"    base fitness  = {base_u:.8f}")
    print()
    if abs(mean_vel_r - mean_vel_u) > 1e-6:
        ratio = mean_vel_u / mean_vel_r if mean_vel_r > 0 else float('inf')
        print(f"  >> UNWRAPPING DID MATTER!")
        print(f"  >> Raw avg velocity = {mean_vel_r:.6f}, Unwrapped avg velocity = {mean_vel_u:.6f}")
        print(f"  >> Ratio = {ratio:.4f}x")
    else:
        print(f"  >> Unwrapping had negligible effect (velocity {mean_vel_r:.8f} vs {mean_vel_u:.8f})")
        print(f"  >> This means the simulation already stored unwrapped COMs,")
        print(f"  >> or the pattern never crossed a toroidal boundary during steps 0–500.")

    # Show raw COM values for every step at 50-step intervals
    print()
    print("=" * 80)
    print("  FULL RAW COM AT 50-STEP INTERVALS (to see toroidal wrapping)")
    print("=" * 80)
    print(f"  {'step':>6}  | {'raw_com_r':>12}  | {'raw_com_c':>12}  | {'unwrapped_r':>12}  | {'unwrapped_c':>12}  | {'corr_r':>8}  | {'corr_c':>8}")
    print(f"  {'-'*6}-+-{'-'*14}-+-{'-'*14}-+-{'-'*14}-+-{'-'*14}-+-{'-'*9}-+-{'-'*9}")
    for step in range(0, SIM_STEPS + 1, 50):
        raw_r, raw_c = raw_com_history[step]
        uw_r, uw_c = unwrapped_com_history[step]
        raw_com = sim_history_raw[step]["com"]
        uw_com = unwrapped_coms[step]
        corr_r = uw_com[0] - raw_com[0]
        corr_c = uw_com[1] - raw_com[1]
        print(f"  {step:>6}  | {raw_r:>12.4f}  | {raw_c:>12.4f}  | {uw_r:>12.4f}  | {uw_c:>12.4f}  | {corr_r:>+8.1f}  | {corr_c:>+8.1f}")
    print()


if __name__ == "__main__":
    main()
