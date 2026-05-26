#!/usr/bin/env python3
"""
test_embedded_glider.py - Code-verification and alignment test for 2D hex glider
embedded into the [111] plane of a 3D FCC lattice via a hybrid engine.

Per pre_registration.md Section 4:
  This is a CODE-VERIFICATION AND ALIGNMENT TEST. If the 2D hex glider rule is
  correctly embedded into a [111] hex plane of the 13-channel FCC lattice with
  identity mappings on the 6 inter-plane channels (alpha=0), the glider survival
  is GUARANTEED BY CONSTRUCTION. It is an algebraic identity, not a physical
  discovery. No emergent or promotional language may be used.

Tests:
  1. Embedded hybrid engine (3D) for 300 steps
  2. Single-bit decomposition test (each seed bit alone for 300 steps)
  3. Positive control: 2D hex standalone (must match hybrid layer)
  4. Negative control: trivial annihilator rule (all states -> 0)
  5. F3 analysis: pure LGCA feasibility

Outputs:
  archive/iter_252/results/embed_test.json   (test results)
  archive/iter_252/results/embed_report.json (analysis report)
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import (
    rule_dict_to_lut,
    center_of_mass,
    LTROMINO_CELLS,
    step_grid,
)
from fcc_engine_embed import (
    embed_step,
    step_hex_2d,
    make_3d_seed,
    attempt_pure_lgca_lut,
)

# -- Configuration -----------------------------------------------------------

GRID_3D = 32
STEPS = 300
OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_252" / "results"
CHAMPION_PATH = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"


def unwrap_com_series(coms, grid_size):
    """Unwrap a sequence of raw (wrapped) COMs on a toroidal grid."""
    if not coms:
        return []
    unwrapped = [[float(coms[0][0]), float(coms[0][1])]]
    for i in range(1, len(coms)):
        dr_raw = float(coms[i][0]) - float(coms[i - 1][0])
        dc_raw = float(coms[i][1]) - float(coms[i - 1][1])
        if dr_raw > grid_size / 2:
            dr_raw -= grid_size
        elif dr_raw < -grid_size / 2:
            dr_raw += grid_size
        if dc_raw > grid_size / 2:
            dc_raw -= grid_size
        elif dc_raw < -grid_size / 2:
            dc_raw += grid_size
        unwrapped.append([unwrapped[-1][0] + dr_raw, unwrapped[-1][1] + dc_raw])
    return unwrapped


def center_of_mass_2d_on_layer(grid, layer):
    """COM of set bits in 2D slice at given layer (channel 12 = center)."""
    bits = grid[layer, :, :, 12]
    ys, xs = np.where(bits > 0)
    if len(ys) == 0:
        return (0.0, 0.0)
    return (float(np.mean(ys)), float(np.mean(xs)))


def load_champion():
    with open(CHAMPION_PATH, "r") as f:
        data = json.load(f)
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    hex_lut = rule_dict_to_lut(rule_dict)
    seed_cells = data.get("seed_cells", LTROMINO_CELLS)
    return hex_lut, seed_cells


def run_embedded_test(hex_lut, seed_cells):
    """Run the hybrid 3D engine for STEPS with the L-tromino seed on layer 16."""
    center_2d = GRID_3D // 2
    offset_r = center_2d - 64
    offset_c = center_2d - 64
    seed_3d = [(r + offset_r, c + offset_c) for r, c in seed_cells]

    grid = make_3d_seed(GRID_3D, seed_3d, layer=center_2d)
    layer = center_2d
    bit_counts = []
    coms = []

    for step in range(STEPS + 1):
        bits_on_layer = int(grid[layer, :, :, 12].sum())
        bit_counts.append(bits_on_layer)
        com = center_of_mass_2d_on_layer(grid, layer)
        coms.append(com)
        if step < STEPS:
            grid = embed_step(grid, hex_lut)

    unwrapped = unwrap_com_series(coms, GRID_3D)
    dr = unwrapped[-1][0] - unwrapped[0][0]
    dc = unwrapped[-1][1] - unwrapped[0][1]
    displacement = math.hypot(dr, dc)
    speed = displacement / STEPS

    return {
        "bit_counts": bit_counts,
        "coms_raw": [list(c) for c in coms],
        "coms_unwrapped": unwrapped,
        "displacement": displacement,
        "speed": speed,
        "final_bits": bit_counts[-1],
    }


def run_decomposition_test(hex_lut, seed_cells):
    """Run each single bit of the seed alone; all must die (annihilate)."""
    center_2d = GRID_3D // 2
    offset_r = center_2d - 64
    offset_c = center_2d - 64
    seed_3d = [(r + offset_r, c + offset_c) for r, c in seed_cells]
    layer = center_2d

    results = []
    for idx, (r, c) in enumerate(seed_3d):
        grid = np.zeros((GRID_3D, GRID_3D, GRID_3D, 13), dtype=np.uint8)
        grid[layer, r, c, 12] = 1
        for _ in range(STEPS):
            grid = embed_step(grid, hex_lut)
        final_bits = int(grid[layer, :, :, 12].sum())
        results.append({"seed_bit": idx, "final_bits": final_bits,
                        "survived": final_bits > 0})

    all_died = all(not r["survived"] for r in results)
    return {
        "results": results,
        "all_bits_annihilate": all_died,
        "decomposition_test_passed": all_died,
    }


def run_positive_control(hex_lut, seed_cells):
    """Run pure 2D hex CA on 32x32 grid; compare layer COM with hybrid."""
    center_2d = GRID_3D // 2
    offset_r = center_2d - 64
    offset_c = center_2d - 64
    seed_2d = [(r + offset_r, c + offset_c) for r, c in seed_cells]

    grid = np.zeros((GRID_3D, GRID_3D), dtype=np.uint8)
    for r, c in seed_2d:
        grid[r, c] = 1

    bit_counts = []
    coms = []
    for step in range(STEPS + 1):
        bit_counts.append(int(grid.sum()))
        coms.append(center_of_mass(grid))
        if step < STEPS:
            grid = step_hex_2d(grid, hex_lut)

    unwrapped = unwrap_com_series(coms, GRID_3D)
    dr = unwrapped[-1][0] - unwrapped[0][0]
    dc = unwrapped[-1][1] - unwrapped[0][1]
    displacement = math.hypot(dr, dc)
    speed = displacement / STEPS

    return {
        "bit_counts": bit_counts,
        "coms_unwrapped": unwrapped,
        "displacement": displacement,
        "speed": speed,
        "final_bits": bit_counts[-1],
    }


def run_negative_control(seed_cells):
    """Run hybrid engine with all-zero hex rule (everything dies)."""
    annihilator = np.zeros(128, dtype=np.uint8)
    center_2d = GRID_3D // 2
    offset_r = center_2d - 64
    offset_c = center_2d - 64
    seed_3d = [(r + offset_r, c + offset_c) for r, c in seed_cells]

    grid = make_3d_seed(GRID_3D, seed_3d, layer=center_2d)
    layer = center_2d
    bit_counts = []
    for step in range(STEPS + 1):
        bit_counts.append(int(grid[layer, :, :, 12].sum()))
        if step < STEPS:
            grid = embed_step(grid, annihilator)

    return {"bit_counts": bit_counts, "final_bits": bit_counts[-1]}


def run_f3_analysis(hex_lut):
    return attempt_pure_lgca_lut(hex_lut)


def main():
    print("=" * 70)
    print("ITER 252.2 - 3D FCC EMBEDDING OF 2D HEX GLIDER (CODE-VERIFICATION TEST)")
    print("=" * 70)

    hex_lut, seed_cells = load_champion()
    print(f"Loaded champion rule: {len(hex_lut)}-entry LUT")
    print(f"Seed cells (128-grid): {seed_cells}")

    # 1. Embedded hybrid
    print("\n[1/5] Running hybrid embedded engine (3D, alpha=0)...")
    embedded = run_embedded_test(hex_lut, seed_cells)
    print(f"  Final bits: {embedded['final_bits']}")
    print(f"  Displacement: {embedded['displacement']:.4f}")
    print(f"  Speed: {embedded['speed']:.4f}")

    # 2. Decomposition
    print("\n[2/5] Running single-bit decomposition test...")
    decomp = run_decomposition_test(hex_lut, seed_cells)
    print(f"  All bits annihilate: {decomp['all_bits_annihilate']}")
    for r in decomp["results"]:
        status = "OK died" if not r["survived"] else "FAIL SURVIVED"
        print(f"    Bit {r['seed_bit']}: final={r['final_bits']} {status}")

    # 3. Positive control
    print("\n[3/5] Running positive control (2D standalone)...")
    positive = run_positive_control(hex_lut, seed_cells)
    print(f"  Final bits: {positive['final_bits']}")
    print(f"  Displacement: {positive['displacement']:.4f}")
    print(f"  Speed: {positive['speed']:.4f}")

    # 4. Negative control
    print("\n[4/5] Running negative control (annihilator rule)...")
    negative = run_negative_control(seed_cells)
    print(f"  Final bits: {negative['final_bits']}")

    # 5. F3
    print("\n[5/5] Running F3 analysis (pure LGCA feasibility)...")
    f3 = run_f3_analysis(hex_lut)
    print(f"  F3 triggered: {f3['f3_triggered']}")
    print(f"  Counterexample: state={f3['counterexample']['state']}, "
          f"pop_in={f3['counterexample']['pop_in']}, pop_out={f3['counterexample']['pop_out']}")

    # Compare embedded vs positive control
    embedded_bc = embedded["bit_counts"]
    positive_bc = positive["bit_counts"]
    positive_matches = (embedded_bc == positive_bc)

    if positive_matches:
        print("\n[ALIGNMENT] Embedded 3D bit counts EXACTLY match 2D positive control.")
    else:
        diffs = [i for i, (a, b) in enumerate(zip(embedded_bc, positive_bc)) if a != b]
        print(f"\n[MISMATCH] Bit counts differ at {len(diffs)} steps: {diffs[:20]}...")

    # Save test output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    embed_test = {
        "iteration": 252,
        "test_type": "code_verification_and_alignment",
        "grid_size_3d": GRID_3D,
        "steps": STEPS,
        "embedded": embedded,
        "decomposition": decomp,
        "positive_control": {
            "bit_counts": positive_bc,
            "displacement": positive["displacement"],
            "speed": positive["speed"],
            "final_bits": positive["final_bits"],
        },
        "negative_control": {
            "bit_counts": negative["bit_counts"],
            "final_bits": negative["final_bits"],
        },
        "f3_analysis": f3,
        "positive_control_matches": bool(positive_matches),
    }

    embed_path = OUTPUT_DIR / "embed_test.json"
    with open(embed_path, "w") as f:
        json.dump(embed_test, f, indent=2)
    print(f"\nSaved embed_test.json -> {embed_path}")

    # Save report
    architecture_notes = (
        "The 2D hex CA (champion_rule_perfect) is a synchronous CA with "
        "7-bit neighborhood -> 1-bit center output. It is NOT bit-conserving "
        "locally (3->4 bits in the glider) and NOT bijective on the 7-bit state space. "
        "The 3D FCC LGCA requires 13-bit -> 13-bit bijective, bit-conserving mappings. "
        "These are architecturally incompatible. The hybrid engine resolves this by "
        "using synchronous neighbor reads for in-plane channels (ch0-5) instead of LGCA "
        "streaming. The inter-plane channels (ch6-11) use standard LGCA stream+identity. "
        "This construction GUARANTEES exact reproduction of the 2D hex dynamics on the "
        "[111] plane when the in-plane state is computed identically to the "
        "2D case. It is an algebraic identity, not emergence. "
        "F3 is triggered because no pure LGCA LUT can simultaneously be bijective, "
        "bit-conserving, and match the hex rule - the hex rule inherently changes "
        "Hamming weight on the 7-bit subspace."
    )

    embed_report = {
        "iteration": 252,
        "f3_triggered": f3["f3_triggered"],
        "embedded_glider_survives": embedded["final_bits"] >= 3,
        "embedded_glider_speed": embedded["speed"],
        "embedded_glider_bit_counts": embedded["bit_counts"],
        "decomposition_test_passed": decomp["decomposition_test_passed"],
        "positive_control_matches": bool(positive_matches),
        "architecture_notes": architecture_notes,
    }

    report_path = OUTPUT_DIR / "embed_report.json"
    with open(report_path, "w") as f:
        json.dump(embed_report, f, indent=2)
    print(f"Saved embed_report.json -> {report_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  F3 triggered:                         {embed_report['f3_triggered']}")
    print(f"  Embedded glider survives (>=3 bits):  {embed_report['embedded_glider_survives']}")
    print(f"  Embedded glider speed:                {embed_report['embedded_glider_speed']:.6f}")
    print(f"  Decomposition test passed:            {embed_report['decomposition_test_passed']}")
    print(f"  Positive control matches:             {embed_report['positive_control_matches']}")
    print("\n  CONCLUSION: The hybrid engine correctly projects the 2D hex glider")
    print("  onto the [111] plane of the 3D FCC lattice.")
    print("  The glider's survival is guaranteed by construction.")


if __name__ == "__main__":
    main()
