#!/usr/bin/env python3
"""Verify iter_248 novel species for genuine glider coherence."""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import stream, collide
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent
from src.search_3d_gliders import (
    generate_symmetric_lut, get_oh_permutations, precompute_perm_action,
    compute_orbits, compute_all_stabilizers, verify_lut,
)


def sim_bits(particle, lut, L=32, steps=32):
    """Return list of (grid, com, extent) per step."""
    grid = seed_grid(L, particle)
    bits0 = int(grid.sum())
    out = [(grid.copy(), compute_com_circular(grid)[0], bounding_extent(grid), bits0)]
    for _ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
        out.append((grid.copy(), compute_com_circular(grid)[0], bounding_extent(grid), int(grid.sum())))
    return out


def get_velocity(history, L, steps):
    cd = np.zeros(3)
    for i in range(1, len(history)):
        c0, c1 = history[i - 1][1], history[i][1]
        if c0 is None or c1 is None:
            return None
        d = c1 - c0
        for a in range(3):
            if d[a] > L / 2:
                d[a] -= L
            elif d[a] < -L / 2:
                d[a] += L
        cd += d
    return cd / steps


def multi_bit_cells(grids):
    """Count total cells with >1 bit across all steps."""
    total = 0
    for grid, _, _, _ in grids:
        packed = np.zeros(grid.shape[:3], dtype=np.uint16)
        for ch in range(12):
            packed |= (grid[..., ch].astype(np.uint16) << ch)
        counts = np.zeros(grid.shape[:3], dtype=np.int32)
        for ch in range(12):
            counts += ((packed >> ch) & 1).astype(np.int32)
        total += int((counts > 1).sum())
    return total


def run_tests(particle, lut, label=""):
    particle = [tuple(c) for c in particle]
    L, steps = 32, 32
    full_hist = sim_bits(particle, lut, L, steps)
    full_vel = get_velocity(full_hist, L, steps)
    if full_vel is None:
        return None

    # Test 1: single-bit decomposition
    t1_match_all = True
    for i, bit in enumerate(particle):
        solo_hist = sim_bits([bit], lut, L, steps)
        solo_vel = get_velocity(solo_hist, L, steps)
        if solo_vel is None or not np.allclose(solo_vel, full_vel, atol=0.01):
            t1_match_all = False
            break

    # Test 2: multi-bit collision cells
    t2_count = multi_bit_cells(full_hist)

    # Test 3: bit-removal stability
    t3_destabilizes = True
    for i in range(len(particle)):
        sub = particle[:i] + particle[i + 1:]
        sub_hist = sim_bits(sub, lut, L, steps)
        sub_vel = get_velocity(sub_hist, L, steps)
        bad = False
        for _, _, ext, bc in sub_hist:
            if bc != len(sub) or max(ext) > 6:
                bad = True
                break
        if not bad and sub_vel is not None and np.allclose(sub_vel, full_vel, atol=0.01):
            # Removing bit i did NOT destabilize
            t3_destabilizes = False
            break

    return {
        "test1_single_bit_velocity_matches": bool(t1_match_all),
        "test2_multi_bit_cell_count": int(t2_count),
        "test3_bit_removal_destabilizes": bool(t3_destabilizes),
    }


