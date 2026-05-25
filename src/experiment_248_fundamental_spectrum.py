#!/usr/bin/env python3
"""Fundamental single-bit particle spectrum and multi-bit coherent structure search."""
from __future__ import annotations
import json, sys
from itertools import combinations
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import stream, collide, SHIFTS
from src.search_3d_gliders import (
    generate_symmetric_lut, get_oh_permutations,
    precompute_perm_action, compute_orbits, compute_all_stabilizers, verify_lut,
)
from src.glider_charge_analysis import make_BT
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent

# ---------------------------------------------------------------------------
# Sparse simulation helpers
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

def max_dist(bits):
    if len(bits) <= 1:
        return 0
    coords = np.array([[b[0], b[1], b[2]] for b in bits])
    best = 0
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            d = np.abs(coords[i] - coords[j])
            best = max(best, int(d.max()))
    return best

def simulate_sparse(particle, lut, L=32, steps=32):
    c = L // 2
    bits = [(c + dl, c + dr, c + dc, ch) for (dl, dr, dc, ch) in particle]
    b0 = len(bits)
    for _ in range(steps):
        bits = stream_bits(bits, L)
        bits = collide_bits(bits, lut)
        if len(bits) != b0:
            return None, None
    return bits, b0

# ---------------------------------------------------------------------------
# Task 1: Weight-1 permutation cycles
# ---------------------------------------------------------------------------
def weight1_cycles(lut, BT_inv):
    perm = []
    for ch in range(12):
        out = int(lut[1 << ch])
        assert bin(out).count('1') == 1, f"LUT not bit-conserving on weight-1: ch={ch} -> {out}"
        dst = (out & -out).bit_length() - 1
        perm.append(dst)

    visited = [False] * 12
    cycles = []
    for i in range(12):
        if visited[i]:
            continue
        cyc = []
        j = i
        while not visited[j]:
            visited[j] = True
            cyc.append(j)
            j = perm[j]
        if len(cyc) >= 1:
            cycles.append(cyc)

    results = []
    for cyc in cycles:
        v_grid = np.mean([SHIFTS[ch] for ch in cyc], axis=0)
        v_cart = v_grid @ BT_inv
        axis_aligned = all(abs(x - round(x * 2) / 2) < 1e-9 for x in v_cart)
        results.append({
            "cycle": cyc,
            "period": len(cyc),
            "velocity_grid": [float(x) for x in v_grid],
            "velocity_cart": [float(x) for x in v_cart],
            "axis_aligned": bool(axis_aligned),
        })
    return results

