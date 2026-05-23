#!/usr/bin/env python3
"""
rigorous_glider_audit.py

Rigorously audit all candidate gliders discovered in iter_240 plus the LUT-08
reference glider from iter_224.

Pipeline:
  1. Load reference particle + LUT from
     archive/iter_224/results/glider_00_lut08_sub03.json
  2. Load every archive/iter_240/results/new_glider_*.json
  3. Group all particles into equivalence classes under the full 48-element
     O_h symmetry group (signed permutations of (l,r,c) coupled with the
     induced channel permutation).
  4. For one representative per class, simulate 200 steps (5 periods at P=40)
     on an L=32 toroidal grid using engine_3d.stream / engine_3d.collide.
  5. Verify exact bit conservation and bounding extent <= 6 at every step.
  6. Compute exact shape period P, coordinate velocity v_coord and
     normalized speed v/c with c = sqrt(2).
  7. Write JSON taxonomy + markdown report.
"""

from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS, stream, collide  # noqa: E402
from src.search_3d_gliders import fcc_neighbor_vectors, get_oh_permutations  # noqa: E402


# ---------------------------------------------------------------------------
# O_h transformation tables
# ---------------------------------------------------------------------------

def build_oh_transforms():
    S = np.array(SHIFTS, dtype=float)
    S_pinv = np.linalg.pinv(S)
    C = fcc_neighbor_vectors().astype(float)
    C_pinv = np.linalg.pinv(C)
    B = S.T @ C_pinv.T
    P = []
    for i in range(12):
        v_proj = B @ C[i]
        diffs = np.linalg.norm(S - v_proj, axis=1)
        j = np.argmin(diffs)
        P.append(j)
    perms_cart = get_oh_permutations()
    transforms = []
    max_err = 0.0
    for p_cart in perms_cart:
        p_proj = [0] * 12
        for i in range(12):
            p_proj[P[i]] = P[p_cart[i]]
        p_proj = tuple(p_proj)
        S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        err = np.max(np.abs(S @ M_g.T - S_rot))
        max_err = max(max_err, err)
        transforms.append((p_proj, M_g))
    assert max_err < 1e-10, f"O_h transform reconstruction error too large: {max_err}"
    return transforms


# ---------------------------------------------------------------------------
# Particle canonicalization
# ---------------------------------------------------------------------------

def particle_translation_canon(particle):
    """Translate a particle so each axis min is 0, then sort cells lex."""
    arr = np.array(particle, dtype=int)
    coords = arr[:, :3]
    coords = coords - coords.min(axis=0, keepdims=True)
    cells = sorted(
        (int(coords[i, 0]), int(coords[i, 1]), int(coords[i, 2]), int(arr[i, 3]))
        for i in range(len(arr))
    )
    return tuple(cells)