def main():
    out_dir = ROOT / "archive/iter_248/results"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "search_results.json") as f:
        data = json.load(f)
    novel = data["novel_species"]

    # Load/generate LUTs
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        ref = json.load(f)
    lut08 = np.array(ref["lut"], dtype=np.uint16)

    perms = get_oh_permutations()
    action = precompute_perm_action(perms)
    orbits, _ = compute_orbits(action)
    stabs = compute_all_stabilizers(action)

    lut_map = {"lut08": lut08}
    for s in [42, 123, 999]:
        lut = generate_symmetric_lut(seed=s, perms=perms, action=action, orbits=orbits, stabs=stabs)
        v = verify_lut(lut, action)
        assert v["bijection"] and v["bit_conserving"] and v["symmetric"]
        lut_map[f"sym_{s}"] = lut

    # Test each novel species
    results = []
    non_interacting = 0
    genuine = 0

    print("Testing novel species...")
    for i, sp in enumerate(novel):
        lut = lut_map[sp["lut"]]
        particle = [tuple(c) for c in sp["canon"]]
        tests = run_tests(particle, lut, label=f"species_{i}")
        if tests is None:
            verdict = "UNSTABLE"
        elif tests["test1_single_bit_velocity_matches"] and tests["test2_multi_bit_cell_count"] == 0:
            verdict = "NON_INTERACTING_COMPOSITE"
            non_interacting += 1
        else:
            verdict = "GENUINE"
            genuine += 1
        tests["verdict"] = verdict
        tests["species_id"] = i
        tests["lut"] = sp["lut"]
        results.append(tests)
        print(f"  species {i} ({sp['lut']}): {verdict} | t1={tests['test1_single_bit_velocity_matches']} t2={tests['test2_multi_bit_cell_count']} t3={tests['test3_bit_removal_destabilizes']}")

    # Positive control: LUT-08 reference glider
    ref_particle = [tuple(c) for c in ref["particle"]]
    ref_tests = run_tests(ref_particle, lut08, label="lut08_ref")
    ref_pass = (ref_tests["test1_single_bit_velocity_matches"] is False and
                ref_tests["test2_multi_bit_cell_count"] > 0 and
                ref_tests["test3_bit_removal_destabilizes"] is True)
    print(f"LUT-08 reference: t1={ref_tests['test1_single_bit_velocity_matches']} t2={ref_tests['test2_multi_bit_cell_count']} t3={ref_tests['test3_bit_removal_destabilizes']} passes_all={ref_pass}")

    output = {
        "species_tested": len(novel),
        "non_interacting_composites": non_interacting,
        "genuine_gliders": genuine,
        "results_per_species": results,
        "lut08_reference_passes_all_tests": ref_pass,
    }
    with open(out_dir / "verification_results.json", "w") as f:
        json.dump(output, f, indent=2)

    md = ["# Iter 248: Glider Verification Report\n",
          "## Methodology\n",
          "- **Test 1**: Single-bit decomposition. If each bit moves with the same velocity solo as in the composite, the species is a non-interacting composite.\n",
          "- **Test 2**: Collision interaction. Count cells containing >1 bit across 32 steps. Zero means bits never interact.\n",
          "- **Test 3**: Bit-removal stability. Removing any bit should destabilize the pattern (change velocity, break bit conservation, or expand beyond extent 6).\n",
          "## Results\n",
          f"- Species tested: **{len(novel)}**\n",
          f"- Non-interacting composites: **{non_interacting}**\n",
          f"- Genuine gliders: **{genuine}**\n",
          f"- LUT-08 positive control passes all tests: **{ref_pass}**\n",
          "## Per-Species Details\n",
          "| ID | LUT | T1 (all solo match) | T2 (multi-bit cells) | T3 (removal destabilizes) | Verdict |\n",
          "|---|---|---|---|---|---|\n"]
    for r in results:
        md.append(f"| {r['species_id']} | {r['lut']} | {r['test1_single_bit_velocity_matches']} | {r['test2_multi_bit_cell_count']} | {r['test3_bit_removal_destabilizes']} | {r['verdict']} |\n")

    md.append("\n## Conclusion\n")
    if non_interacting == len(novel):
        md.append("**All 10 claimed 'novel species' are NON-INTERACTING COMPOSITES.** None exhibit coherent bit interaction required for a genuine glider.\n")
    else:
        md.append(f"{non_interacting} of {len(novel)} species are non-interacting composites; {genuine} appear genuine.\n")
    if not ref_pass:
        md.append("\n**WARNING**: The LUT-08 reference glider failed the positive control. The test suite may be defective.\n")

    with open(out_dir / "verification_report.md", "w") as f:
        f.write("".join(md))
    print(f"[done] Wrote verification_results.json and verification_report.md")


if __name__ == "__main__":
    main()
