#!/usr/bin/env python3
"""
experiment_250_hex_decomposition.py
Rigorous single-bit decomposition test for the 2D hex v=0.469c glider.

Determines whether the iter_222 champion glider is:
(a) genuinely bound with binding energy > 0, or
(b) a non-interacting composite of independent single-bit trajectories.

This experiment is Sub-Goal 250.1 of Phase 250 and holds ABSOLUTE PRIORITY.
No 3D FCC non-additive LUT construction may proceed until this verdict is reached.
"""

import json
import sys
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid

GRID_SIZE = 128
STEPS = 500
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]
CHAMPION_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"
OUTPUT_PATH = PROJECT_ROOT / "archive" / "iter_250" / "results" / "hex_decomposition.json"


def unwrap_cells(prev_unwrapped_com, raw_cells, grid_size):
    """Find periodic images of raw_cells closest to prev_unwrapped_com."""
    if not raw_cells:
        return []
    pr, pc = prev_unwrapped_com
    unwrapped = []
    for r, c in raw_cells:
        best_r, best_c = r, c
        best_dist = float('inf')
        for dr in (-grid_size, 0, grid_size):
            for dc in (-grid_size, 0, grid_size):
                rr = r + dr
                cc = c + dc
                dist = (rr - pr) ** 2 + (cc - pc) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_r, best_c = rr, cc
        unwrapped.append((best_r, best_c))
    return unwrapped


def simulate(lut, seed_cells, steps=STEPS, grid_size=GRID_SIZE):
    """Run CA simulation with robust unwrapped COM tracking.
    
    Returns:
        history: list of dicts with step, unwrapped_com, bit_count, active_cells
        grid_history: list of grid arrays at each timestep
    """
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in seed_cells:
        grid[r, c] = 1
    
    # Initial state
    raw_cells = sorted((int(r), int(c)) for r, c in zip(*np.where(grid > 0)))
    initial_com = (
        float(np.mean([c[0] for c in raw_cells])) if raw_cells else 0.0,
        float(np.mean([c[1] for c in raw_cells])) if raw_cells else 0.0
    )
    unwrapped_com = initial_com
    
    history = [{
        'step': 0,
        'unwrapped_com': list(unwrapped_com),
        'bit_count': len(raw_cells),
        'active_cells': [list(c) for c in raw_cells]
    }]
    grid_history = [grid.copy()]
    
    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        grid_history.append(grid.copy())
        
        raw_cells = sorted((int(r), int(c)) for r, c in zip(*np.where(grid > 0)))
        
        if raw_cells:
            unwrapped_cells = unwrap_cells(unwrapped_com, raw_cells, grid_size)
            unwrapped_com = (
                float(np.mean([c[0] for c in unwrapped_cells])),
                float(np.mean([c[1] for c in unwrapped_cells]))
            )
        # else: keep previous unwrapped_com (pattern extinct)
        
        history.append({
            'step': t,
            'unwrapped_com': list(unwrapped_com),
            'bit_count': len(raw_cells),
            'active_cells': [list(c) for c in raw_cells]
        })
    
    return history, grid_history


def compute_velocity(history):
    """Compute average velocity from unwrapped COM trajectory."""
    if len(history) < 2:
        return 0.0, (0.0, 0.0)
    
    h0 = history[0]
    hf = history[-1]
    dt = hf['step'] - h0['step']
    
    dx = hf['unwrapped_com'][0] - h0['unwrapped_com'][0]
    dy = hf['unwrapped_com'][1] - h0['unwrapped_com'][1]
    
    speed = np.sqrt(dx * dx + dy * dy) / dt
    velocity = (dx / dt, dy / dt)
    return float(speed), (float(velocity[0]), float(velocity[1]))


