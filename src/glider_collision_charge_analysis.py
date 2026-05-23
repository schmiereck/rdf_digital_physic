#!/usr/bin/env python3
"""Two-glider collision scan under LUT-08: chirality & sub-lattice charge conservation."""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import deque
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import SHIFTS, stream, collide  # noqa: E402
from src.search_3d_gliders import fcc_neighbor_vectors  # noqa: E402

L = 32
SUB = {(0, 0, 0): 0, (1, 1, 0): 1, (1, 0, 1): 2, (0, 1, 1): 3}


def make_BT():
    S, C = np.array(SHIFTS, float), fcc_neighbor_vectors().astype(float)
    BT = np.linalg.inv(C[[0, 4, 8]]) @ S[[0, 2, 6]]; return BT, np.linalg.inv(BT)


def reflect(part, BT, BT_inv):
    out = []
    for (l, r, c, ch) in part:
        cart = np.array([l, r, c], float) @ BT_inv; cart[0] = -cart[0]; g = cart @ BT
        out.append((int(round(g[0])), int(round(g[1])), int(round(g[2])), ch))
    return out


def place(grid, part, o):
    for (dl, dr, dc, ch) in part: grid[(o[0]+dl) % L, (o[1]+dr) % L, (o[2]+dc) % L, ch] = 1


def step_part(part, lut):
    g = np.zeros((L, L, L, 12), np.uint8); c = L // 2; place(g, part, (c, c, c)); g = collide(stream(g), lut)
    return [(int(i[0]-c), int(i[1]-c), int(i[2]-c), int(i[3])) for i in np.argwhere(g > 0)]


def clusters(bits, R=4):
    n = len(bits); seen = [False]*n; out = []
    for i in range(n):
        if seen[i]: continue
        comp, seen[i], q = [i], True, deque([i])
        while q:
            u = q.popleft()
            for j in range(n):
                if seen[j]: continue
                d = sum(min(abs(bits[u][k]-bits[j][k]), L-abs(bits[u][k]-bits[j][k])) for k in range(3))
                if d <= R: seen[j] = True; comp.append(j); q.append(j)
        out.append([bits[k] for k in comp])
    return out


def chi(cl, BT_inv):
    ref = cl[0][:3]
    cart = [np.array(tuple(((b[i]-ref[i]+L//2) % L) - L//2 + ref[i] for i in range(3)), float) @ BT_inv for b in cl]
    cart.sort(key=lambda v: tuple(np.round(v, 6)))
    return float((cart[1]-cart[0]).dot(np.cross(cart[2]-cart[0], cart[3]-cart[0])))


def Q(bits):
    q = [0, 0, 0, 0]
    for (l, r, c, _) in bits: q[SUB[((r + c) % 2, r % 2, c % 2)]] += 1
    return tuple(q)


def analyze(g, BT_inv):
    bits = [tuple(map(int, x)) for x in np.argwhere(g > 0)]; n_gl, cs = 0, 0.0
    for cl in clusters(bits):
        if len(cl) == 4:
            ch = chi(cl, BT_inv)
            if abs(abs(ch)-4) < 1e-6 or abs(abs(ch)-2) < 1e-6: n_gl += 1; cs += ch
    return len(bits), Q(bits), n_gl, cs


def main():
    with open(ROOT/"archive/iter_224/results/glider_00_lut08_sub03.json") as f: d = json.load(f)
    lut = np.array(d["lut"], np.uint16); pA = [tuple(c) for c in d["particle"]]
    BT, BT_inv = make_BT(); pB = reflect(pA, BT, BT_inv); pAp = step_part(pA, lut)
    print(f"BT =\n{BT}\nBT_inv =\n{BT_inv}\nA seed       = {pA}\nB (x-refl)   = {pB}\nA' (phase+1) = {pAp}\n")
    cfgs = [(pA,(6,16,6),pB,(26,16,26),"head_on_aligned"), (pAp,(6,16,6),pB,(26,16,26),"head_on_phase1"),
            (pA,(6,16,6),pB,(26,17,26),"head_on_dy1"), (pA,(6,16,6),pB,(26,19,26),"off_center_dy3"),
            (pA,(6,16,6),pB,(26,16,28),"off_center_dz2"), (pA,(6,16,6),pB,(26,18,28),"glancing_dy2_dz2"),
            (pA,(6,16,6),pB,(26,20,28),"glancing_dy4_dz2"), (pA,(6,14,4),pB,(26,18,28),"off_center_asym"),
            (pA,(4,16,4),pB,(28,16,28),"head_on_far"), (pAp,(10,16,10),pB,(22,22,22),"phase1_off_ctr")]
    print(f"{'#':>2} {'label':>18} {'N0':>3} {'Q0':>14} {'Nf':>3} {'Qf':>14} {'gIn':>3} {'gOut':>4} {'chiIn':>6} {'chiOut':>7} {'outcome':>18}")
    rows = []
    for i, (a, oa, b, ob, lbl) in enumerate(cfgs):
        g = np.zeros((L, L, L, 12), np.uint8); place(g, a, oa); place(g, b, ob)
        N0, q0, gIn, chiIn = analyze(g, BT_inv); Qt = [q0]; ok = True
        for _ in range(100):
            g = collide(stream(g), lut); bits = [tuple(map(int, x)) for x in np.argwhere(g > 0)]
            if len(bits) != N0: ok = False
            Qt.append(Q(bits))
        Nf, qf, gOut, chiOut = analyze(g, BT_inv)
        outcome = "Elastic" if (gOut == 2 and Nf == 8) else "Glider+Debris" if gOut == 1 else "Inelastic Debris" if gOut == 0 else f"{gOut}-cluster"
        rows.append((lbl, N0, Nf, gIn, gOut, chiIn, chiOut, outcome, Qt, ok))
        print(f"{i:>2} {lbl:>18} {N0:>3} {str(q0):>14} {Nf:>3} {str(qf):>14} {gIn:>3} {gOut:>4} {chiIn:>+6.1f} {chiOut:>+7.1f} {outcome:>18}")
    n_el = sum(1 for r in rows if r[7] == "Elastic"); chi_eq = sum(1 for r in rows if abs(r[5]-r[6]) < 1e-6)
    bit_cons = all(r[9] for r in rows); Qmix = (np.array(rows[0][8]).max(0) - np.array(rows[0][8]).min(0)).tolist()
    print(f"\nElastic outcomes: {n_el}/10   chi_in==chi_out: {chi_eq}/10   strict bit conservation: {bit_cons}")
    print(f"Q(t) range over t=0..100 (run 0): {Qmix}   distinct Q states (run 0): {len(set(rows[0][8]))}")
    print("\nPre-registered falsification criteria:")
    print(f"  F1 bit count strictly conserved:   {'PASS' if bit_cons else 'FAIL'}")
    print(f"  F2 sum of chi conserved per run:   {'PASS' if chi_eq == 10 else f'FAIL ({chi_eq}/10)'}")
    print(f"  F3 Q mixing stays bounded (single-glider range <=2): {'PASS' if max(Qmix) <= 2 else f'MIX (max range {max(Qmix)})'}")
    print(f"  F4 at least one elastic collision:  {'PASS' if n_el >= 1 else 'FAIL'}")

if __name__ == "__main__": main()
