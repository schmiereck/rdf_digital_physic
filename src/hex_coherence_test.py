#!/usr/bin/env python3
"""
hex_coherence_test.py — Single-bit decomposition test for the 2D hex v=0.469c glider

This test determines whether the celebrated sub-light glider from iter_222
(champion_rule_perfect.json) is a genuine multi-bit coherent particle or a
non-interacting composite of single-bit trajectories.

Method:
1. Load the champion rule LUT
2. Run the full glider (L-tromino seed) for N steps
3. For each bit in the initial seed, run with ONLY that bit active
4. Compare: does the full glider's behavior match the superposition of 
   individual bit trajectories?
5. Check for multi-bit cells during propagation (necessary condition for
   genuine coherence)
"""

import json
import sys
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid, make_ltromino_grid

GRID_SIZE = 128
STEPS = 200
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]
CHAMPION_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"

HEX_DIRS = [
    (1, 0),   # E
    (1, -1),  # SE
    (0, -1),  # SW
    (-1, 0),  # W
    (-1, 1),  # NW
    (0, 1),   # NE
]


def com_and_bits(grid):
    """Return raw toroidal COM and bit count."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())


def _unwrap_com(prev_com, raw_com, grid_size=GRID_SIZE):
    """Unwrap one raw COM step relative to the previous raw COM."""
    pr, pc = prev_com
    cr, cc = raw_com
    half = grid_size / 2.0
    dr = cr - pr
    dc = cc - pc
    if dr > half:
        cr -= grid_size
    elif dr < -half:
        cr += grid_size
    if dc > half:
        cc -= grid_size
    elif dc < -half:
        cc += grid_size
    return (cr, cc)


def simulate_with_history(lut, seed_cells, steps=STEPS):
    """Run CA simulation with perfectly unwrapped COM tracking."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_cells:
        grid[r, c] = 1

    raw_c0, b0 = com_and_bits(grid)
    prev_raw = (raw_c0[0], raw_c0[1])
    hist = [{"step": 0, "com_raw": (raw_c0[0], raw_c0[1]), 
             "com_unwrapped": prev_raw, "bit_count": b0}]
    
    # Also store full grid snapshots for multi-bit analysis
    grid_history = [grid.copy()]

    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = com_and_bits(grid)
        unwrapped = _unwrap_com(prev_raw, raw_c)
        prev_raw = raw_c
        hist.append({"step": t, "com_raw": (raw_c[0], raw_c[1]),
                      "com_unwrapped": unwrapped, "bit_count": bc})
        grid_history.append(grid.copy())

    return hist, grid_history


def find_active_cells(grid):
    """Return list of (row, col) where grid > 0."""
    return sorted(zip(*np.where(grid > 0)))


def count_multi_bit_cells(grid_history):
    """
    For the hex CA, each cell's state can be 0 or 1 (binary).
    The 'bits' are per-cell, not per-direction. So multi-bit would mean
    multiple cells with state=1. But the question is whether during 
    propagation, bits from different origins co-locate.
    
    For this synchronous CA, each cell is binary (0 or 1).
    The real question is: does running all bits together produce 
    different results than the XOR superposition of individual runs?
    """
    max_bits = max(len(find_active_cells(g)) for g in grid_history)
    return max_bits


def normalize_cell(cell, grid_size=GRID_SIZE):
    """Normalize cell position to canonical representation near origin."""
    r, c = cell
    # Shift so min values are near 0
    return (r, c)


def get_canonical_pattern(cells):
    """Get canonical form of pattern by shifting to origin."""
    if not cells:
        return frozenset()
    cells = list(cells)
    min_r = min(c[0] for c in cells)
    min_c = min(c[1] for c in cells)
    return frozenset((c[0] - min_r, c[1] - min_c) for c in cells)


def get_pattern_centered(cells):
    """Get pattern centered on COM."""
    if not cells:
        return frozenset()
    cells = list(cells)
    avg_r = np.mean([c[0] for c in cells])
    avg_c = np.mean([c[1] for c in cells])
    return frozenset((int(round(c[0] - avg_r)), int(round(c[1] - avg_c))) for c in cells)