def main():
    print("=" * 78)
    print("  EXPERIMENT 250: 2D HEX DECOMPOSITION CHECK")
    print("  Phase 250 Sub-Goal 250.1 — ABSOLUTE PRIORITY")
    print("=" * 78)
    
    # ── Step 1: Load champion rule ────────────────────────────────────────────
    print("\n[1] Loading champion rule from iter_222...")
    with open(CHAMPION_PATH) as f:
        data = json.load(f)
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)
    print(f"    Loaded rule with {len(rule_dict)} non-identity mappings")
    print(f"    Seed cells: {SEED_CELLS}")
    
    # ── Step 2: Full 3-bit glider ─────────────────────────────────────────────
    print(f"\n[2] Running FULL 3-bit glider for {STEPS} steps...")
    full_hist, full_grids = simulate(lut, SEED_CELLS, steps=STEPS)
    
    full_speed, full_velocity = compute_velocity(full_hist)
    full_initial_bits = full_hist[0]['bit_count']
    full_final_bits = full_hist[-1]['bit_count']
    full_max_bits = max(h['bit_count'] for h in full_hist)
    full_min_bits = min(h['bit_count'] for h in full_hist)
    full_bit_conserving = all(h['bit_count'] == full_initial_bits for h in full_hist)
    
    print(f"    Initial bits: {full_initial_bits}")
    print(f"    Final bits:   {full_final_bits}")
    print(f"    Max bits:     {full_max_bits}")
    print(f"    Min bits:     {full_min_bits}")
    print(f"    Bit-conserving: {full_bit_conserving}")
    print(f"    Speed: {full_speed:.6f} c")
    print(f"    Velocity vector: ({full_velocity[0]:.6f}, {full_velocity[1]:.6f})")
    
    # Show pattern snapshots
    print("\n    Pattern snapshots (active cells):")
    for t in [0, 10, 50, 100, 200, 300, 400, 500]:
        cells = full_hist[t]['active_cells']
        bc = full_hist[t]['bit_count']
        com = full_hist[t]['unwrapped_com']
        print(f"      t={t:4d}: {bc} bits, COM=({com[0]:.2f},{com[1]:.2f}), cells={cells}")
    
    # ── Step 3: Single-bit runs ───────────────────────────────────────────────
    print(f"\n[3] Running each of {len(SEED_CELLS)} seed bits INDIVIDUALLY...")
    single_results = {}
    
    for i, cell in enumerate(SEED_CELLS):
        print(f"\n    [3.{i+1}] Single bit at {cell}...")
        hist, grids = simulate(lut, [cell], steps=STEPS)
        speed, velocity = compute_velocity(hist)
        
        final_bits = hist[-1]['bit_count']
        max_bits = max(h['bit_count'] for h in hist)
        survives = final_bits > 0
        
        print(f"      Initial bits: 1")
        print(f"      Final bits:   {final_bits}")
        print(f"      Max bits:     {max_bits}")
        print(f"      Survives:     {survives}")
        print(f"      Speed:        {speed:.6f} c")
        print(f"      Velocity:     ({velocity[0]:.6f}, {velocity[1]:.6f})")
        
        # Show snapshots
        for t in [0, 10, 50, 100, 200, 300, 400, 500]:
            cells = hist[t]['active_cells']
            bc = hist[t]['bit_count']
            com = hist[t]['unwrapped_com']
            print(f"        t={t:4d}: {bc} bits, COM=({com[0]:.2f},{com[1]:.2f}), cells={cells}")
        
        single_results[i] = {
            'seed_cell': list(cell),
            'history': hist,
            'grids': grids,
            'final_bits': final_bits,
            'max_bits': max_bits,
            'survives': survives,
            'speed': speed,
            'velocity': list(velocity)
        }
    
    # ── Step 4: 2-bit subset runs ─────────────────────────────────────────────
    print(f"\n[4] Running all 2-bit subsets...")
    pair_results = {}
    pair_indices = [(0, 1), (0, 2), (1, 2)]
    
    for pair_idx, (i, j) in enumerate(pair_indices):
        pair_cells = [SEED_CELLS[i], SEED_CELLS[j]]
        print(f"\n    [4.{pair_idx+1}] Pair {pair_cells}...")
        hist, grids = simulate(lut, pair_cells, steps=STEPS)
        speed, velocity = compute_velocity(hist)
        
        final_bits = hist[-1]['bit_count']
        max_bits = max(h['bit_count'] for h in hist)
        
        print(f"      Initial bits: 2")
        print(f"      Final bits:   {final_bits}")
        print(f"      Max bits:     {max_bits}")
        print(f"      Speed:        {speed:.6f} c")
        print(f"      Velocity:     ({velocity[0]:.6f}, {velocity[1]:.6f})")
        
        # Compare pair run with OR of corresponding single-bit runs
        or_mismatches = []
        for t in range(STEPS + 1):
            or_grid = np.logical_or(
                single_results[i]['grids'][t],
                single_results[j]['grids'][t]
            ).astype(np.uint8)
            if not np.array_equal(grids[t], or_grid):
                diff = int(np.abs(grids[t].astype(int) - or_grid.astype(int)).sum())
                or_mismatches.append({
                    'step': t,
                    'diff_count': diff,
                    'pair_bits': int(grids[t].sum()),
                    'or_bits': int(or_grid.sum())
                })
        
        print(f"      OR-superposition mismatches: {len(or_mismatches)}/{STEPS+1}")
        if or_mismatches:
            print(f"        First 5 mismatches:")
            for m in or_mismatches[:5]:
                print(f"          step={m['step']:4d}, pair={m['pair_bits']}, or={m['or_bits']}, diff={m['diff_count']}")
        
        pair_results[f"{i}_{j}"] = {
            'seed_cells': [list(c) for c in pair_cells],
            'final_bits': final_bits,
            'max_bits': max_bits,
            'speed': speed,
            'velocity': list(velocity),
            'or_mismatches': or_mismatches,
            'or_mismatch_count': len(or_mismatches)
        }
    
    # ── Step 5: Critical Test — 3-bit OR Superposition Comparison ─────────────
    print(f"\n[5] CRITICAL TEST: 3-bit OR superposition comparison...")
    or_mismatches_3bit = []
    
    for t in range(STEPS + 1):
        or_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
        for i in range(len(SEED_CELLS)):
            or_grid = np.logical_or(or_grid, single_results[i]['grids'][t]).astype(np.uint8)
        
        if not np.array_equal(full_grids[t], or_grid):
            diff = int(np.abs(full_grids[t].astype(int) - or_grid.astype(int)).sum())
            or_mismatches_3bit.append({
                'step': t,
                'diff_count': diff,
                'full_bits': int(full_grids[t].sum()),
                'or_bits': int(or_grid.sum())
            })
    
    or_match_count = (STEPS + 1) - len(or_mismatches_3bit)
    print(f"    Matching steps:    {or_match_count}/{STEPS+1}")
    print(f"    Mismatching steps: {len(or_mismatches_3bit)}/{STEPS+1}")
    if or_mismatches_3bit:
        print(f"    First 10 mismatches:")
        for m in or_mismatches_3bit[:10]:
            print(f"      step={m['step']:4d}, full={m['full_bits']}, or={m['or_bits']}, diff={m['diff_count']}")
    
    # ── Step 6: Binding Energy Verdict ────────────────────────────────────────
    print(f"\n[6] BINDING ENERGY VERDICT...")
    
    verdict = "PENDING"
    evidence = []
    confidence = "low"
    
    # Criterion A: Any single bit annihilates alone but survives in full glider
    any_annihilates = False
    for i, res in single_results.items():
        if not res['survives']:
            any_annihilates = True
            evidence.append(
                f"Single bit at {res['seed_cell']} ANNIHILATES when run alone "
                f"(final_bits=0) but the full glider survives with {full_final_bits} bits. "
                f"This is consistent with binding energy > 0."
            )
    
    if any_annihilates and full_final_bits > 0:
        verdict = "GENUINE_GLIDER"
        confidence = "high"
    
    # Criterion B: All bits survive alone with same velocity as full glider AND OR matches
    all_survive = all(res['survives'] for res in single_results.values())
    
    if all_survive and len(or_mismatches_3bit) == 0:
        velocities_match = True
        for i, res in single_results.items():
            v_diff = np.sqrt(
                (res['velocity'][0] - full_velocity[0])**2 +
                (res['velocity'][1] - full_velocity[1])**2
            )
            if v_diff > 0.001:
                velocities_match = False
                evidence.append(
                    f"Single bit at {res['seed_cell']} survives alone with "
                    f"velocity ({res['velocity'][0]:.4f}, {res['velocity'][1]:.4f}), "
                    f"which differs from full glider velocity "
                    f"({full_velocity[0]:.4f}, {full_velocity[1]:.4f}). "
                    f"Difference = {v_diff:.4f}. This is consistent with binding energy > 0."
                )
        
        if velocities_match:
            verdict = "NON_INTERACTING_COMPOSITE"
            confidence = "high"
            evidence.append(
                f"All {len(SEED_CELLS)} individual bits survive when run alone "
                f"with velocities matching the full glider velocity "
                f"({full_velocity[0]:.4f}, {full_velocity[1]:.4f})."
            )
            evidence.append(
                f"The full 3-bit glider matches the logical OR superposition "
                f"of the three individual 1-bit runs at ALL {STEPS+1} timesteps. "
                f"This is consistent with binding energy = 0."
            )
        else:
            if verdict == "PENDING":
                verdict = "GENUINE_GLIDER"
                confidence = "medium"
    
    # Criterion C: OR superposition mismatches exist
    if len(or_mismatches_3bit) > 0:
        if verdict == "PENDING":
            verdict = "GENUINE_GLIDER"
            confidence = "medium"
        evidence.append(
            f"The full glider differs from the OR superposition of individual "
            f"1-bit runs at {len(or_mismatches_3bit)} out of {STEPS+1} timesteps. "
            f"This demonstrates that the bits interact via their neighborhoods."
        )
    
    # Criterion D: Check 2-bit subset behavior
    for key, res in pair_results.items():
        if res['or_mismatch_count'] > 0:
            evidence.append(
                f"2-bit subset {res['seed_cells']} shows "
                f"{res['or_mismatch_count']} OR-superposition mismatches, "
                f"indicating pairwise interaction."
            )
    
    if verdict == "PENDING":
        verdict = "UNCERTAIN"
        evidence.append("Could not determine a definitive verdict from the available tests.")
    
    print(f"\n    VERDICT: {verdict}")
    print(f"    Confidence: {confidence}")
    print(f"\n    Evidence:")
    for e in evidence:
        print(f"      - {e}")
    
    # ── Step 7: Save results ──────────────────────────────────────────────────
    print(f"\n[7] Saving results to {OUTPUT_PATH}...")
    
    def sample_trajectory(hist, interval=50):
        return [
            {
                'step': h['step'],
                'unwrapped_com': h['unwrapped_com'],
                'bit_count': h['bit_count'],
                'active_cells': h['active_cells']
            }
            for h in hist[::interval]
        ]
    
    output = {
        'experiment': '250_hex_decomposition',
        'grid_size': GRID_SIZE,
        'steps': STEPS,
        'seed_cells': [list(c) for c in SEED_CELLS],
        'champion_rule': str(CHAMPION_PATH),
        'full_glider': {
            'initial_bits': full_initial_bits,
            'final_bits': full_final_bits,
            'max_bits': full_max_bits,
            'min_bits': full_min_bits,
            'bit_conserving': full_bit_conserving,
            'speed': full_speed,
            'velocity': list(full_velocity),
            'trajectory_sample': sample_trajectory(full_hist)
        },
        'single_bit_runs': {
            str(i): {
                'seed_cell': res['seed_cell'],
                'survives': res['survives'],
                'final_bits': res['final_bits'],
                'max_bits': res['max_bits'],
                'speed': res['speed'],
                'velocity': res['velocity'],
                'trajectory_sample': sample_trajectory(res['history'])
            }
            for i, res in single_results.items()
        },
        'pair_runs': {
            key: {
                'seed_cells': res['seed_cells'],
                'final_bits': res['final_bits'],
                'max_bits': res['max_bits'],
                'speed': res['speed'],
                'velocity': res['velocity'],
                'or_mismatch_count': res['or_mismatch_count'],
                'or_mismatch_first_10': res['or_mismatches'][:10]
            }
            for key, res in pair_results.items()
        },
        'superposition_comparison': {
            'matching_steps': or_match_count,
            'mismatching_steps': len(or_mismatches_3bit),
            'mismatch_first_20': or_mismatches_3bit[:20]
        },
        'verdict': verdict,
        'confidence': confidence,
        'evidence': evidence
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"    Saved.")
    print(f"\n{'=' * 78}")
    print(f"  FINAL VERDICT: {verdict} (confidence: {confidence})")
    print(f"{'=' * 78}")
    
    return verdict


if __name__ == "__main__":
    main()
