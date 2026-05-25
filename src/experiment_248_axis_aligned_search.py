#!/usr/bin/env python3
"""src/experiment_248_axis_aligned_search.py"""
import json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import stream, collide, SHIFTS
from src.rigorous_glider_audit import (
    build_oh_transforms, oh_canonical, simulate, seed_grid,
    compute_com_circular, bounding_extent, is_translate,
)
from src.search_3d_gliders import (
    generate_symmetric_lut, get_oh_permutations,
    precompute_perm_action, compute_orbits, compute_all_stabilizers, verify_lut,
)
from src.glider_charge_analysis import make_BT

# ---------------------------------------------------------------------------
# Sparse simulation helpers (fast for screening)
# ---------------------------------------------------------------------------
def stream_bits(bits, L):
    return [((l + SHIFTS[ch][0]) % L, (r + SHIFTS[ch][1]) % L, (c + SHIFTS[ch][2]) % L, ch) for (l, r, c, ch) in bits]

def collide_bits(bits, lut):
    cell_map = {}
    for (l, r, c, ch) in bits:
        cell_map[(l, r, c)] = cell_map.get((l, r, c), 0) | (1 << ch)
    new_bits = []
    for (l, r, c), packed in cell_map.items():
        new_packed = lut[packed]
        for ch in range(12):
            if (new_packed >> ch) & 1:
                new_bits.append((l, r, c, ch))
    return new_bits

def com_bits(bits, L):
    if not bits:
        return None
    coords = np.array([[b[0], b[1], b[2]] for b in bits], dtype=float)
    result = np.zeros(3)
    theta = 2 * np.pi * coords / L
    for a in range(3):
        x = np.cos(theta[:, a]).sum()
        y = np.sin(theta[:, a]).sum()
        result[a] = (L * np.arctan2(y, x) / (2 * np.pi)) % L
    return result

def extent_bits(bits, L):
    if not bits:
        return (0, 0, 0)
    coords = np.array([[b[0], b[1], b[2]] for b in bits])
    ext = []
    for a in range(3):
        pos = coords[:, a]
        best = L
        for s in np.unique(pos):
            shifted = (pos - s) % L
            w = int(shifted.max() - shifted.min() + 1)
            if w < best:
                best = w
        ext.append(best)
    return tuple(ext)

