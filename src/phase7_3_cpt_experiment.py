#!/usr/bin/env python3
"""Phase 7.3 — Antiparticle CPT Experiment (compact)"""
import json, sys
from pathlib import Path
from collections import deque
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import stream, collide
from src.glider_charge_analysis import make_BT, reflect
from src.rigorous_glider_audit import build_oh_transforms, seed_grid, compute_com_circular

L = 32

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
    for dl, dr, dc, ch in part: g[(o[0] + dl) % L, (o[1] + dr) % L, (o[2] + dc) % L, ch] = 1

def solo(part, lut):
    g = seed_grid(L, part)
    for _ in range(80):
        g = step(g, lut)
        if int(g.sum()) != 4: return False
    return True

def collision(a, oa, b, ob, lut, steps=100):
    g = np.zeros((L, L, L, 12), np.uint8); place(g, a, oa); place(g, b, ob)
    for _ in range(steps): g = step(g, lut)
    bits = [tuple(map(int, x)) for x in np.argwhere(g > 0)]
    return classify(bits)

def disp1(part, lut):
    g = seed_grid(L, part); g1 = step(g, lut)
    c0, _ = compute_com_circular(g); c1, _ = compute_com_circular(g1)
    return np.array([(c1[i] - c0[i] + L / 2) % L - L / 2 for i in range(3)])

def find_pC(pA, lut, transforms):
    dA = disp1(pA, lut); best = None; bestsc = -1
    for perm, M in transforms:
        if round(np.linalg.det(M)) != 1: continue
        pC = []
        for l, r, c, ch in pA:
            v = M @ np.array([l, r, c], float)
            pC.append((int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch])))
        dC = disp1(pC, lut)
        sc = -np.linalg.norm(dC + dA)
        if best is None or sc > bestsc: best, bestsc = pC, sc
    return best

def main():
    lut, pA = load(); BT, BT_inv = make_BT(); transforms = build_oh_transforms()
    pB = reflect(pA, BT, BT_inv); pC = find_pC(pA, lut, transforms)
    print("CONTROL A: pB solo stable =", solo(pB, lut))
    if pC != pA: print("CONTROL A: pC solo stable =", solo(pC, lut))
    offs = [(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 0, 1), (0, 1, 1)]
    baseA, baseB = (6, 16, 6), (26, 16, 26)
    results = []
    print("\nEXPERIMENT: opposite-chirality collisions")
    print("#  offset       outcome        bits n4 n1")
    for i, o in enumerate(offs):
        out, nb, n4, n1 = collision(pA, baseA, pB, ((baseB[0] + o[0]) % L, (baseB[1] + o[1]) % L, (baseB[2] + o[2]) % L), lut)
        results.append({"type": "opposite", "offset": o, "outcome": out, "bits": nb, "n4": n4, "n1": n1})
        print(f"{i}  {o}  {out:12s}   {nb:>4} {n4:>2} {n1:>2}")
    print("\nCONTROL B: same-chirality collisions")
    for i, o in enumerate(offs):
        out, nb, n4, n1 = collision(pA, baseA, pC, ((baseB[0] + o[0]) % L, (baseB[1] + o[1]) % L, (baseB[2] + o[2]) % L), lut)
        results.append({"type": "same", "offset": o, "outcome": out, "bits": nb, "n4": n4, "n1": n1})
        print(f"{i}  {o}  {out:12s}   {nb:>4} {n4:>2} {n1:>2}")
    # O_h covariance: first non-identity proper rotation
    perm, M = next((p, M) for p, M in transforms if round(np.linalg.det(M)) == 1 and not np.allclose(M, np.eye(3)))
    def rot(part):
        return [(int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch])) for l, r, c, ch in part for v in [M @ np.array([l, r, c], float)]]
    pAr, pBr = rot(pA), rot(pB)
    oAr = tuple(np.round(M @ np.array(baseA, float)).astype(int) % L)
    oBr = tuple(np.round(M @ np.array(baseB, float)).astype(int) % L)
    out, nb, n4, n1 = collision(pAr, oAr, pBr, oBr, lut)
    results.append({"type": "oh_rotated", "offset": (0, 0, 0), "outcome": out, "bits": nb, "n4": n4, "n1": n1})
    print(f"\nO_h rotated head-on: {out}  bits={nb} n4={n4} n1={n1}")
    outd = ROOT / "archive/iter_245/results"; outd.mkdir(parents=True, exist_ok=True)
    with open(outd / "cpt_experiment_results.json", "w") as f: json.dump(results, f, indent=2)
    print(f"\nSaved to {outd / 'cpt_experiment_results.json'}")

if __name__ == "__main__": main()
