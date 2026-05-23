#!/usr/bin/env python3
"""
fcc_glider_search.py - Phase 7.1 Glider Taxonomy

Searches the FCC LGCA configuration space (using the LUT-08 rule) for stable,
propagating gliders that are NOT in the O_h orbit of the known LUT-08 glider.

Pipeline:
  1. Load reference glider LUT-08 and its 4096-entry LUT.
  2. Build the 48 O_h coordinate transforms (matrix M_g + channel permutation perm)
     using the same B-mapping approach verified in src/rigorous_glider_audit.py.
  3. Simulate LUT-08 for 40 steps, extract each step's unwrapped/translated shape,
     and rotate every shape under all 48 O_h symmetries to populate
     LUT08_ORBIT_SHAPES.
  4. Generate candidate seeds via three methods:
       A. Systematic connected sweep, W in {4,5}, on 1- and 2-cell configurations.
       B. Randomized compact contiguous sweep, W in {4..8}, ~100 unique per W.
       C. Genetic Algorithm, W in {4..8}, population 40, 6 generations.
  5. For each candidate, run an 80-step pre-filter simulation. Promote those with
     displacement >= 4.0 to be classified against LUT08_ORBIT_SHAPES; any survivor
     undergoes extended 1000-step stability, sub-light, and O_h covariance
     verification.
  6. Save search_summary.json and exhaustive_search_report.md.
"""

from __future__ import annotations