def main():
    print("=" * 72)
    print("  SINGLE-BIT DECOMPOSITION TEST: 2D Hex v=0.469c Glider")
    print("=" * 72)

    # ── Step 1: Load champion rule ────────────────────────────────────────────
    with open(CHAMPION_PATH) as f:
        data = json.load(f)
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    lut = rule_dict_to_lut(rule_dict)
    print(f"\nLoaded champion rule: {len(rule_dict)} non-identity mappings")
    print(f"Seed: {SEED_CELLS}")

    # ── Step 2: Run full glider ──────────────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  STEP 2: Full glider simulation")
    print(f"{'─' * 72}")

    full_hist, full_grids = simulate_with_history(lut, SEED_CELLS, steps=STEPS)
    
    print(f"Initial bit count: {full_hist[0]['bit_count']}")
    print(f"Final bit count:   {full_hist[-1]['bit_count']}")
    print(f"Max bit count:     {max(h['bit_count'] for h in full_hist)}")
    print(f"Min bit count:     {min(h['bit_count'] for h in full_hist)}")
    
    # Check bit conservation
    initial_bits = full_hist[0]['bit_count']
    bit_conserving = all(h['bit_count'] == initial_bits for h in full_hist)
    print(f"Bit-conserving:    {bit_conserving}")
    
    if not bit_conserving:
        non_matching = [h for h in full_hist if h['bit_count'] != initial_bits]
        print(f"Steps with different bit count: {len(non_matching)}")
        first_change = non_matching[0] if non_matching else None
        if first_change:
            print(f"  First change at step {first_change['step']}: {first_change['bit_count']} bits")

    # Initial cells
    full_initial_cells = find_active_cells(full_grids[0])
    print(f"\nInitial active cells: {full_initial_cells}")
    num_bits = len(full_initial_cells)
    print(f"Number of bits in initial glider seed: {num_bits}")

    # Track COM
    c0 = full_hist[0]['com_unwrapped']
    cf = full_hist[-1]['com_unwrapped']
    total_disp = ((cf[0]-c0[0])**2 + (cf[1]-c0[1])**2)**0.5
    avg_speed = total_disp / STEPS
    print(f"\nCOM trajectory (unwrapped):")
    print(f"  Start: ({c0[0]:.4f}, {c0[1]:.4f})")
    print(f"  End:   ({cf[0]:.4f}, {cf[1]:.4f})")
    print(f"  Total displacement: {total_disp:.4f} in {STEPS} steps")
    print(f"  Average speed: {avg_speed:.6f} c")

    # Show pattern at several timesteps
    print("\nPattern snapshots (cell positions):")
    for t in [0, 5, 10, 20, 50, 100]:
        cells = find_active_cells(full_grids[t])
        bc = full_hist[t]['bit_count']
        print(f"  t={t:4d}: {bc} bits, positions: {cells}")

    # ── Step 3: Run each bit independently ────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  STEP 3: Single-bit independent simulations")
    print(f"{'─' * 72}")

    single_bit_results = {}
    for i, (r, c) in enumerate(full_initial_cells):
        print(f"\n  Running single bit at ({r}, {c})...")
        single_seed = [(r, c)]
        single_hist, single_grids = simulate_with_history(lut, single_seed, steps=STEPS)
        
        sc0 = single_hist[0]['com_unwrapped']
        scf = single_hist[-1]['com_unwrapped']
        sdisp = ((scf[0]-sc0[0])**2 + (scf[1]-sc0[1])**2)**0.5
        sspeed = sdisp / STEPS
        
        print(f"    Initial: {single_hist[0]['bit_count']} bit(s)")
        print(f"    Final:   {single_hist[-1]['bit_count']} bit(s)")
        print(f"    Max:     {max(h['bit_count'] for h in single_hist)}")
        print(f"    COM displacement: {sdisp:.4f} (speed={sspeed:.6f}c)")
        
        # Pattern snapshots
        for t in [0, 5, 10, 20, 50, 100]:
            cells = find_active_cells(single_grids[t])
            bc = single_hist[t]['bit_count']
            print(f"    t={t:4d}: {bc} bits, {cells}")
        
        single_bit_results[i] = {
            "initial_cell": (r, c),
            "trajectory": single_hist,
            "grids": single_grids,
            "final_displacement": sdisp,
            "avg_speed": sspeed,
        }

    # ── Step 4: Compare superposition vs. full run ────────────────────────────
    print(f"\n{'─' * 72}")
    print("  STEP 4: Superposition comparison")
    print(f"{'─' * 72}")

    # Check if the full glider at any step differs from XOR superposition
    # of individual bit runs at that step
    mismatches = []
    superposition_matches = 0
    
    for t in range(STEPS + 1):
        # Compute XOR superposition of all single-bit grids at step t
        superposition = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
        for i, result in single_bit_results.items():
            superposition ^= result['grids'][t]  # XOR to see if bits overlap
        
        # Compare with full glider
        full_grid = full_grids[t]
        
        if not np.array_equal(full_grid, superposition):
            diff = np.abs(full_grid.astype(int) - superposition.astype(int))
            diff_sum = int(diff.sum())
            mismatches.append({
                "step": t,
                "diff_cells": diff_sum,
                "full_bit_count": int(full_grid.sum()),
                "superpositions_bit_count": int(superposition.sum()),
            })
        else:
            superposition_matches += 1
    
    print(f"\n  Superposition check (full glider vs XOR of single-bit runs):")
    print(f"    Steps matching: {superposition_matches}/{STEPS+1}")
    print(f"    Steps mismatching: {len(mismatches)}")
    
    if mismatches:
        print(f"\n  First 10 mismatches:")
        for m in mismatches[:10]:
            print(f"    step={m['step']:4d}, full_bits={m['full_bit_count']:3d}, "
                  f"xor_bits={m['superpositions_bit_count']:3d}, diff_cells={m['diff_cells']:3d}")

    # Alternative: check logical OR superposition (since CA is not linear, 
    # we also check if bits ever occupy the same cell in different single-bit runs)
    print(f"\n  OR-superposition analysis:")
    or_collisions = 0
    for t in range(STEPS + 1):
        # Count how many single-bit grids have a 1 at each position
        overlap = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
        for i, result in single_bit_results.items():
            overlap += result['grids'][t]
        # If any cell has overlap > 1, bits co-located in different single-bit runs
        max_overlap = int(overlap.max())
        if max_overlap > 1:
            or_collisions += 1
            if or_collisions <= 5:
                cols_with_overlap = np.where(overlap > 1)
                overlap_val = overlap[cols_with_overlap[0][0], cols_with_overlap[1][0]]
                print(f"    t={t:4d}: max overlap = {max_overlap}")
    
    print(f"  Steps with bit collision in OR-superposition: {or_collisions}")

    # ── Step 5: Check for multi-bit cells in full glider ──────────────────────
    print(f"\n{'─' * 72}")
    print("  STEP 5: Multi-bit cell analysis")
    print(f"{'─' * 72}")
    
    # In this binary CA, each cell holds 0 or 1.
    # Multi-bit cells would mean a cell value > 1, which shouldn't happen.
    # But we can check if the full glider uses states that 
    # require multi-bit neighborhood interactions.
    
    max_bits_in_full = max(h['bit_count'] for h in full_hist)
    print(f"  Max bits in full glider propagation: {max_bits_in_full}")
    print(f"  Initial bits: {initial_bits}")
    print(f"  Bit count is conserved: {bit_conserving}")
    
    # Check what neighborhood states the full glider processes
    neighborhood_states_used = set()
    for t in range(STEPS):
        grid = full_grids[t]
        # Compute neighborhood for all active cells
        e  = np.roll(grid, -1, axis=0)
        w  = np.roll(grid,  1, axis=0)
        ne = np.roll(grid, -1, axis=1)
        sw = np.roll(grid,  1, axis=1)
        se = np.roll(e,    1, axis=1)
        nw = np.roll(w,   -1, axis=1)
        states = (
            (grid.astype(np.uint16) << 6)
            | (e.astype(np.uint16)  << 5)
            | (se.astype(np.uint16) << 4)
            | (sw.astype(np.uint16) << 3)
            | (w.astype(np.uint16)  << 2)
            | (nw.astype(np.uint16) << 1)
            |  ne.astype(np.uint16)
        ).astype(np.uint8)
        
        # Only collect states of active cells
        active_mask = grid > 0
        states_used = set(states[active_mask].tolist())
        neighborhood_states_used.update(states_used)
    
    # Count multi-bit (weight > 1) neighborhood states
    weight_states = []
    for s in neighborhood_states_used:
        weight = bin(s).count('1')
        if weight > 1:
            weight_states.append((s, weight))
    
    print(f"  Total unique neighborhood states used: {len(neighborhood_states_used)}")
    print(f"  States with weight > 1: {len(weight_states)}")
    weight_states_sorted = sorted(weight_states, key=lambda x: -x[1])
    print(f"  Top weight states: {weight_states_sorted[:5]}")

    # ── Step 6: Verdict ──────────────────────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  STEP 6: VERDICT")
    print(f"{'─' * 72}")

    verdict = "PENDING"
    evidence = []
    
    # Test 1: Bit conservation
    if not bit_conserving:
        verdict = "GENUINE_GLIDER"
        evidence.append(
            f"Bit count is NOT conserved (starts at {initial_bits}, "
            f"reaches {max_bits_in_full}, ends at {full_hist[-1]['bit_count']})"
        )
        evidence.append(
            f"If the glider were a non-interacting composite, "
            f"running B independent bits would always give B bits."
        )
    
    # Test 2: Superposition matching
    if superposition_matches < STEPS + 1:
        verdict = "GENUINE_GLIDER"
        evidence.append(
            f"Full glider differs from XOR superposition of single-bit runs "
            f"at {len(mismatches)} out of {STEPS+1} steps"
        )
    
    # Test 3: Individual bit behavior
    for i, result in single_bit_results.items():
        if result['grids'][-1].sum() == 0:
            verdict = "GENUINE_GLIDER"
            evidence.append(f"Single bit at {result['initial_cell']} annihilates completely")
        elif result['grids'][-1].sum() > 1:
            evidence.append(
                f"Single bit at {result['initial_cell']} produces "
                f"{result['grids'][-1].sum()} bits (evolves, not stable)"
            )
        else:
            evidence.append(
                f"Single bit at {result['initial_cell']} remains as "
                f"{result['grids'][-1].sum()} bit(s)"
            )
    
    if not evidence and verdict == "PENDING":
        verdict = "NON_INTERACTING_COMPOSITE"
        evidence.append("All single-bit runs preserve their identity")
        evidence.append("Full glider matches XOR superposition of individual runs")
    
    print(f"\n  VERDICT: {verdict}")
    print(f"\n  Evidence:")
    for e in evidence:
        print(f"    - {e}")
    
    print(f"\n  Number of bits in glider seed: {num_bits}")
    print(f"  Period: Cannot determine from single run (trajectory analysis showed period=1 for bit_count)")
    print(f"  Glider speed: {avg_speed:.4f}c")

    # ── Step 7: Save results ──────────────────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  STEP 7: Saving results")
    print(f"{'─' * 72}")

    results_dir = PROJECT_ROOT / "archive" / "iter_249" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Build serializable results
    result_data = {
        "num_bits": num_bits,
        "glider_period": "unknown (need longer run to determine)",
        "initial_seed": list(SEED_CELLS),
        "initial_bit_count": initial_bits,
        "final_bit_count_full": full_hist[-1]['bit_count'],
        "max_bit_count_full": max(h['bit_count'] for h in full_hist),
        "bit_conserving": bit_conserving,
        "full_glider_speed": avg_speed,
        "full_glider_displacement": total_disp,
        "single_bit_results": {},
        "superposition_comparison": {
            "steps_matching": superposition_matches,
            "steps_mismatching": len(mismatches),
            "or_collision_steps": or_collisions,
        },
        "neighborhood_analysis": {
            "unique_states_used": len(neighborhood_states_used),
            "multi_bit_states_used": len(weight_states),
        },
        "verdict": verdict,
        "evidence": evidence,
    }
    
    # Serialize single-bit trajectories (just COM + bit count for compactness)
    for i, result in single_bit_results.items():
        result_data["single_bit_results"][str(i)] = {
            "initial_cell": list(result["initial_cell"]),
            "final_bit_count": int(result["grids"][-1].sum()),
            "max_bit_count": max(int(g.sum()) for g in result["grids"]),
            "final_displacement": result["final_displacement"],
            "avg_speed": result["avg_speed"],
            "trajectory_summary": [
                {"step": h["step"], "com": h["com_unwrapped"], 
                 "bit_count": h["bit_count"]}
                for h in result["trajectory"][0::20]  # Sample every 20 steps
            ],
        }
    
    # Add full glider trajectory summary
    result_data["full_trajectory_summary"] = [
        {"step": h["step"], "com": h["com_unwrapped"], 
         "bit_count": h["bit_count"]}
        for h in full_hist[0::20]
    ]
    
    output_path = results_dir / "hex_coherence_result.json"
    with open(output_path, "w") as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\n  Results saved to: {output_path}")
    print(f"\n{'=' * 72}")
    print(f"  FINAL VERDICT: {verdict}")
    print(f"{'=' * 72}")
    
    return verdict


if __name__ == "__main__":
    main()
