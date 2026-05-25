#!/usr/bin/env python3
"""Sweep all 24 proper O_h rotations on L=64 for opposite-chirality collision."""
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

def step(g, lut):
    return collide(stream(g), lut)

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

def sub_pat(part, origin):
    result = []
    for dl, dr, dc, ch in part:
        l, r, c = (origin[0] + dl) % L, (origin[1] + dr) % L, (origin[2] + dc) % L
        key = (l % 2, r % 2, c % 2)
        result.append(SUB.get(key, -1))
    return result

def rot_part(part, perm, M):
    out = []
    for l, r, c, ch in part:
        v = M @ np.array([l, r, c], float)
        out.append((int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch])))
    return out

def rot_origin(origin, M):
    return tuple(int(round(x)) % L for x in M @ np.array(origin, float))

def max_round_err(part, M):
    err = 0.0
    for l, r, c, ch in part:
        v = M @ np.array([l, r, c], float)
        rv = np.array([round(v[0]), round(v[1]), round(v[2])])
        err = max(err, np.max(np.abs(v - rv)))
    return err

def collision(a, oa, b, ob, lut, steps=80):
    g = np.zeros((L, L, L, 12), np.uint8)
    place(g, a, oa); place(g, b, ob)
    for _ in range(steps):
        g = step(g, lut)
    bits = [tuple(map(int, x)) for x in np.argwhere(g > 0)]
    return classify(bits)

def main():
    lut, pA = load()
    BT, BT_inv = make_BT()
    pB = reflect(pA, BT, BT_inv)
    transforms = build_oh_transforms()

    # Filter to 24 proper rotations (det=+1)
    proper = [(i, perm, M) for i, (perm, M) in enumerate(transforms)
              if round(np.linalg.det(M)) == 1]

    originA = (22, 32, 22)
    originB = (42, 32, 42)

    results = []
    print(f"Sweeping {len(proper)} proper O_h rotations on L={L}")
    print(f"{'idx':>3} {'tid':>3} {'det':>3} {'outcome':>10} {'bits':>4} {'n4':>2} {'n1':>2} {'rnd_err':>8} {'mismatch':>8} {'subAr':>20} {'subBr':>20}")
    for count, (tid, perm, M) in enumerate(proper):
        is_identity = np.allclose(M, np.eye(3))
        pAr = rot_part(pA, perm, M)
        pBr = rot_part(pB, perm, M)
        oAr = rot_origin(originA, M)
        oBr = rot_origin(originB, M)
        rnd_err = max(max_round_err(pA, M), max_round_err(pB, M))
        spA = sub_pat(pAr, oAr)
        spB = sub_pat(pBr, oBr)
        has_invalid = (-1 in spA) or (-1 in spB)
        mismatch = (rnd_err > 1e-10) or has_invalid or (spA != [1, 2, 3, 3])
        outcome, nb, n4, n1 = collision(pAr, oAr, pBr, oBr, lut)
        results.append({
            "tid": tid, "is_identity": bool(is_identity), "outcome": outcome,
            "bits": nb, "n4": n4, "n1": n1, "max_round_err": float(rnd_err),
            "alignment_mismatch": bool(mismatch), "sub_pat_Ar": spA, "sub_pat_Br": spB
        })
        print(f"{count:>3} {tid:>3} {int(round(np.linalg.det(M))):>3} {outcome:>10} {nb:>4} {n4:>2} {n1:>2} {rnd_err:>8.3f} {'Y' if mismatch else 'N':>8} {str(spA):>20} {str(spB):>20}")

    elastic = sum(1 for r in results if r["outcome"] == "Elastic")
    chaotic = sum(1 for r in results if r["outcome"] == "Chaotic")
    partial = sum(1 for r in results if r["outcome"] == "Partial")
    no_mismatch_elastic = sum(1 for r in results if r["outcome"] == "Elastic" and not r["alignment_mismatch"])
    with_mismatch = sum(1 for r in results if r["alignment_mismatch"])
    without_mismatch = sum(1 for r in results if not r["alignment_mismatch"])

    print(f"\nSUMMARY:")
    print(f"  Total proper rotations: {len(proper)}")
    print(f"  Elastic: {elastic}, Chaotic: {chaotic}, Partial: {partial}")
    print(f"  With alignment mismatch: {with_mismatch}")
    print(f"  Without alignment mismatch: {without_mismatch}")
    print(f"  Elastic WITHOUT mismatch: {no_mismatch_elastic}")

    # Save
    outd = ROOT / "archive/iter_246/results"
    outd.mkdir(parents=True, exist_ok=True)
    summary = {
        "L": L, "n_proper_rotations": len(proper),
        "elastic": elastic, "chaotic": chaotic, "partial": partial,
        "with_mismatch": with_mismatch, "without_mismatch": without_mismatch,
        "elastic_without_mismatch": no_mismatch_elastic,
        "results": results
    }
    with open(outd / "multi_rotation_sweep.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved to {outd / 'multi_rotation_sweep.json'}")

if __name__ == "__main__":
    main()