def oh_canonical(particle, transforms):
    best = None
    for perm, M_g in transforms:
        transformed = []
        for (l, r, c, ch) in particle:
            v = M_g @ np.array([l, r, c], dtype=float)
            nl = int(np.round(v[0]))
            nr = int(np.round(v[1]))
            nc = int(np.round(v[2]))
            transformed.append((nl, nr, nc, int(perm[ch])))
        canon = particle_translation_canon(transformed)
        if best is None or canon < best:
            best = canon
    return best


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def seed_grid(L: int, particle, center=None):
    grid = np.zeros((L, L, L, 12), dtype=np.uint8)
    if center is None:
        center = (L // 2, L // 2, L // 2)
    cl, cr, cc = center
    for (dl, dr, dc, ch) in particle:
        grid[(cl + dl) % L, (cr + dr) % L, (cc + dc) % L, int(ch)] = 1
    return grid


def compute_com_circular(grid):
    L = grid.shape[0]
    total = int(grid.sum())
    if total == 0:
        return None, 0
    coords = np.zeros(3)
    pos = np.arange(L)
    theta = 2 * np.pi * pos / L
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    for axis in range(3):
        if axis == 0:
            w = grid.sum(axis=(1, 2, 3)).astype(np.float64)
        elif axis == 1:
            w = grid.sum(axis=(0, 2, 3)).astype(np.float64)
        else:
            w = grid.sum(axis=(0, 1, 3)).astype(np.float64)
        x = (w * cos_t).sum()
        y = (w * sin_t).sum()
        coords[axis] = (L * np.arctan2(y, x) / (2 * np.pi)) % L
    return coords, total


def circular_axis_min_shift(positions, L):
    """Given occupied positions on a length-L cycle, return shift s such
    that ((positions - s) % L) has minimum max-min, ties broken by smallest s."""
    if len(positions) == 0:
        return 0, 0
    uniq = np.unique(positions)
    best_shift = 0
    best_width = L + 1
    for s in uniq:
        shifted = (positions - s) % L
        w = int(shifted.max() - shifted.min() + 1)
        if w < best_width or (w == best_width and int(s) < int(best_shift)):
            best_width = w
            best_shift = int(s)
    return best_shift, best_width


def bounding_extent(grid):
    L = grid.shape[0]
    ext = []
    for axis in range(3):
        if axis == 0:
            occ = grid.sum(axis=(1, 2, 3)) > 0
        elif axis == 1:
            occ = grid.sum(axis=(0, 2, 3)) > 0
        else:
            occ = grid.sum(axis=(0, 1, 3)) > 0
        if not occ.any():
            ext.append(0)
            continue
        pos = np.where(occ)[0]
        _, width = circular_axis_min_shift(pos, L)
        ext.append(width)
    return tuple(ext)


def grid_cells(grid):
    """Return frozenset of (l, r, c, ch) tuples of occupied cells."""
    bits = np.argwhere(grid > 0)
    return frozenset((int(b[0]), int(b[1]), int(b[2]), int(b[3])) for b in bits)


def is_translate(cells1, cells2, L):
    """Are two cell sets equal modulo translation on torus L?"""
    if len(cells1) != len(cells2):
        return False
    l1 = sorted(cells1)
    l2 = sorted(cells2)
    if sorted(c[3] for c in l1) != sorted(c[3] for c in l2):
        return False
    c0 = l1[0]
    s2_set = set(cells2)
    for cand in l2:
        if cand[3] != c0[3]:
            continue
        dl = (cand[0] - c0[0]) % L
        dr = (cand[1] - c0[1]) % L
        dc = (cand[2] - c0[2]) % L
        ok = True
        for c in l1:
            shifted = ((c[0] + dl) % L, (c[1] + dr) % L, (c[2] + dc) % L, c[3])
            if shifted not in s2_set:
                ok = False
                break
        if ok:
            return True
    return False


def detect_period(shapes_list, L):
    n = len(shapes_list)
    for p in range(1, n):
        ok = True
        for t in range(n - p):
            if not is_translate(shapes_list[t], shapes_list[t + p], L):
                ok = False
                break
        if ok:
            return p
    return None


def simulate(particle, lut, L=32, steps=200):
    initial_bits = len(particle)
    grid = seed_grid(L, particle)
    if int(grid.sum()) != initial_bits:
        raise RuntimeError(
            f"Seeding failed: expected {initial_bits} bits, got {int(grid.sum())}"
        )

    bit_history = [int(grid.sum())]
    extent_history = [bounding_extent(grid)]
    shapes = [grid_cells(grid)]
    coms = [compute_com_circular(grid)[0]]

    stable = True
    for step in range(1, steps + 1):
        grid = stream(grid)
        grid = collide(grid, lut)
        bc = int(grid.sum())
        ext = bounding_extent(grid)
        bit_history.append(bc)
        extent_history.append(ext)
        shapes.append(grid_cells(grid))
        coms.append(compute_com_circular(grid)[0])
        if bc != initial_bits:
            stable = False
        if max(ext) > 6:
            stable = False

    # Cumulative displacement
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
    v_over_c = v_coord / np.sqrt(2.0)

    period = detect_period(shapes, L) if stable else None

    max_extent = int(max(max(e) for e in extent_history))
    return {
        "stable": stable,
        "initial_bits": initial_bits,
        "bit_conserved": all(b == initial_bits for b in bit_history),
        "max_extent": max_extent,
        "extent_under_6": max_extent <= 6,
        "period": period,
        "cumulative_displacement": cumdisp.tolist(),
        "displacement_norm": disp_norm,
        "v_coord": float(v_coord),
        "v_over_c": float(v_over_c),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    arch = ROOT / "archive"
    ref_path = arch / "iter_224" / "results" / "glider_00_lut08_sub03.json"
    out_dir = arch / "iter_240" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[load] reference: {ref_path}")
    with open(ref_path, "r") as f:
        ref_data = json.load(f)
    lut = np.array(ref_data["lut"], dtype=np.uint16)
    assert lut.shape == (4096,)
    ref_particle = [tuple(c) for c in ref_data["particle"]]
    print(f"  reference particle: {ref_particle}")
    print(f"  LUT length: {len(lut)}")

    # Load all 163 new glider files
    pattern = str(out_dir / "new_glider_*.json")
    files = sorted(glob.glob(pattern))
    print(f"[load] found {len(files)} new_glider_*.json files in {out_dir}")

    candidates = []  # list of dicts {source, particle}
    candidates.append({
        "source": "reference (iter_224 glider_00_lut08_sub03)",
        "is_reference": True,
        "particle": ref_particle,
    })
    for fp in files:
        with open(fp, "r") as f:
            d = json.load(f)
        part = [tuple(c) for c in d["particle"]]
        candidates.append({
            "source": os.path.basename(fp),
            "is_reference": False,
            "particle": part,
        })

    print(f"[load] total candidates (incl. reference): {len(candidates)}")

    # Build O_h transforms
    print("[oh] building 48 transforms ...")
    transforms = build_oh_transforms()
    print(f"[oh] built {len(transforms)} transforms")

    # Group by O_h canonical rep
    print("[group] computing O_h canonical reps ...")
    classes = {}  # canon -> {"members": [...], "rep_particle": ..., "has_reference": bool}
    for idx, cand in enumerate(candidates):
        canon = oh_canonical(cand["particle"], transforms)
        if canon not in classes:
            classes[canon] = {
                "rep_particle": list(canon),  # the canonical form itself is a fine particle
                "members": [],
                "has_reference": False,
            }
        classes[canon]["members"].append({
            "idx": idx,
            "source": cand["source"],
            "particle": cand["particle"],
        })
        if cand["is_reference"]:
            classes[canon]["has_reference"] = True

    print(f"[group] discovered {len(classes)} O_h equivalence classes")

    # Find reference class canon for "equivalent to reference" reporting
    ref_canon = oh_canonical(ref_particle, transforms)

    # Simulate one representative per class
    print(f"[simulate] running 200 steps on L=32 per class ...")
    results = []
    for class_id, (canon, info) in enumerate(sorted(classes.items())):
        rep_particle = info["rep_particle"]
        sim = simulate(rep_particle, lut, L=32, steps=200)
        result = {
            "class_id": class_id,
            "canonical_form": [list(c) for c in canon],
            "rep_particle": [list(c) for c in rep_particle],
            "n_members": len(info["members"]),
            "members": [
                {"idx": m["idx"], "source": m["source"]} for m in info["members"]
            ],
            "equivalent_to_reference": (canon == ref_canon),
            "stable": sim["stable"],
            "bit_conserved": sim["bit_conserved"],
            "max_extent": sim["max_extent"],
            "extent_under_6": sim["extent_under_6"],
            "period": sim["period"],
            "cumulative_displacement": sim["cumulative_displacement"],
            "displacement_norm": sim["displacement_norm"],
            "v_coord": sim["v_coord"],
            "v_over_c": sim["v_over_c"],
            "status": "STABLE" if sim["stable"] else "UNSTABLE",
        }
        results.append(result)
        print(
            f"  class {class_id:02d}: n={len(info['members']):3d}  "
            f"status={result['status']:<8}  "
            f"period={str(sim['period']):>5}  "
            f"|disp|={sim['displacement_norm']:7.3f}  "
            f"v/c={sim['v_over_c']:.4f}  "
            f"ref={'YES' if result['equivalent_to_reference'] else 'no'}"
        )

    # --- Detailed print ---
    print()
    print("=" * 90)
    print("AUDITED EQUIVALENCE CLASSES")
    print("=" * 90)
    for r in results:
        print(f"\nClass {r['class_id']}:")
        print(f"  canonical particle      : {r['canonical_form']}")
        print(f"  number of members       : {r['n_members']}")
        print(f"  equivalent to LUT-08 ref: {r['equivalent_to_reference']}")
        print(f"  status                  : {r['status']}")
        print(f"  bit-conserving          : {r['bit_conserved']}")
        print(f"  max_extent (200 steps)  : {r['max_extent']}  (<=6: {r['extent_under_6']})")
        print(f"  exact period P          : {r['period']}")
        print(f"  cum. displacement       : {r['cumulative_displacement']}")
        print(f"  |displacement|          : {r['displacement_norm']:.6f}")
        print(f"  v_coord = |disp|/200    : {r['v_coord']:.6f}")
        print(f"  v/c (c = sqrt(2))       : {r['v_over_c']:.6f}")

    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    stable = [r for r in results if r["stable"]]
    print(f"  total candidates loaded : {len(candidates)}  (163 new + 1 reference expected)")
    print(f"  total equivalence classes (full 48-element O_h): {len(results)}")
    print(f"  STABLE classes          : {len(stable)}")
    print(f"  UNSTABLE classes        : {len(results) - len(stable)}")
    ref_classes = [r for r in results if r["equivalent_to_reference"]]
    print(f"  classes equiv. to LUT-08 reference: {len(ref_classes)}")
    if stable:
        unique_periods = sorted({r["period"] for r in stable if r["period"]})
        print(f"  distinct periods (stable): {unique_periods}")
        unique_vovc = sorted({round(r["v_over_c"], 6) for r in stable})
        print(f"  distinct v/c   (stable): {unique_vovc}")

    # Save taxonomy
    tax_path = out_dir / "audited_glider_taxonomy.json"
    tax_doc = {
        "n_input_files": len(files),
        "n_total_candidates": len(candidates),
        "n_classes": len(results),
        "reference_canonical_form": [list(c) for c in ref_canon],
        "L": 32,
        "steps": 200,
        "c_max": float(np.sqrt(2.0)),
        "classes": results,
    }
    with open(tax_path, "w") as f:
        json.dump(tax_doc, f, indent=2)
    print(f"\n[write] taxonomy JSON: {tax_path}")

    # Markdown report
    md = []
    md.append("# Rigorous Glider Audit (LUT-08)\n")
    md.append("## Setup\n")
    md.append(f"- LUT source: `archive/iter_224/results/glider_00_lut08_sub03.json`")
    md.append(f"- Candidate gliders loaded from `archive/iter_240/results/new_glider_*.json`: **{len(files)}**")
    md.append(f"- Reference particle included: **1**")
    md.append(f"- Total candidates audited: **{len(candidates)}**")
    md.append(f"- Toroidal grid: L = 32")
    md.append(f"- Simulation steps: 200 (5 expected periods of P=40)")
    md.append(f"- Stability criterion: bit_count == initial_bits AND max_extent <= 6 on every step")
    md.append(f"- Symmetry group: full 48-element O_h, applied to (l, r, c) via signed-permutation matrices M_g coupled with induced 12-channel permutations")
    md.append(f"- c_max = sqrt(2)\n")
    md.append("## Aggregate results\n")
    md.append(f"- Distinct O_h equivalence classes: **{len(results)}**")
    md.append(f"- STABLE classes: **{len(stable)}**")
    md.append(f"- Classes equivalent to LUT-08 reference orbit: **{len(ref_classes)}**\n")
    md.append("## Per-class details\n")
    for r in results:
        md.append(f"### Class {r['class_id']} ({'STABLE' if r['stable'] else 'UNSTABLE'})")
        md.append("")
        md.append(f"- Members: **{r['n_members']}**")
        md.append(f"- Equivalent to LUT-08 reference: **{r['equivalent_to_reference']}**")
        md.append(f"- Canonical particle: `{r['canonical_form']}`")
        md.append(f"- Bit conserving: {r['bit_conserved']}")
        md.append(f"- Max extent over 200 steps: {r['max_extent']} (<=6: {r['extent_under_6']})")
        md.append(f"- Exact shape period P: **{r['period']}**")
        md.append(f"- Cumulative displacement: {r['cumulative_displacement']}")
        md.append(f"- |displacement| over 200 steps: {r['displacement_norm']:.6f}")
        md.append(f"- Coordinate velocity v = |disp|/200: {r['v_coord']:.6f}")
        md.append(f"- Normalized speed v/c = v/sqrt(2): **{r['v_over_c']:.6f}**")
        md.append("")
    md_path = out_dir / "audited_glider_taxonomy_report.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md))
    print(f"[write] markdown report: {md_path}")
    print("\n[done]")


if __name__ == "__main__":
    main()
