#!/usr/bin/env python3
"""Chirality chi(t) and sub-lattice charge q(t) analysis of the LUT-08 glider."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import SHIFTS, stream, collide  # noqa: E402
from src.search_3d_gliders import fcc_neighbor_vectors  # noqa: E402

L = 32
SUB = {(0, 0, 0): 0, (1, 1, 0): 1, (1, 0, 1): 2, (0, 1, 1): 3}


def make_BT():
    S, C = np.array(SHIFTS, dtype=float), fcc_neighbor_vectors().astype(float)
    BT = np.linalg.inv(C[[0, 4, 8]]) @ S[[0, 2, 6]]
    return BT, np.linalg.inv(BT)


def seed(particle):
    g, c = np.zeros((L, L, L, 12), dtype=np.uint8), L // 2
    for (dl, dr, dc, ch) in particle:
        g[(c + dl) % L, (c + dr) % L, (c + dc) % L, ch] = 1
    return g


def bits_cartesian(grid, BT_inv):
    bits = np.argwhere(grid > 0)
    if len(bits) == 0:
        return []
    ref = bits[0][:3]
    uw = [tuple(((b[i] - ref[i] + L // 2) % L) - L // 2 + ref[i] for i in range(3)) for b in bits]
    return sorted([np.array(u, dtype=float) @ BT_inv for u in uw], key=lambda v: tuple(np.round(v, 6)))


def chi_and_q(coords):
    chi = (coords[1] - coords[0]).dot(np.cross(coords[2] - coords[0], coords[3] - coords[0]))
    q = [0, 0, 0, 0]
    for r in coords:
        q[SUB[(int(round(r[0])) % 2, int(round(r[1])) % 2, int(round(r[2])) % 2)]] += 1
    return chi, tuple(q)


def run(particle, lut, BT_inv, label, steps=100):
    grid, chis, qs = seed(particle), [], []
    print(f"\n[{label}] step    chi(t)        q(t)")
    for t in range(steps + 1):
        coords = bits_cartesian(grid, BT_inv)
        if len(coords) != 4:
            print(f"  t={t}: instability (bits={len(coords)})"); return None, None
        chi, q = chi_and_q(coords)
        chis.append(chi); qs.append(q)
        if t < 12 or t % 10 == 0 or t == steps:
            print(f"  {t:3d}  {chi:+12.6f}   {q}")
        grid = collide(stream(grid), lut)
    return np.array(chis), qs


def detect_M(qs):
    base = np.array(qs[0])
    for t in range(1, len(qs)):
        for sigma in [(0, 2, 3, 1), (0, 3, 1, 2), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0)]:
            if tuple(base[list(sigma)]) == qs[t]:
                M = np.zeros((4, 4), int)
                for i in range(4): M[sigma[i], i] = 1
                return M, t, sigma
    return None, None, None


def reflect(particle, BT, BT_inv):
    out = []
    for (l, r, c, ch) in particle:
        cart = np.array([l, r, c], dtype=float) @ BT_inv
        cart[0] = -cart[0]
        g = cart @ BT
        out.append((int(round(g[0])), int(round(g[1])), int(round(g[2])), ch))
    return out


def main():
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        d = json.load(f)
    lut = np.array(d["lut"], dtype=np.uint16)
    particle = [tuple(c) for c in d["particle"]]
    BT, BT_inv = make_BT()
    print(f"BT =\n{BT}\nBT_inv =\n{BT_inv}\n\nLUT-08 particle (l, r, c, ch): {particle}")
    print("\nInitial Cartesian coords of the 4 bits:")
    for r in bits_cartesian(seed(particle), BT_inv):
        par = (int(round(r[0])) % 2, int(round(r[1])) % 2, int(round(r[2])) % 2)
        print(f"  cart={np.round(r, 4).tolist()}  parity={par}  sublattice=L_{SUB[par]}")
    chis, qs = run(particle, lut, BT_inv, "ORIGINAL")
    print(f"\nchi(t) strictly constant: {np.allclose(chis, chis[0])}; period-2 phase: {np.allclose(chis[::2], chis[0]) and np.allclose(chis[1::2], chis[1])}")
    print(f"Even-step chi = {chis[0]:+.4f}; Odd-step chi = {chis[1]:+.4f}; distinct q(t): {sorted(set(qs))}")
    M, t_m, sigma = detect_M(qs)
    if M is not None:
        print(f"\nCyclic permutation matrix M (q(t={t_m}) = M q(0), sigma={sigma}):\n{M}")
        print(f"Verified q(t+1) = M q(t) for all t in [0,99]: {all(tuple((M @ np.array(qs[t])).tolist()) == qs[t + 1] for t in range(len(qs) - 1))}")
    refl = reflect(particle, BT, BT_inv)
    print(f"\nReflected particle (x -> -x): {refl}")
    chis_r, qs_r = run(refl, lut, BT_inv, "REFLECTED")
    if chis_r is not None:
        print(f"\nReflected chi(t) = -chi_original(t) at every step: {np.allclose(chis_r, -chis)}; reflected glider stable over 100 steps: True")


if __name__ == "__main__":
    main()
