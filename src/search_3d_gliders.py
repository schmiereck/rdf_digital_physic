#!/usr/bin/env python3
"""
search_3d_gliders.py — Symmetric, bit-conserving, reversible 3D CA rule
generator and search for 3D gliders.

Pipeline:
1. Construct the 48 permutations of {0..11} corresponding to the O_h symmetry
   group of the cuboctahedron by applying all signed permutation matrices in
   R^3 to the 12 FCC nearest-neighbor vectors.
2. Decompose the 4096 states of {0,1}^12 into orbits under O_h and group by
   Hamming weight.
3. generate_symmetric_lut() produces a bijective, bit-conserving LUT that is
   invariant under all 48 O_h channel permutations.
4. Verify (bijection, bit conservation, full symmetry).
5. Seed (16,16,16,12) grids with small asymmetric particles, simulate 100
   steps via engine_3d, track center-of-mass (torus-unwrapped) and bit count,
   and report rules whose particles have bounded extent and nonzero net
   displacement.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from itertools import permutations as iperms, product
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from engine_3d import stream, collide, invert_lut  # noqa: E402


# ============================================================
# 1. Symmetries of the Cuboctahedron
# ============================================================

def fcc_neighbor_vectors() -> np.ndarray:
    """The 12 FCC nearest-neighbor vectors (cuboctahedron vertices)."""
    vecs = []
    for i in range(3):
        for j in range(i + 1, 3):
            for si in (-1, 1):
                for sj in (-1, 1):
                    v = [0, 0, 0]
                    v[i] = si
                    v[j] = sj
                    vecs.append(tuple(v))
    return np.array(vecs, dtype=int)


def get_oh_permutations(verbose: bool = False) -> list[tuple[int, ...]]:
    """Build the 48 permutations of channel indices induced by signed-permutation
    matrices acting on the 12 FCC nearest-neighbor vectors.
    """
    vecs = fcc_neighbor_vectors()
    vec_to_idx = {tuple(v): i for i, v in enumerate(vecs)}

    perms: list[tuple[int, ...]] = []
    matrices_built = 0
    for perm in iperms(range(3)):
        for signs in product((-1, 1), repeat=3):
            sigma = []
            ok = True
            for v in vecs:
                v_new = [0, 0, 0]
                for k in range(3):
                    v_new[perm[k]] = signs[k] * int(v[k])
                key = tuple(v_new)
                if key not in vec_to_idx:
                    ok = False
                    break
                sigma.append(vec_to_idx[key])
            if not ok:
                continue
            matrices_built += 1
            perms.append(tuple(sigma))

    assert matrices_built == 48, f"Expected 48 signed-perm matrices, got {matrices_built}"
    unique = sorted(set(perms))
    assert len(unique) == 48, f"Expected 48 unique permutations, got {len(unique)}"
    if verbose:
        print(f"[oh] built {len(unique)} distinct channel permutations from {matrices_built} signed perms")
    return unique


# ============================================================
# 2. Orbit decomposition of {0,1}^12 under O_h
# ============================================================

def precompute_perm_action(perms: list[tuple[int, ...]]) -> np.ndarray:
    """For each (perm, state), produce sigma(state). Shape (n_perms, 4096)."""
    n = len(perms)
    action = np.zeros((n, 4096), dtype=np.uint16)
    # Vectorized using bit-extraction
    for g, sigma in enumerate(perms):
        # For each i in 0..11 and each state s, set bit sigma[i] of result if bit i of s is set
        out = np.zeros(4096, dtype=np.uint32)
        s_arr = np.arange(4096, dtype=np.uint32)
        for i in range(12):
            mask = (s_arr >> i) & 1
            out |= mask << int(sigma[i])
        action[g] = out.astype(np.uint16)
    return action


def hamming(s: int) -> int:
    return bin(s).count('1')


def compute_orbits(action: np.ndarray) -> tuple[list[list[int]], np.ndarray]:
    """Partition {0..4095} into orbits under the action."""
    n_perms = action.shape[0]
    orbit_of = -np.ones(4096, dtype=np.int32)
    orbits: list[list[int]] = []
    for s in range(4096):
        if orbit_of[s] >= 0:
            continue
        members = {s}
        stack = [s]
        while stack:
            t = stack.pop()
            for g in range(n_perms):
                u = int(action[g, t])
                if u not in members:
                    members.add(u)
                    stack.append(u)
        oid = len(orbits)
        for t in members:
            orbit_of[t] = oid
        orbits.append(sorted(members))
    return orbits, orbit_of


def compute_all_stabilizers(action: np.ndarray) -> list[tuple[int, ...]]:
    """For each state, return the sorted tuple of permutation indices that fix it."""
    n_perms = action.shape[0]
    stabs: list[tuple[int, ...]] = []
    for s in range(4096):
        stab = [g for g in range(n_perms) if int(action[g, s]) == s]
        stabs.append(tuple(stab))
    return stabs


# ============================================================
# 3. Symmetric LUT generation
# ============================================================

def generate_symmetric_lut(
    seed: int = 0,
    perms: list[tuple[int, ...]] | None = None,
    action: np.ndarray | None = None,
    orbits: list[list[int]] | None = None,
    stabs: list[tuple[int, ...]] | None = None,
) -> np.ndarray:
    """Generate a bijective, bit-conserving, O_h-equivariant LUT of size 4096.

    Strategy: orbits with the same (Hamming weight, orbit size, stabilizer
    conjugacy class) are pooled and randomly matched. For each src->dst orbit
    pair, an equivariant bijection is built by mapping a representative
    r (with stabilizer H) to a target t in the destination orbit chosen so
    that Stab(t) == H. The map extends uniquely to f(g·r) = g·t for all g.
    """
    rng = np.random.default_rng(seed)

    if perms is None:
        perms = get_oh_permutations()
    if action is None:
        action = precompute_perm_action(perms)
    if orbits is None:
        orbits, _ = compute_orbits(action)
    if stabs is None:
        stabs = compute_all_stabilizers(action)

    n_perms = len(perms)

    # Orbit signature: (Hamming weight, orbit size, set of stabilizers as frozenset of tuples)
    # Two orbits sharing this signature have conjugate stabilizer classes and can be paired
    # equivariantly.
    orbit_sigs = []
    for o in orbits:
        rep = o[0]
        w = hamming(rep)
        sz = len(o)
        stab_set = frozenset(stabs[x] for x in o)
        orbit_sigs.append((w, sz, stab_set))

    groups: dict[tuple, list[int]] = {}
    for idx, sig in enumerate(orbit_sigs):
        groups.setdefault(sig, []).append(idx)

    lut = -np.ones(4096, dtype=np.int32)

    for sig, orbit_list in groups.items():
        n = len(orbit_list)
        # Random permutation of orbits within the group
        shuffled = list(orbit_list)
        if n > 1:
            order = rng.permutation(n)
            shuffled = [orbit_list[i] for i in order]

        for src_idx, dst_idx in zip(orbit_list, shuffled):
            src_orbit = orbits[src_idx]
            dst_orbit = orbits[dst_idx]

            rep_src = src_orbit[0]
            H_src = stabs[rep_src]

            # Targets in dst_orbit with matching stabilizer
            valid_targets = [t for t in dst_orbit if stabs[t] == H_src]
            assert len(valid_targets) > 0, (
                f"No valid target for orbit {src_idx} (size {len(src_orbit)}, weight {sig[0]})"
                f" -> orbit {dst_idx}"
            )

            target = int(valid_targets[rng.integers(len(valid_targets))])

            # Define f(g·rep_src) = g·target for all g
            for g in range(n_perms):
                src = int(action[g, rep_src])
                dst = int(action[g, target])
                if lut[src] != -1:
                    assert lut[src] == dst, (
                        f"Inconsistent equivariant map at src={src}: existing={lut[src]} new={dst}"
                    )
                lut[src] = dst

    assert (lut >= 0).all(), "LUT incomplete"
    return lut.astype(np.uint16)


# ============================================================
# Verification
# ============================================================

def verify_lut(lut: np.ndarray, action: np.ndarray) -> dict:
    """Verify the LUT is a bijection, bit-conserving, and O_h-symmetric."""
    results: dict = {}
    results['bijection'] = bool(len(np.unique(lut)) == 4096)

    pop_in = np.array([hamming(s) for s in range(4096)])
    pop_out = np.array([hamming(int(lut[s])) for s in range(4096)])
    results['bit_conserving'] = bool(np.array_equal(pop_in, pop_out))

    sym_ok = True
    bad = None
    for g in range(action.shape[0]):
        # lut[sigma_g(s)] == sigma_g(lut[s])
        lhs = lut[action[g]]
        rhs = action[g, lut]
        if not np.array_equal(lhs, rhs):
            sym_ok = False
            bad = g
            break
    results['symmetric'] = sym_ok
    if bad is not None:
        results['first_violating_perm'] = bad
    return results


# ============================================================
# 4. Glider search
# ============================================================

def seed_grid(L: int, particle: list[tuple[int, int, int, int]]) -> np.ndarray:
    grid = np.zeros((L, L, L, 12), dtype=np.uint8)
    cx, cy, cz = L // 2, L // 2, L // 2
    for (dl, dr, dc, ch) in particle:
        grid[(cx + dl) % L, (cy + dr) % L, (cz + dc) % L, ch] = 1
    return grid


def random_particle(rng: np.random.Generator, n_bits: int, radius: int = 1) -> list[tuple[int, int, int, int]]:
    bits: set[tuple[int, int, int, int]] = set()
    while len(bits) < n_bits:
        dl = int(rng.integers(-radius, radius + 1))
        dr = int(rng.integers(-radius, radius + 1))
        dc = int(rng.integers(-radius, radius + 1))
        ch = int(rng.integers(0, 12))
        bits.add((dl, dr, dc, ch))
    return sorted(bits)


def compute_com_circular(grid: np.ndarray):
    """Circular-mean 3D center of mass and bit count."""
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


def bounding_extent(grid: np.ndarray) -> tuple[int, int, int]:
    """Minimum circular bounding width on each axis."""
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
        best = L
        for shift in range(L):
            rot = (pos - shift) % L
            w = int(rot.max() - rot.min() + 1)
            if w < best:
                best = w
        ext.append(best)
    return tuple(ext)


def simulate_track(grid: np.ndarray, lut: np.ndarray, steps: int = 100) -> dict:
    L = grid.shape[0]
    initial_bits = int(grid.sum())
    state = grid.copy()

    coms: list = []
    bcs: list = []
    extents: list = []

    com, bc = compute_com_circular(state)
    coms.append(com)
    bcs.append(bc)
    extents.append(bounding_extent(state))

    for _ in range(steps):
        state = stream(state)
        state = collide(state, lut)
        com, bc = compute_com_circular(state)
        coms.append(com)
        bcs.append(bc)
        extents.append(bounding_extent(state))

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

    max_ext = max(max(e) for e in extents)
    final_ext = extents[-1]

    return {
        'initial_bits': initial_bits,
        'bcs': bcs,
        'extents': [list(e) for e in extents],
        'cumulative_displacement': cumdisp.tolist(),
        'displacement_norm': float(np.linalg.norm(cumdisp)),
        'bit_stable': all(bc == initial_bits for bc in bcs),
        'final_bits': bcs[-1],
        'max_extent': int(max_ext),
        'final_extent': [int(e) for e in final_ext],
    }


def search(
    num_luts: int = 20,
    num_seeds_per_lut: int = 8,
    steps: int = 100,
    L: int = 16,
    extent_cap: int = 6,
    disp_min: float = 0.5,
    verbose: bool = True,
):
    perms = get_oh_permutations(verbose=verbose)
    action = precompute_perm_action(perms)
    orbits, _ = compute_orbits(action)
    stabs = compute_all_stabilizers(action)

    if verbose:
        size_count = Counter(len(o) for o in orbits)
        weight_count = Counter(hamming(o[0]) for o in orbits)
        weight_size = Counter((hamming(o[0]), len(o)) for o in orbits)
        print(f"[orbits] total {len(orbits)} orbits over 4096 states")
        print(f"[orbits] sizes: {dict(sorted(size_count.items()))}")
        print(f"[orbits] by weight: {dict(sorted(weight_count.items()))}")
        for w in range(13):
            ws = sorted(((sz, count) for (ww, sz), count in weight_size.items() if ww == w))
            if ws:
                print(f"  weight {w:2d}: orbits by size = {ws}")

    results = []
    verified_once = False

    for lut_seed in range(num_luts):
        t_lut = time.time()
        lut = generate_symmetric_lut(seed=lut_seed, perms=perms, action=action, orbits=orbits, stabs=stabs)
        t_lut = time.time() - t_lut

        if not verified_once:
            v = verify_lut(lut, action)
            if verbose:
                print(f"[verify] LUT seed=0: {v}")
            assert v['bijection'] and v['bit_conserving'] and v['symmetric'], \
                f"LUT seed=0 verification failed: {v}"
            verified_once = True

        # Quick uniqueness check: is this the identity?
        ident_frac = float((lut == np.arange(4096, dtype=np.uint16)).mean())

        # Try several seeds
        lut_found = 0
        for sub_seed in range(num_seeds_per_lut):
            rng = np.random.default_rng(lut_seed * 1000 + sub_seed + 1)
            n_bits = int(rng.integers(3, 7))
            particle = random_particle(rng, n_bits=n_bits, radius=1)

            grid = seed_grid(L, particle)
            res = simulate_track(grid, lut, steps=steps)
            res['lut_seed'] = lut_seed
            res['sub_seed'] = sub_seed
            res['particle'] = particle

            if (res['bit_stable']
                    and res['displacement_norm'] >= disp_min
                    and res['max_extent'] <= extent_cap):
                results.append(res)
                lut_found += 1
                if verbose:
                    print(
                        f"  GLIDER lut={lut_seed} sub={sub_seed} bits={res['initial_bits']} "
                        f"disp={res['displacement_norm']:.2f} v={res['cumulative_displacement']} "
                        f"max_ext={res['max_extent']} final_ext={res['final_extent']}"
                    )

        if verbose:
            print(
                f"[lut {lut_seed:02d}] gen={t_lut:.2f}s identity_frac={ident_frac:.3f} "
                f"gliders_found={lut_found}"
            )

    return results, perms, action, orbits, stabs


def main():
    out_dir = SCRIPT_DIR.parent / 'archive' / 'iter_224' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    results, perms, action, orbits, stabs = search(
        num_luts=24,
        num_seeds_per_lut=10,
        steps=100,
        L=16,
        extent_cap=6,
        disp_min=0.5,
        verbose=True,
    )
    dt = time.time() - t0

    print(f"\n[search] runtime {dt:.2f}s, candidates found: {len(results)}")

    results.sort(key=lambda r: r['displacement_norm'], reverse=True)

    top_k = min(10, len(results))
    saved_luts: dict[int, np.ndarray] = {}
    for i, res in enumerate(results[:top_k]):
        seed = res['lut_seed']
        if seed not in saved_luts:
            saved_luts[seed] = generate_symmetric_lut(
                seed=seed, perms=perms, action=action, orbits=orbits, stabs=stabs
            )
        lut = saved_luts[seed]
        out_path = out_dir / f'glider_{i:02d}_lut{seed:02d}_sub{res["sub_seed"]:02d}.json'
        save_dict = {
            'rank': i,
            'lut_seed': seed,
            'sub_seed': res['sub_seed'],
            'particle': [list(p) for p in res['particle']],
            'initial_bits': res['initial_bits'],
            'bit_stable': res['bit_stable'],
            'displacement_norm': res['displacement_norm'],
            'cumulative_displacement': res['cumulative_displacement'],
            'max_extent': res['max_extent'],
            'final_extent': res['final_extent'],
            'final_bits': res['final_bits'],
            'bit_count_history': res['bcs'],
            'extent_history': res['extents'],
            'lut': lut.tolist(),
        }
        with open(out_path, 'w') as f:
            json.dump(save_dict, f, indent=2)
        print(
            f"  [save] rank {i}: disp={res['displacement_norm']:.3f} bits={res['initial_bits']} "
            f"max_ext={res['max_extent']} -> {out_path.name}"
        )

    summary = {
        'num_luts': 24,
        'num_seeds_per_lut': 10,
        'steps': 100,
        'L': 16,
        'extent_cap': 6,
        'disp_min': 0.5,
        'num_candidates': len(results),
        'top_displacements': [r['displacement_norm'] for r in results[:top_k]],
        'top_max_extents': [r['max_extent'] for r in results[:top_k]],
        'top_initial_bits': [r['initial_bits'] for r in results[:top_k]],
        'top_displacement_vectors': [r['cumulative_displacement'] for r in results[:top_k]],
        'runtime_seconds': dt,
    }
    with open(out_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  [save] summary -> {(out_dir / 'summary.json').name}")

    return results


if __name__ == '__main__':
    main()
