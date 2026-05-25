#!/usr/bin/env python3
"""Experiment 246: L=64 O_h Covariance with Coordinate-Rounding Diagnostics"""
import json, sys
from pathlib import Path
from collections import deque
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import stream, collide
from src.glider_charge_analysis import make_BT, reflect
from src.rigorous_glider_audit import build_oh_transforms, seed_grid, compute_com_circular

L = 64
SUB = {(0, 0, 0): 0, (1, 1, 0): 1, (1, 0, 1): 2, (0, 1, 1): 3}

def load():
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        d = json.load(f)
    return np.array(d["lut"], np.uint16), [tuple(c) for c in d["particle"]]

def step(g, lut): return collide(stream(g), lut)

def clusters(bits, R=4):
    n = len(bits); seen = [False] * n; out = []
    for i in range(n):
        if seen[i]: continue
        comp, seen[i], q = [i], True, deque([i])
        while q:
            u = q.popleft()
            for j in range(n):
                if seen[j]: continue
                d = sum(min(abs(bits[u][k] - bits[j][k]), L - abs(bits[u][k] - bits[j][k])) for k in range(3))
                if d <= R: seen[j] = True; comp.append(j); q.append(j)
        out.append([bits[k] for k in comp])
    return out

def classify(bits):
    cs = clusters(bits); n4 = sum(1 for c in cs if len(c) == 4)
    n1 = sum(1 for c in cs if len(c) == 1); tot = len(bits)
    if n4 == 2 and len(cs) == 2: return "Elastic", tot, n4, n1
    if n4 == 0 and len(cs) == tot and tot > 0: return "Annihilation", tot, n4, n1
    if n4 == 1: return "Partial", tot, n4, n1
    return "Chaotic", tot, n4, n1

def place(g, part, o):
    for dl, dr, dc, ch in part:
        g[(o[0] + dl) % L, (o[1] + dr) % L, (o[2] + dc) % L, ch] = 1