# ---------------------------------------------------------------------------
# Task 2 & 3: Coherent structure search
# ---------------------------------------------------------------------------
def search_coherent(lut, weight, max_dist_allowed, L=32, steps=32):
    c = L // 2
    found = []
    for subset in combinations(range(12), weight):
        particle = [(0, 0, 0, ch) for ch in subset]
        bits, b0 = simulate_sparse(particle, lut, L, steps)
        if bits is None:
            continue
        if max_dist(bits) > max_dist_allowed:
            continue
        # Also check extent <= 4
        grid = seed_grid(L, particle)
        ok = True
        for _ in range(steps):
            grid = stream(grid)
            grid = collide(grid, lut)
            if int(grid.sum()) != b0 or max(bounding_extent(grid)) > 4:
                ok = False
                break
        if ok:
            found.append(list(subset))
    return found

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

    # Generate symmetric LUTs
    perms = get_oh_permutations()
    action = precompute_perm_action(perms)
    orbits, _ = compute_orbits(action)
    stabs = compute_all_stabilizers(action)

    luts = [("lut08", lut08), ("sym_42", generate_symmetric_lut(42, perms, action, orbits, stabs)),
            ("sym_123", generate_symmetric_lut(123, perms, action, orbits, stabs)),
            ("sym_999", generate_symmetric_lut(999, perms, action, orbits, stabs))]
    for name, lut in luts[1:]:
        v = verify_lut(lut, action)
        assert v["bijection"] and v["bit_conserving"] and v["symmetric"], f"{name} failed"

    BT, BT_inv = make_BT()

    # Task 1
    w1_results = {}
    for name, lut in luts:
        w1_results[name] = weight1_cycles(lut, BT_inv)
        print(f"[{name}] weight-1 cycles: {len(w1_results[name])}")
        for c in w1_results[name]:
            print(f"  period={c['period']} channels={c['cycle']} v_grid={c['velocity_grid']} v_cart={c['velocity_cart']} axis_aligned={c['axis_aligned']}")

    # Task 2
    w2_results = {}
    for name, lut in luts:
        w2_results[name] = search_coherent(lut, 2, 1)
        print(f"[{name}] weight-2 coherent: {len(w2_results[name])}")

    # Task 3
    w3_results = {}
    for name, lut in luts:
        w3_results[name] = search_coherent(lut, 3, 2)
        print(f"[{name}] weight-3 coherent: {len(w3_results[name])}")

    # Task 4: cross-LUT comparison
    species_counts = {name: len(w1_results[name]) for name, _ in luts}
    genuine_multibit = any(len(w2_results[n]) > 0 or len(w3_results[n]) > 0 for n, _ in luts)

    # Determine F1
    all_single_bit = all(species_counts[n] > 0 for n, _ in luts)
    f1_triggered = all_single_bit and not genuine_multibit

    # Build JSON output
    output = {
        "lut08_weight1_cycles": w1_results["lut08"],
        "sym_42_weight1_cycles": w1_results["sym_42"],
        "sym_123_weight1_cycles": w1_results["sym_123"],
        "sym_999_weight1_cycles": w1_results["sym_999"],
        "weight2_coherent_structures": {k: v for k, v in w2_results.items()},
        "weight3_coherent_structures": {k: v for k, v in w3_results.items()},
        "species_counts": species_counts,
        "genuine_multibit_gliders_found": genuine_multibit,
        "f1_triggered": f1_triggered,
        "verdict": "MONOSPECIFIC: all dynamics are composites of single-bit streaming particles. F1 TRIGGERED." if f1_triggered else "MULTISPECIFIC: genuine multi-bit coherent structures exist."
    }
    with open(out_dir / "fundamental_spectrum.json", "w") as f:
        json.dump(output, f, indent=2)

    # Markdown report
    md = ["# Fundamental Spectrum Analysis (Iter 248)\n",
          "## Task 1: Weight-1 Single-Bit Particle Spectrum\n"]
    for name, _ in luts:
        md.append(f"### {name}\n")
        md.append(f"Distinct single-bit species (cycles): **{len(w1_results[name])}**\n")
        md.append("| Period | Channels | v_grid | v_cart | Axis-Aligned |\n")
        md.append("|---|---|---|---|---|\n")
        for c in w1_results[name]:
            vg = ", ".join(f"{x:.3f}" for x in c["velocity_grid"])
            vc = ", ".join(f"{x:.3f}" for x in c["velocity_cart"])
            md.append(f"| {c['period']} | {c['cycle']} | ({vg}) | ({vc}) | {c['axis_aligned']} |\n")
        md.append("\n")

    md.append("## Task 2: Weight-2 Coherent Structures\n")
    for name, _ in luts:
        md.append(f"- **{name}**: {len(w2_results[name])} structures found\n")
        if w2_results[name]:
            md.append(f"  - {w2_results[name]}\n")
    md.append("\n")

    md.append("## Task 3: Weight-3 Coherent Structures\n")
    for name, _ in luts:
        md.append(f"- **{name}**: {len(w3_results[name])} structures found\n")
        if w3_results[name]:
            md.append(f"  - {w3_results[name]}\n")
    md.append("\n")

    md.append("## Task 4: Cross-LUT Comparison\n")
    md.append(f"Species counts: {species_counts}\n")
    md.append(f"Genuine multi-bit gliders found: **{genuine_multibit}**\n")
    md.append(f"F1 triggered: **{f1_triggered}**\n")
    md.append(f"\n**Verdict**: {output['verdict']}\n")

    md.append("\n## Critical Analysis\n")
    md.append("Since O_h acts transitively on the 12 NN channels, ALL single-bit particles are in the SAME O_h orbit. ")
    if f1_triggered:
        md.append("With no genuine multi-bit coherent structures found, the taxonomy is **MONOSPECIFIC**. ")
        md.append("All observed 'gliders' are non-interacting composites of single-bit streaming particles. ")
        md.append("This satisfies the Phase 7.1 falsification criterion F1.\n")
    else:
        md.append("However, genuine multi-bit structures were found, indicating a multispecific taxonomy.\n")

    with open(out_dir / "fundamental_spectrum_report.md", "w") as f:
        f.write("".join(md))

    print(f"\n[done] F1 triggered: {f1_triggered}")
    print(f"[done] Verdict: {output['verdict']}")

if __name__ == "__main__":
    main()