import json
import os
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS, stream, collide  # noqa: E402
from src.rigorous_glider_audit import (  # noqa: E402
    bounding_extent,
    build_oh_transforms,
    circular_axis_min_shift,
    compute_com_circular,
    particle_translation_canon,
    seed_grid,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REF_PATH = ROOT / "archive" / "iter_224" / "results" / "glider_00_lut08_sub03.json"
OUT_DIR = ROOT / "archive" / "iter_241" / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

C_LIGHT = float(np.sqrt(2.0))


# ---------------------------------------------------------------------------
# Shape extraction & canonicalisation
# ---------------------------------------------------------------------------

def extract_unwrapped_shape(grid: np.ndarray) -> tuple:
    """Extract the active bit set, unwrapped on the torus and translated so the
    lexicographical minimum of (l, r, c) is (0, 0, 0). Returns a sorted tuple of
    (l, r, c, ch) entries.
    """
    L = grid.shape[0]
    bits = np.argwhere(grid > 0)
    if len(bits) == 0:
        return tuple()
    coords = bits[:, :3].astype(int)
    chans = bits[:, 3].astype(int)

    shifted = np.empty_like(coords)
    for axis in range(3):
        s, _ = circular_axis_min_shift(coords[:, axis], L)
        shifted[:, axis] = (coords[:, axis] - s) % L
    mins = shifted.min(axis=0)
    shifted = shifted - mins
    cells = sorted(
        (int(shifted[i, 0]), int(shifted[i, 1]), int(shifted[i, 2]), int(chans[i]))
        for i in range(len(bits))
    )
    return tuple(cells)


def apply_oh_to_shape(shape: tuple, transform) -> tuple:
    """Apply an O_h transform (perm, M_g) to a shape and re-translate so lex-min
    of (l, r, c) is (0, 0, 0)."""
    perm, M_g = transform
    out = []
    for (l, r, c, ch) in shape:
        v = M_g @ np.array([l, r, c], dtype=float)
        nl = int(round(v[0]))
        nr = int(round(v[1]))
        nc = int(round(v[2]))
        out.append((nl, nr, nc, int(perm[ch])))
    return particle_translation_canon(out)


def apply_oh_to_particle(particle, transform):
    perm, M_g = transform
    out = []
    for (l, r, c, ch) in particle:
        v = M_g @ np.array([l, r, c], dtype=float)
        nl = int(round(v[0]))
        nr = int(round(v[1]))
        nc = int(round(v[2]))
        out.append((nl, nr, nc, int(perm[ch])))
    return out


# ---------------------------------------------------------------------------
# Simulation primitives
# ---------------------------------------------------------------------------

def simulate_with_metrics(particle, lut, L=20, steps=80, extent_every=4):
    """Simulate a particle and return aggregate metrics. extent_every controls
    how often we evaluate the bounding extent (>=6 quick fail)."""
    initial_bits = len(particle)
    grid = seed_grid(L, particle)
    if int(grid.sum()) != initial_bits:
        return {"valid": False, "reason": "seed bit collision"}

    coms = [compute_com_circular(grid)[0]]
    max_ext = 0
    bit_constant = True

    for step in range(1, steps + 1):
        grid = stream(grid)
        grid = collide(grid, lut)
        bc = int(grid.sum())
        if bc != initial_bits:
            bit_constant = False
            if bc == 0:
                coms.append(None)
                break
        if (step % extent_every) == 0 or step == steps:
            ext = bounding_extent(grid)
            max_ext = max(max_ext, max(ext))
        coms.append(compute_com_circular(grid)[0])

    cumdisp = np.zeros(3)
    for i in range(1, len(coms)):
        if coms[i] is None or coms[i - 1] is None:
            continue
        d = coms[i] - coms[i - 1]
        for axis in range(3):
            if d[axis] > L / 2:
                d[axis] -= L
            elif d[axis] < -L / 2:
                d[axis] += L
        cumdisp += d

    disp_norm = float(np.linalg.norm(cumdisp))
    v_coord = disp_norm / steps
    return {
        "valid": True,
        "initial_bits": initial_bits,
        "final_bits": int(grid.sum()),
        "bit_constant": bool(bit_constant),
        "max_extent": int(max_ext),
        "max_extent_under_6": bool(max_ext <= 6),
        "cumulative_displacement": cumdisp.tolist(),
        "displacement_norm": disp_norm,
        "v_coord": float(v_coord),
    }


def extended_stability(particle, lut, L=32, steps=1000):
    """Verify perfect bit conservation and max_extent <= 6 at EVERY step."""
    initial_bits = len(particle)
    grid = seed_grid(L, particle)
    if int(grid.sum()) != initial_bits:
        return {"stable": False, "reason": "seed bit collision", "failed_at": 0}

    coms = [compute_com_circular(grid)[0]]
    for step in range(1, steps + 1):
        grid = stream(grid)
        grid = collide(grid, lut)
        bc = int(grid.sum())
        if bc != initial_bits:
            return {"stable": False, "reason": "bit count change", "failed_at": step}
        ext = bounding_extent(grid)
        if max(ext) > 6:
            return {"stable": False, "reason": f"max_extent {max(ext)} > 6", "failed_at": step}
        coms.append(compute_com_circular(grid)[0])

    cumdisp = np.zeros(3)
    for i in range(1, len(coms)):
        if coms[i] is None or coms[i - 1] is None:
            continue
        d = coms[i] - coms[i - 1]
        for axis in range(3):
            if d[axis] > L / 2:
                d[axis] -= L
            elif d[axis] < -L / 2:
                d[axis] += L
        cumdisp += d
    disp_norm = float(np.linalg.norm(cumdisp))
    v_coord = disp_norm / steps
    return {
        "stable": True,
        "steps": steps,
        "cumulative_displacement": cumdisp.tolist(),
        "displacement_norm": disp_norm,
        "v_coord": float(v_coord),
        "v_over_c": float(v_coord / C_LIGHT),
    }


# ---------------------------------------------------------------------------
# Seed generators
# ---------------------------------------------------------------------------

def gen_method_a(per_combo_cap=4):
    """Method A: systematic 1-cell and 2-cell sweep for W in {4, 5}."""
    seeds = set()
    # 1-cell: place W channels at origin
    for W in (4, 5):
        for chans in combinations(range(12), W):
            part = tuple(sorted((0, 0, 0, ch) for ch in chans))
            seeds.add(part)

    # 2-cell: cells at origin and one FCC nearest neighbor offset
    for W in (4, 5):
        for offset in SHIFTS:
            for w1 in range(1, W):
                w2 = W - w1
                chans1 = list(combinations(range(12), w1))
                chans2 = list(combinations(range(12), w2))
                # Cap to keep total tractable; sample evenly
                if len(chans1) > per_combo_cap:
                    step = max(1, len(chans1) // per_combo_cap)
                    chans1 = chans1[::step][:per_combo_cap]
                if len(chans2) > per_combo_cap:
                    step = max(1, len(chans2) // per_combo_cap)
                    chans2 = chans2[::step][:per_combo_cap]
                for c1 in chans1:
                    for c2 in chans2:
                        bits = [(0, 0, 0, ch) for ch in c1] + \
                               [(int(offset[0]), int(offset[1]), int(offset[2]), ch) for ch in c2]
                        # Reject if duplicate bit (shouldn't happen because sites differ)
                        if len(set(bits)) == len(bits):
                            seeds.add(tuple(sorted(bits)))
    return sorted(seeds)


def _random_compact_particle(W, rng):
    """Generate a random compact contiguous particle with W bits."""
    placed_sites = {(0, 0, 0)}
    bits = []
    start_ch = int(rng.integers(0, 12))
    bits.append((0, 0, 0, start_ch))
    attempts = 0
    while len(bits) < W and attempts < 200:
        attempts += 1
        # pick existing site
        sites = list(placed_sites)
        src = sites[int(rng.integers(0, len(sites)))]
        offset = SHIFTS[int(rng.integers(0, 12))]
        new_site = (src[0] + offset[0], src[1] + offset[1], src[2] + offset[2])
        ch = int(rng.integers(0, 12))
        candidate = (new_site[0], new_site[1], new_site[2], ch)
        if candidate in bits:
            continue
        bits.append(candidate)
        placed_sites.add(new_site)
    if len(bits) < W:
        return None
    return tuple(sorted(bits))


def gen_method_b(rng, per_W=100):
    seeds = set()
    by_W = {}
    for W in range(4, 9):
        by_W[W] = set()
        attempts = 0
        while len(by_W[W]) < per_W and attempts < per_W * 20:
            attempts += 1
            p = _random_compact_particle(W, rng)
            if p is None:
                continue
            by_W[W].add(p)
        seeds |= by_W[W]
    return sorted(seeds)


def _ga_fitness(metrics):
    if not metrics["valid"]:
        return 0.0
    base = metrics["displacement_norm"]
    if not metrics["bit_constant"]:
        base *= 0.4
    if not metrics["max_extent_under_6"]:
        base *= 0.3
    return base


def _crossover_mutate(a, b, W, rng):
    """One-point crossover with mutation, ensuring W unique bits."""
    cut = int(rng.integers(1, W))
    proposed = list(a[:cut]) + list(b[cut:])
    seen = set()
    uniq = []
    for c in proposed:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    # Fill in
    fill_attempts = 0
    while len(uniq) < W and fill_attempts < 100:
        fill_attempts += 1
        sites = list({(c[0], c[1], c[2]) for c in uniq}) or [(0, 0, 0)]
        src = sites[int(rng.integers(0, len(sites)))]
        offset = SHIFTS[int(rng.integers(0, 12))]
        new_site = (src[0] + offset[0], src[1] + offset[1], src[2] + offset[2])
        ch = int(rng.integers(0, 12))
        cand = (new_site[0], new_site[1], new_site[2], ch)
        if cand not in seen:
            seen.add(cand)
            uniq.append(cand)
    if len(uniq) < W:
        return None
    # Mutation: swap one bit's channel
    if rng.random() < 0.35:
        i = int(rng.integers(0, W))
        bit = uniq[i]
        new_ch = int(rng.integers(0, 12))
        uniq[i] = (bit[0], bit[1], bit[2], new_ch)
    return tuple(sorted(uniq))


def gen_method_c(lut, rng, pop_size=40, generations=6):
    """Genetic Algorithm for W in {4..8}. Returns list of (W, fitness, particle, metrics)."""
    all_records = []
    for W in range(4, 9):
        pop = []
        seen = set()
        while len(pop) < pop_size:
            p = _random_compact_particle(W, rng)
            if p is not None and p not in seen:
                seen.add(p)
                pop.append(p)

        best_records = []
        for gen in range(generations):
            scored = []
            for p in pop:
                m = simulate_with_metrics(p, lut, L=16, steps=40, extent_every=8)
                scored.append((_ga_fitness(m), p, m))
            scored.sort(key=lambda x: -x[0])
            best_records.append(scored[0])
            elite = [s[1] for s in scored[:10]]
            new_pop = list(elite)
            while len(new_pop) < pop_size:
                a = elite[int(rng.integers(0, len(elite)))]
                b = elite[int(rng.integers(0, len(elite)))]
                child = _crossover_mutate(a, b, W, rng)
                if child is not None and child not in seen:
                    seen.add(child)
                    new_pop.append(child)
            pop = new_pop
            print(f"  [GA W={W} gen={gen}] best fitness = {scored[0][0]:.3f}, "
                  f"disp={scored[0][2].get('displacement_norm', 0):.3f}")
        all_records.append((W, best_records))
    return all_records


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print(f"[load] reference: {REF_PATH}")
    with open(REF_PATH, "r") as f:
        ref_data = json.load(f)
    lut = np.array(ref_data["lut"], dtype=np.uint16)
    assert lut.shape == (4096,)
    ref_particle = [tuple(c) for c in ref_data["particle"]]
    print(f"  particle: {ref_particle}")
    print(f"  initial bits: {len(ref_particle)}")

    print("[oh] building 48 transforms ...")
    transforms = build_oh_transforms()
    assert len(transforms) == 48

    # ----- Step 1: build LUT08_ORBIT_SHAPES -----
    print("[orbit] simulating LUT-08 for 40 steps and applying all 48 rotations ...")
    L_ORBIT = 32
    grid = seed_grid(L_ORBIT, ref_particle)
    orbit_shapes = set()
    phase_shapes = []
    for step in range(41):  # 0..40 inclusive => 41 phases for safety
        sh = extract_unwrapped_shape(grid)
        phase_shapes.append(sh)
        for tr in transforms:
            orbit_shapes.add(apply_oh_to_shape(sh, tr))
        if step < 40:
            grid = stream(grid)
            grid = collide(grid, lut)
    LUT08_ORBIT_SHAPES = orbit_shapes
    print(f"[orbit] {len(LUT08_ORBIT_SHAPES)} unique shapes covering 41 phases x 48 rotations")

    # ----- Step 2: Generate seeds -----
    print("[method A] generating seeds ...")
    seeds_a = gen_method_a()
    print(f"  Method A: {len(seeds_a)} seeds")

    rng = np.random.default_rng(20260523)
    print("[method B] generating seeds ...")
    seeds_b = gen_method_b(rng, per_W=100)
    print(f"  Method B: {len(seeds_b)} seeds")

    print("[method C] running GA ...")
    ga_records = gen_method_c(lut, rng, pop_size=40, generations=6)
    ga_seed_set = set()
    for W, recs in ga_records:
        for fit, p, m in recs:
            ga_seed_set.add(p)
    print(f"  Method C: {len(ga_seed_set)} unique elite seeds")

    # Tag seeds by method
    seeds_meta = {}
    for p in seeds_a:
        seeds_meta.setdefault(p, set()).add("A")
    for p in seeds_b:
        seeds_meta.setdefault(p, set()).add("B")
    for p in ga_seed_set:
        seeds_meta.setdefault(p, set()).add("C")
    all_seeds = list(seeds_meta.keys())
    print(f"[combined] {len(all_seeds)} unique seeds across A+B+C")

    # ----- Step 3: 80-step pre-filter -----
    print("[search] 80-step pre-filter simulation ...")
    candidates = []
    n = len(all_seeds)
    t_pre = time.time()
    for i, p in enumerate(all_seeds):
        m = simulate_with_metrics(p, lut, L=20, steps=80, extent_every=4)
        if m["valid"] and m["displacement_norm"] >= 4.0:
            candidates.append({
                "particle": [list(x) for x in p],
                "methods": sorted(seeds_meta[p]),
                "displacement_norm": m["displacement_norm"],
                "v_coord": m["v_coord"],
                "max_extent": m["max_extent"],
                "bit_constant": m["bit_constant"],
                "max_extent_under_6": m["max_extent_under_6"],
                "initial_bits": m["initial_bits"],
            })
        if (i + 1) % 500 == 0:
            elapsed = time.time() - t_pre
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (n - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{n}] {len(candidates)} candidates so far "
                  f"(rate {rate:.1f}/s, ETA {eta:.0f}s)")
    print(f"[search] pre-filter complete: {len(candidates)} candidates "
          f"with |displacement| >= 4.0")

    # ----- Step 4: classify candidates against LUT-08 orbit -----
    print("[classify] checking each candidate's canonical shape vs LUT08 orbit ...")
    lut08_matches = []
    novel = []
    for c in candidates:
        part = [tuple(x) for x in c["particle"]]
        canon = particle_translation_canon(part)
        in_orbit = canon in LUT08_ORBIT_SHAPES
        c["in_lut08_orbit"] = bool(in_orbit)
        c["canonical_shape"] = [list(x) for x in canon]
        if in_orbit:
            lut08_matches.append(c)
        else:
            novel.append(c)
    print(f"  matched to LUT-08 orbit (discarded): {len(lut08_matches)}")
    print(f"  novel candidates (not in LUT-08 orbit): {len(novel)}")

    # ----- Step 5: extended verification for novel candidates -----
    print("[verify] running extended 1000-step verification for novel candidates ...")
    survivors = []
    g_idx_covariance = 21  # selected O_h rotation for covariance check
    for c in novel:
        part = [tuple(x) for x in c["particle"]]
        ext = extended_stability(part, lut, L=32, steps=1000)
        c["extended_stability"] = ext
        if not ext["stable"]:
            continue
        sub_light = ext["v_coord"] < C_LIGHT
        c["sub_light"] = bool(sub_light)
        if not sub_light:
            continue
        rotated = apply_oh_to_particle(part, transforms[g_idx_covariance])
        rot_ext = extended_stability(rotated, lut, L=32, steps=1000)
        c["oh_covariance"] = {
            "g_index": g_idx_covariance,
            "rotated_particle": [list(x) for x in rotated],
            "rotated_extended": rot_ext,
            "speed_matches": bool(
                rot_ext["stable"]
                and abs(rot_ext["v_coord"] - ext["v_coord"]) < 1e-6
            ),
            "direction_consistent": False,
        }
        if rot_ext["stable"]:
            cd_orig = np.array(ext["cumulative_displacement"])
            cd_rot = np.array(rot_ext["cumulative_displacement"])
            # Expected: rotated displacement equals M_g . original displacement
            perm, M_g = transforms[g_idx_covariance]
            expected = M_g @ cd_orig
            mismatch = float(np.linalg.norm(cd_rot - expected))
            c["oh_covariance"]["expected_rotated_disp"] = expected.tolist()
            c["oh_covariance"]["disp_mismatch_norm"] = mismatch
            c["oh_covariance"]["direction_consistent"] = bool(mismatch < 1.0)
        if c["oh_covariance"]["speed_matches"] and c["oh_covariance"]["direction_consistent"]:
            survivors.append(c)
    print(f"  survivors after 1000-step + sub-light + covariance: {len(survivors)}")

    # ----- Step 6: save artefacts -----
    summary = {
        "phase_7_1": "Glider Taxonomy search",
        "ref_path": str(REF_PATH.relative_to(ROOT)),
        "ref_particle": [list(x) for x in ref_particle],
        "lut08_orbit_n_shapes": len(LUT08_ORBIT_SHAPES),
        "transforms_count": len(transforms),
        "c_light": C_LIGHT,
        "method_a_n_seeds": len(seeds_a),
        "method_b_n_seeds": len(seeds_b),
        "method_c_n_unique_seeds": len(ga_seed_set),
        "total_unique_seeds": len(all_seeds),
        "n_candidates_disp_ge_4": len(candidates),
        "n_classified_as_lut08": len(lut08_matches),
        "n_novel_candidates": len(novel),
        "n_novel_survivors": len(survivors),
        "candidates": candidates,
        "novel_candidates": novel,
        "survivors": survivors,
        "wall_seconds": time.time() - t0,
    }
    summary_path = OUT_DIR / "search_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[write] summary JSON: {summary_path}")

    # Markdown report
    md = []
    md.append("# Phase 7.1 - Exhaustive Glider Search (LUT-08 rule)\n")
    md.append("## Setup\n")
    md.append(f"- Rule LUT: `archive/iter_224/results/glider_00_lut08_sub03.json` (LUT-08)\n")
    md.append(f"- Reference particle: `{ref_particle}`\n")
    md.append(f"- Lattice c = sqrt(2) ~ {C_LIGHT:.6f}\n")
    md.append(f"- Reference orbit (40 phases x 48 O_h rotations): "
              f"**{len(LUT08_ORBIT_SHAPES)}** unique unwrapped shapes\n")
    md.append("\n## Methods\n")
    md.append("### Method A - Systematic connected sweep (W in {4, 5}, 1- and 2-cell)\n")
    md.append(f"- Unique seeds enumerated: **{len(seeds_a)}**\n")
    md.append("- 1-cell: all channel subsets of size W at a single lattice site.\n")
    md.append("- 2-cell: site pair {origin, FCC nearest neighbor offset}, all (w1, w2) "
              "splits with bounded channel-subset sampling per combo.\n")
    md.append("\n### Method B - Randomized compact contiguous (W in {4..8})\n")
    md.append(f"- Unique seeds: **{len(seeds_b)}** (target 100 per W, RNG seed 20260523)\n")
    md.append("- Particles are grown by repeatedly attaching a random channel at a "
              "random FCC neighbor of an already-occupied site.\n")
    md.append("\n### Method C - Genetic Algorithm (W in {4..8})\n")
    md.append(f"- Population 40, 6 generations per W. {len(ga_seed_set)} unique elite particles retained.\n")
    md.append("- Fitness = displacement_norm (40-step, L=16) penalised for "
              "bit-count drift and extent overflow.\n")
    md.append(f"\n### Combined search space\n")
    md.append(f"- Total unique seeds simulated for the 80-step pre-filter: **{len(all_seeds)}**\n")
    md.append("\n## Pre-filter result\n")
    md.append(f"- Candidates with |displacement| >= 4.0 over 80 steps: **{len(candidates)}**\n")
    md.append(f"- Of these, classified as LUT-08 orbit members (discarded): "
              f"**{len(lut08_matches)}**\n")
    md.append(f"- Novel candidates (not in LUT-08 orbit): **{len(novel)}**\n")

    md.append("\n## Extended verification (only novel candidates)\n")
    md.append("- Per candidate: 1000-step simulation requiring bit-conservation AND "
              "max_extent <= 6 on every step.\n")
    md.append("- Sub-light gate: v_coord < sqrt(2).\n")
    md.append(f"- O_h covariance: rotate seed by transform g={g_idx_covariance}, "
              "verify identical stability/speed and that displacement matches M_g . disp.\n")
    md.append(f"- Survivors of full verification: **{len(survivors)}**\n")

    if not survivors:
        md.append("\n## Conclusion - Null Result\n")
        md.append(
            "Across all three search modalities (systematic, randomised, and "
            "evolutionary), **no new stable propagating glider was discovered "
            "outside the O_h orbit of LUT-08**. Every candidate exceeding the "
            "displacement threshold either:\n"
            "1. collapsed onto a translate/rotate of the reference LUT-08 shape, or\n"
            "2. failed the extended 1000-step stability gate (bit-count drift or "
            "extent overflow), or\n"
            "3. failed the O_h covariance check.\n\n"
            "This is a robust negative result: the scanned configuration space "
            "(W in {4..8}, 1- and 2-cell systematic enumeration, randomised compact "
            "growth, and 6-generation GA refinement) "
            "**is consistent with the unique isolation of the LUT-08 glider within "
            "the scanned configuration space** under its own conservative LUT.\n"
        )
    else:
        md.append("\n## NEW GLIDER(S) DISCOVERED\n")
        for i, s in enumerate(survivors):
            md.append(f"\n### Candidate {i} (W={s['initial_bits']})\n")
            md.append(f"- Methods: {s['methods']}\n")
            md.append(f"- Particle: `{s['particle']}`\n")
            md.append(f"- 80-step displacement: {s['displacement_norm']:.4f}\n")
            md.append(f"- 1000-step v_coord: {s['extended_stability']['v_coord']:.6f} "
                      f"(v/c = {s['extended_stability']['v_over_c']:.6f})\n")
            md.append(f"- O_h covariance: speed_matches="
                      f"{s['oh_covariance']['speed_matches']}, "
                      f"direction_consistent="
                      f"{s['oh_covariance']['direction_consistent']}\n")

    md.append("\n## Artefacts\n")
    md.append("- `archive/iter_241/results/search_summary.json` (machine-readable)\n")
    md.append("- `archive/iter_241/results/exhaustive_search_report.md` (this report)\n")

    report_path = OUT_DIR / "exhaustive_search_report.md"
    with open(report_path, "w") as f:
        f.write("".join(md))
    print(f"[write] report: {report_path}")

    print(f"[done] wall time {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