def solo(part, lut):
    g = np.zeros((L, L, L, 12), np.uint8); place(g, part, (L // 2, L // 2, L // 2))
    for t in range(80):
        g = step(g, lut)
        if int(g.sum()) != 4: return False, t
    return True, None

def collision(a, oa, b, ob, lut, steps=80):
    g = np.zeros((L, L, L, 12), np.uint8); place(g, a, oa); place(g, b, ob)
    for _ in range(steps): g = step(g, lut)
    bits = [tuple(map(int, x)) for x in np.argwhere(g > 0)]
    return classify(bits)

def disp1(part, lut):
    g = np.zeros((L, L, L, 12), np.uint8); place(g, part, (L // 2, L // 2, L // 2)); g1 = step(g, lut)
    c0, _ = compute_com_circular(g); c1, _ = compute_com_circular(g1)
    if c0 is None or c1 is None: return None
    return np.array([(c1[i] - c0[i] + L / 2) % L - L / 2 for i in range(3)])

def find_pC(pA, lut, transforms):
    dA = disp1(pA, lut)
    if dA is None: return None
    best = None; bestsc = -1
    for perm, M in transforms:
        if round(np.linalg.det(M)) != 1: continue
        pC = []
        for l, r, c, ch in pA:
            v = M @ np.array([l, r, c], float)
            pC.append((int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch])))
        dC = disp1(pC, lut)
        if dC is None: continue
        sc = -np.linalg.norm(dC + dA)
        if best is None or sc > bestsc: best, bestsc = pC, sc
    return best

def subidx(pos): return SUB.get((int(pos[0]) % 2, int(pos[1]) % 2, int(pos[2]) % 2), -1)

def toroidal_dist(a, b):
    diffs = []
    for k in range(3):
        ak, bk = int(a[k]) % L, int(b[k]) % L
        d = abs(ak - bk)
        diffs.append(min(d, L - d))
    return float(np.linalg.norm(diffs))

def diagnostic(pA, oA, pB, oB, pAr, oAr, pBr, oBr, M_g, BT_inv, label):
    print(f"\n{'='*60}\nDIAGNOSTIC: {label}\n{'='*60}")
    for tag, part, o in [("A", pA, oA), ("B", pB, oB), ("A_rot", pAr, oAr), ("B_rot", pBr, oBr)]:
        print(f"\n[{tag}] Absolute positions:")
        subs = []
        for i, (dl, dr, dc, ch) in enumerate(part):
            lat = (int(o[0]) + dl, int(o[1]) + dr, int(o[2]) + dc)
            cart = np.array(lat, float) @ BT_inv
            sub = subidx(lat)
            subs.append(sub)
            print(f"  bit{i}: lat={lat} cart={np.round(cart, 6).tolist()} sub={sub}")
        print(f"  Sub-lattice pattern: {tuple(sorted(subs))}")
    print("\n[Rounding errors for rotated gliders]")
    max_err = 0.0
    for tag, part_o, part_r, o_o, o_r in [("A", pA, pAr, oA, oAr), ("B", pB, pBr, oB, oBr)]:
        errs = []
        for i, (dl, dr, dc, ch) in enumerate(part_o):
            exact = M_g @ np.array([o_o[0] + dl, o_o[1] + dr, o_o[2] + dc], float)
            rounded = np.array([o_r[0] + part_r[i][0], o_r[1] + part_r[i][1], o_r[2] + part_r[i][2]], float)
            err = toroidal_dist(exact, rounded)
            errs.append(err); max_err = max(max_err, err)
        print(f"  Glider {tag}: errs={np.round(errs, 12).tolist()} max={max(errs):.2e}")
    def minsep(part1, o1, part2, o2):
        return min(toroidal_dist((int(o1[0])+dl1, int(o1[1])+dr1, int(o1[2])+dc1),
                                  (int(o2[0])+dl2, int(o2[1])+dr2, int(o2[2])+dc2))
                   for dl1, dr1, dc1, _ in part1 for dl2, dr2, dc2, _ in part2)
    sep_unrot = minsep(pA, oA, pB, oB)
    sep_rot = minsep(pAr, oAr, pBr, oBr)
    print(f"\nMinimum separation unrotated: {sep_unrot:.6f}")
    print(f"Minimum separation rotated:   {sep_rot:.6f}")
    def get_pattern(part, o):
        return tuple(sorted(subidx((int(o[0])+dl, int(o[1])+dr, int(o[2])+dc)) for dl, dr, dc, _ in part))
    patA, patB = get_pattern(pA, oA), get_pattern(pB, oB)
    patAr, patBr = get_pattern(pAr, oAr), get_pattern(pBr, oBr)
    print(f"\nSub-lattice phase A={patA} B={patB} match={'YES' if patA == patB else 'NO'}")
    print(f"Sub-lattice phase Ar={patAr} Br={patBr} match={'YES' if patAr == patBr else 'NO'}")
    phase_mismatch = (patA != patAr) or (patB != patBr) or (patAr != patBr)
    align_mismatch = (max_err > 1e-10) or phase_mismatch
    print(f"\nALIGNMENT_MISMATCH={align_mismatch}  (max_err={max_err:.2e}, phase_mismatch={phase_mismatch})")
    return {"max_rounding_error": max_err, "phase_mismatch": phase_mismatch,
            "alignment_mismatch": align_mismatch, "min_sep_unrot": sep_unrot,
            "min_sep_rot": sep_rot, "sub_pat_A": patA, "sub_pat_B": patB,
            "sub_pat_Ar": patAr, "sub_pat_Br": patBr}

def to_int_tuple(t): return tuple(int(x) for x in t)

def main():
    with open(ROOT / "src/pre_registration.md") as f:
        print(f.read())
    print("\n" + "=" * 60 + "\nBEGINNING EXPERIMENT\n" + "=" * 60)
    lut, pA = load(); BT, BT_inv = make_BT(); transforms = build_oh_transforms()
    pB = reflect(pA, BT, BT_inv); pC = find_pC(pA, lut, transforms)
    proper = [(p, M) for p, M in transforms if round(np.linalg.det(M)) == 1]
    first_rot = next((p, M) for p, M in proper if not np.allclose(M, np.eye(3)))
    second_rot = next((p, M) for p, M in proper if not np.allclose(M, np.eye(3)) and not np.allclose(M, first_rot[1]))
    def rot(part, perm, M):
        return [(int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch]))
                for l, r, c, ch in part for v in [M @ np.array([l, r, c], float)]]
    oA, oB = (22, 32, 22), (42, 32, 42)
    oAr = to_int_tuple(np.round(first_rot[1] @ np.array(oA, float)).astype(int) % L)
    oBr = to_int_tuple(np.round(first_rot[1] @ np.array(oB, float)).astype(int) % L)
    pAr = rot(pA, first_rot[0], first_rot[1])
    pBr = rot(pB, first_rot[0], first_rot[1])
    oA2 = to_int_tuple(np.round(second_rot[1] @ np.array(oA, float)).astype(int) % L)
    oB2 = to_int_tuple(np.round(second_rot[1] @ np.array(oB, float)).astype(int) % L)
    pA2 = rot(pA, second_rot[0], second_rot[1])
    pB2 = rot(pB, second_rot[0], second_rot[1])
    diag1 = diagnostic(pA, oA, pB, oB, pAr, oAr, pBr, oBr, first_rot[1], BT_inv, "First O_h rotation")
    print("\n" + "=" * 60 + "\nSOLO STABILITY CONTROLS\n" + "=" * 60)
    solos = {}
    for tag, part in [("pA", pA), ("pB", pB), ("pAr", pAr), ("pBr", pBr), ("pA2", pA2), ("pB2", pB2)]:
        ok, fail_t = solo(part, lut)
        solos[tag] = ok
        print(f"solo {tag}: {'STABLE' if ok else 'FAILED at t=' + str(fail_t)}")
    print("\n" + "=" * 60 + "\nCOLLISION RUNS\n" + "=" * 60)
    results = []
    out, nb, n4, n1 = collision(pA, oA, pB, oB, lut)
    results.append({"config": "unrotated_opposite", "outcome": out, "bits": nb, "n4": n4, "n1": n1})
    print(f"(a) Unrotated opposite: {out} bits={nb} n4={n4} n1={n1}")
    out, nb, n4, n1 = collision(pAr, oAr, pBr, oBr, lut)
    results.append({"config": "oh_rotated_1", "outcome": out, "bits": nb, "n4": n4, "n1": n1})
    print(f"(b) O_h rotated (1st):  {out} bits={nb} n4={n4} n1={n1}")
    diag2 = diagnostic(pA, oA, pB, oB, pA2, oA2, pB2, oB2, second_rot[1], BT_inv, "Second O_h rotation")
    out, nb, n4, n1 = collision(pA2, oA2, pB2, oB2, lut)
    results.append({"config": "oh_rotated_2", "outcome": out, "bits": nb, "n4": n4, "n1": n1})
    print(f"(c) O_h rotated (2nd):  {out} bits={nb} n4={n4} n1={n1}")
    if pC is not None:
        out, nb, n4, n1 = collision(pA, oA, pC, oB, lut)
        results.append({"config": "same_chirality", "outcome": out, "bits": nb, "n4": n4, "n1": n1})
        print(f"(d) Same chirality:     {out} bits={nb} n4={n4} n1={n1}")
    outd = ROOT / "archive/iter_246/results"; outd.mkdir(parents=True, exist_ok=True)
    summary = {"L": L, "center": (32, 32, 32), "solo_stability": solos,
               "collision_results": results, "diagnostic_rot1": diag1, "diagnostic_rot2": diag2,
               "origins": {"A": oA, "B": oB, "Ar": list(oAr), "Br": list(oBr), "A2": list(oA2), "B2": list(oB2)}}
    with open(outd / "oh_covariance_64_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved JSON to {outd / 'oh_covariance_64_results.json'}")
    unrot = next(r for r in results if r["config"] == "unrotated_opposite")
    rot1 = next(r for r in results if r["config"] == "oh_rotated_1")
    rot2 = next(r for r in results if r["config"] == "oh_rotated_2")
    md = ["# Iteration 246: O_h Covariance on L=64\n",
          "## Pre-Declared Hypothesis & Falsification Criteria",
          "See `src/pre_registration.md` for the full pre-registration.\n",
          "## Protocol", f"- Grid: L={L} FCC toroidal", "- Collision center: (32, 32, 32)",
          f"- Origins: pA at {oA}, pB at {oB}", "- Steps: 80",
          f"- O_h rotations: first={first_rot[1].tolist()}, second={second_rot[1].tolist()}\n",
          "## Observations", "\n### Coordinate-Rounding Diagnostic (Rotation 1)"]
    for k, v in diag1.items(): md.append(f"- {k}: {v}")
    md.append("\n### Coordinate-Rounding Diagnostic (Rotation 2)")
    for k, v in diag2.items(): md.append(f"- {k}: {v}")
    md.append("\n### Solo Stability")
    for k, v in solos.items(): md.append(f"- {k}: {'STABLE' if v else 'FAILED'}")
    md.extend(["\n### Collision Outcomes", "| Config | Outcome | Bits | n4 | n1 |",
               "|--------|---------|------|----|----|"])
    for r in results: md.append(f"| {r['config']} | {r['outcome']} | {r['bits']} | {r['n4']} | {r['n1']} |")
    md.append("\n## Verdict")
    f1 = (rot1["outcome"] != unrot["outcome"])
    md.append(f"\n**F1** (Rotated differs from unrotated): {'REFUTED' if f1 else 'NOT REFUTED'}")
    md.append(f"  - Unrotated: {unrot['outcome']}, Rotated-1: {rot1['outcome']}")
    f2 = (unrot["outcome"] != "Elastic")
    md.append(f"\n**F2** (Unrotated not Elastic): {'REFUTED' if f2 else 'NOT REFUTED'}")
    f3 = not all(solos.values())
    md.append(f"\n**F3** (Solo stability failed): {'REFUTED' if f3 else 'NOT REFUTED'}")
    if f1 and diag1["alignment_mismatch"]:
        md.append(f"\n**F4-enhanced**: ALIGNMENT MISMATCH identified.")
        md.append(f"  Outcome difference attributed to coordinate-rounding artifact.")
    else:
        md.append(f"\n**F4-enhanced**: {'No alignment mismatch' if not diag1['alignment_mismatch'] else 'Mismatch present but F1 not triggered'}")
    if diag1["alignment_mismatch"] and rot2["outcome"] == unrot["outcome"] and not diag2["alignment_mismatch"]:
        md.append(f"\n**F5**: PARTIALLY CONFIRMED — second proper rotation yields same outcome as unrotated.")
    else:
        md.append(f"\n**F5**: Not applicable or not confirmed.")
    md.extend(["\n## Construction-vs-Empirical Note",
               "All glider structures were constructed algorithmically from the LUT-08 seed. No post-hoc parameter tuning was performed.",
               "\n## Limitations",
               "- Only two O_h rotations tested; full 48-element group coverage not attempted.",
               "- Classification taxonomy is coarse (Elastic/Partial/Chaotic/Annihilation).",
               "- Debris dynamics not analysed beyond bit counting.",
               f"- L={L} grid may still exhibit wrap-around effects for very long runs (>80 steps)."])
    with open(outd / "RESEARCH-RESULT-246.md", "w") as f:
        f.write("\n".join(md))
    print(f"Saved report to {outd / 'RESEARCH-RESULT-246.md'}")

if __name__ == "__main__":
    main()