def quick_sim(particle, lut, L=32, steps=16):
    c = L // 2
    bits = [(c + dl, c + dr, c + dc, ch) for (dl, dr, dc, ch) in particle]
    b0 = len(bits)
    com_prev = com_bits(bits, L)
    cd = np.zeros(3)
    for _ in range(steps):
        bits = stream_bits(bits, L)
        bits = collide_bits(bits, lut)
        if len(bits) != b0:
            return None
        if max(extent_bits(bits, L)) > 6:
            return None
        com = com_bits(bits, L)
        if com is not None and com_prev is not None:
            d = com - com_prev
            d = (d + L // 2) % L - L // 2
            cd += d
        com_prev = com
    return cd

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out_dir = ROOT / "archive/iter_248/results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load LUT-08
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        ref = json.load(f)
    lut08 = np.array(ref["lut"], dtype=np.uint16)
    ref_particle = [tuple(c) for c in ref["particle"]]

    # Generate additional LUTs
    perms = get_oh_permutations()
    action = precompute_perm_action(perms)
    orbits, _ = compute_orbits(action)
    stabs = compute_all_stabilizers(action)

    luts = [("lut08", lut08)]
    for s in [42, 123, 999]:
        lut = generate_symmetric_lut(seed=s, perms=perms, action=action, orbits=orbits, stabs=stabs)
        v = verify_lut(lut, action)
        assert v["bijection"] and v["bit_conserving"] and v["symmetric"], f"LUT seed {s} failed: {v}"
        luts.append((f"sym_{s}", lut))

    # O_h transforms and reference canonical
    transforms = build_oh_transforms()
    ref_canon = oh_canonical(ref_particle, transforms)
    BT, BT_inv = make_BT()

    def axis_aligned(cd, steps=16):
        vc = (cd / steps) @ BT
        return all(abs(x - round(x * 2) / 2) < 0.01 for x in vc)

    rng = np.random.default_rng(248)
    candidates = []
    t0 = time.time()

    # Phase A: single-cell exhaustive
    phase_a = 0
    for k in range(3, 13):
        for subset in combinations(range(12), k):
            particle = [(0, 0, 0, ch) for ch in subset]
            for name, lut in luts:
                phase_a += 1
                cd = quick_sim(particle, lut, 32, 16)
                if cd is not None and np.linalg.norm(cd) > 0.1:
                    candidates.append({"phase": "A", "particle": particle, "lut_name": name, "cd16": cd.copy(), "bits": len(particle)})
            if phase_a % 2000 == 0:
                print(f"[A] tested {phase_a} ({time.time()-t0:.1f}s)", flush=True)
    print(f"[A] {phase_a} tested, {sum(1 for c in candidates if c['phase']=='A')} candidates")

    # Phase B: two-cell seeds along FCC directions
    phase_b = 0
    for shift in SHIFTS:
        for _ in range(300):
            total = int(rng.integers(3, 9))
            n1 = int(rng.integers(1, total))
            n2 = total - n1
            ch = rng.permutation(12)
            particle = [(0, 0, 0, int(c)) for c in ch[:n1]] + [(shift[0], shift[1], shift[2], int(c)) for c in ch[n1:n1 + n2]]
            for name, lut in luts:
                phase_b += 1
                cd = quick_sim(particle, lut, 32, 16)
                if cd is not None and np.linalg.norm(cd) > 0.1:
                    candidates.append({"phase": "B", "particle": particle, "lut_name": name, "cd16": cd.copy(), "bits": len(particle)})
    print(f"[B] {phase_b} tested, {sum(1 for c in candidates if c['phase']=='B')} candidates")

    # Phase C: multi-cell random seeds
    phase_c = 0
    for _ in range(5000):
        n = int(rng.integers(3, 13))
        bits = set()
        while len(bits) < n:
            bits.add((int(rng.integers(-1, 2)), int(rng.integers(-1, 2)), int(rng.integers(-1, 2)), int(rng.integers(0, 12))))
        particle = list(bits)
        for name, lut in luts:
            phase_c += 1
            cd = quick_sim(particle, lut, 32, 16)
            if cd is not None and np.linalg.norm(cd) > 0.1:
                candidates.append({"phase": "C", "particle": particle, "lut_name": name, "cd16": cd.copy(), "bits": len(particle)})
        if phase_c % 4000 == 0:
            print(f"[C] tested {phase_c} ({time.time()-t0:.1f}s)", flush=True)
    print(f"[C] {phase_c} tested, {sum(1 for c in candidates if c['phase']=='C')} candidates")

    # Phase D: verify candidates
    stable_moving = []
    axis_aligned_list = []
    novel = []
    lut_map = {name: lut for name, lut in luts}

    print(f"[D] verifying {len(candidates)} candidates...")
    for ci, cand in enumerate(candidates):
        if ci % 50 == 0:
            print(f"[D] {ci}/{len(candidates)} ({time.time()-t0:.1f}s)", flush=True)
        lut = lut_map[cand["lut_name"]]
        sim32 = simulate(cand["particle"], lut, L=32, steps=200)
        if not sim32["stable"] or sim32["displacement_norm"] <= 0.1:
            continue
        stable_moving.append(cand)
        cd = np.array(sim32["cumulative_displacement"])
        if not axis_aligned(cd, 200):
            continue
        axis_aligned_list.append(cand)
        canon = oh_canonical(cand["particle"], transforms)
        if canon == ref_canon:
            continue
        cand["velocity_grid"] = (cd / 200).tolist()
        cand["velocity_cart"] = ((cd / 200) @ BT).tolist()
        cand["period"] = sim32["period"]
        cand["canon"] = [list(c) for c in canon]

        # Verify on L=64, 300 steps
        sim64 = simulate(cand["particle"], lut, L=64, steps=300)
        if not sim64["stable"]:
            continue

        # O_h covariance test
        perm, M_g = transforms[1]
        rot = []
        for (l, r, c, ch) in cand["particle"]:
            v = M_g @ np.array([l, r, c], dtype=float)
            rot.append((int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch])))
        sim_rot = simulate(rot, lut, L=32, steps=200)
        if not sim_rot["stable"]:
            continue
        cd_rot = np.array(sim_rot["cumulative_displacement"])
        cd_orig_rot = M_g @ cd
        cov_ok = np.linalg.norm(cd_rot - cd_orig_rot) < 1.0
        cand["oh_covariant"] = bool(cov_ok)
        cand["oh_orbit_distinct"] = True
        novel.append(cand)

    # Write outputs
    results = {
        "phase_a_candidates_tested": phase_a,
        "phase_b_candidates_tested": phase_b,
        "phase_c_candidates_tested": phase_c,
        "luts_tested": 4,
        "stable_moving_candidates": [{"phase": c["phase"], "lut": c["lut_name"], "bits": c["bits"], "cd16": c["cd16"].tolist()} for c in stable_moving],
        "axis_aligned_candidates": [{"phase": c["phase"], "lut": c["lut_name"], "bits": c["bits"], "velocity_grid": c.get("velocity_grid"), "velocity_cart": c.get("velocity_cart")} for c in axis_aligned_list],
        "novel_species": [{"phase": c["phase"], "lut": c["lut_name"], "bits": c["bits"], "velocity_grid": c["velocity_grid"], "velocity_cart": c["velocity_cart"], "period": c["period"], "canon": c["canon"], "oh_covariant": c["oh_covariant"]} for c in novel],
        "f1_triggered": len(novel) == 0,
        "summary": f"Tested {phase_a+phase_b+phase_c} candidates. Found {len(stable_moving)} stable moving, {len(axis_aligned_list)} axis-aligned, {len(novel)} novel species.",
    }
    with open(out_dir / "search_results.json", "w") as f:
        json.dump(results, f, indent=2)

    md = ["# Iter 248: Axis-Aligned Glider Search Report\n",
          "## Search Coverage\n",
          f"- Phase A (single-cell exhaustive): {phase_a} candidates\n",
          f"- Phase B (two-cell NN random): {phase_b} candidates\n",
          f"- Phase C (multi-cell random): {phase_c} candidates\n",
          "- LUTs: LUT-08 + 3 generated symmetric LUTs (seeds 42, 123, 999)\n",
          "## Results\n",
          f"- Stable moving candidates: **{len(stable_moving)}**\n",
          f"- Axis-aligned candidates: **{len(axis_aligned_list)}**\n",
          f"- Novel species (distinct O_h orbit from LUT-08): **{len(novel)}**\n",
          "## F1 Status\n",
          f"**{'TRIGGERED' if len(novel)==0 else 'NOT TRIGGERED'}**\n"]
    if novel:
        md.append("## Novel Species Details\n")
        for i, c in enumerate(novel):
            md.append(f"### Species {i}\n")
            md.append(f"- Phase: {c['phase']}, LUT: {c['lut_name']}, Bits: {c['bits']}\n")
            md.append(f"- Velocity grid: {c['velocity_grid']}\n")
            md.append(f"- Velocity cart: {c['velocity_cart']}\n")
            md.append(f"- Period: {c['period']}\n")
            md.append(f"- O_h covariant: {c['oh_covariant']}\n")
    if novel:
        with open(out_dir / "species_table.csv", "w") as f:
            f.write("species_id,bit_count,period,velocity_grid,velocity_cartesian,axis_aligned,oh_orbit_distinct_from_lut08,oh_covariant\n")
            for i, c in enumerate(novel):
                vg = str(c["velocity_grid"]).replace(",", ";")
                vc = str(c["velocity_cart"]).replace(",", ";")
                f.write(f"{i},{c['bits']},{c['period']},{vg},{vc},True,True,{c['oh_covariant']}\n")

    with open(out_dir / "search_report.md", "w") as f:
        f.write("\n".join(md))

    print(f"[done] {results['summary']} in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
