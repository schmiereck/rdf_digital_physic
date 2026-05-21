#!/usr/bin/env python3
"""engine_d4_spacetime.py — 3D+1 Spacetime LGCA on the D4 Lattice.

A Lattice Gas Cellular Automaton in which every cell carries 6 boolean
channels, one per *future-directed light-like* D4 lattice vector under the
[1, 1, 1, 1] time projection (T = (x + y + z + w) / 2 = 1).  In the 3D
spatial hyperplane orthogonal to that time direction, the 6 channel
directions form the vertices of a regular octahedron, so the engine is
naturally equivariant under the full octahedral symmetry group O_h
(48 elements).

The module provides:

    SHIFTS                              – the 6 integer (dx, dy, dz) shifts
    PROJECTED_VECTORS                   – the 6 channels as 3D unit vectors
    OH_GROUP                            – the 48 induced channel permutations
    compute_orbits(), orbit_signature() – orbit decomposition of {0,1}^6
    generate_symmetric_lut(seed)        – random O_h-equivariant bijective LUT
    stream(grid, reverse=False)         – propagation step on the (L,L,L,6) torus
    collide(grid, lut)                  – local pack / lookup / unpack step
    invert_lut(lut)                     – inverse of a permutation LUT
    verify_*                            – diagnostic helpers

Running the file as a script executes a full self-test.
"""

from __future__ import annotations

from itertools import permutations as iperms, product
from typing import Dict, FrozenSet, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# 1. The six D4 channels.
# ---------------------------------------------------------------------------

# Future-directed light-like 4D D4 vectors (T = (x + y + z + w) / 2 = 1).
D4_VECTORS_4D: np.ndarray = np.array(
    [
        [1, 1, 0, 0],  # D0
        [0, 0, 1, 1],  # D1
        [1, 0, 1, 0],  # D2
        [0, 1, 0, 1],  # D3
        [1, 0, 0, 1],  # D4
        [0, 1, 1, 0],  # D5
    ],
    dtype=np.int64,
)

# Spatial shifts on the integer (x, y, z) grid: first three components of
# each 4D vector.  The implicit w-component is determined by w = 2 - x - y - z.
SHIFTS: List[Tuple[int, int, int]] = [
    (1, 1, 0),  # D0
    (0, 0, 1),  # D1
    (1, 0, 1),  # D2
    (0, 1, 0),  # D3
    (1, 0, 0),  # D4
    (0, 1, 1),  # D5
]

NUM_CHANNELS: int = 6
NUM_STATES: int = 1 << NUM_CHANNELS  # 64


# ---------------------------------------------------------------------------
# 2. Orthogonal projection to 3D and the 48-element octahedral group O_h.
# ---------------------------------------------------------------------------

def project_to_3d(v4d: np.ndarray) -> np.ndarray:
    """Orthogonal projection of a 4D D4 vector to the 3D hyperplane
    perpendicular to the time direction (1, 1, 1, 1) / 2.

    The basis (built from D2-, D4- and D0-projected directions) places the 6
    light-like vectors exactly at ±e_x, ±e_y, ±e_z::

        X = (x - y + z - w) / 2     # D2 / D3 axis
        Y = (x - y - z + w) / 2     # D4 / D5 axis
        Z = (x + y - z - w) / 2     # D0 / D1 axis

    Note
    ----
    The task description offers an alternate basis,
    ``X' = (x - y) / √2,  Y' = (z - w) / √2,  Z' = (x + y - z - w) / 2``,
    which projects to the *same* octahedron rotated 45° about the Z axis.
    With that basis only 16 of the 48 standard signed-permutation matrices
    preserve the set; with the basis above all 48 do.  Both choices induce
    isomorphic group actions on the channel indices.
    """
    x, y, z, w = v4d
    return np.array(
        [
            (x - y + z - w) / 2.0,
            (x - y - z + w) / 2.0,
            (x + y - z - w) / 2.0,
        ],
        dtype=np.float64,
    )


PROJECTED_VECTORS: np.ndarray = np.array([project_to_3d(v) for v in D4_VECTORS_4D])
#   D0 → ( 0,  0,  1)    D1 → ( 0,  0, -1)
#   D2 → ( 1,  0,  0)    D3 → (-1,  0,  0)
#   D4 → ( 0,  1,  0)    D5 → ( 0, -1,  0)


def _signed_permutation_matrices() -> List[np.ndarray]:
    """All 48 signed permutation matrices in 3D (6 axis-permutations × 8 sign flips)."""
    mats: List[np.ndarray] = []
    for perm in iperms(range(3)):
        for signs in product((-1, 1), repeat=3):
            M = np.zeros((3, 3), dtype=np.float64)
            for col, row in enumerate(perm):
                M[row, col] = signs[col]
            mats.append(M)
    return mats


def _channel_perm_from_matrix(M: np.ndarray) -> Tuple[int, ...]:
    """Induced permutation of {0,…,5} when M acts on the 6 projected vectors."""
    transformed = PROJECTED_VECTORS @ M.T  # (6, 3); transformed[i] = M · PROJECTED_VECTORS[i]
    induced: List[int] = []
    for tv in transformed:
        d2 = np.sum((PROJECTED_VECTORS - tv) ** 2, axis=1)
        j = int(np.argmin(d2))
        if d2[j] > 1e-9:
            raise ValueError(
                f"Signed permutation does not preserve the channel set: M·v = {tv}"
            )
        induced.append(j)
    return tuple(induced)


def _build_oh_group() -> List[Tuple[int, ...]]:
    perms: List[Tuple[int, ...]] = [
        _channel_perm_from_matrix(M) for M in _signed_permutation_matrices()
    ]
    if len(set(perms)) != 48:
        raise RuntimeError(
            f"Expected 48 unique channel permutations, got {len(set(perms))}"
        )
    return perms


OH_GROUP: List[Tuple[int, ...]] = _build_oh_group()


# ---------------------------------------------------------------------------
# 3. Action on 6-bit packed states and orbit decomposition.
# ---------------------------------------------------------------------------

def apply_channel_perm(perm: Tuple[int, ...], state: int) -> int:
    """Apply a channel permutation to a 6-bit state via pull-back:
    ``new_bit[i] = old_bit[perm[i]]``.

    Since OH_GROUP is closed under inverse, orbits and equivariance properties
    are independent of pull-back vs. push-forward conventions.
    """
    new = 0
    for i in range(NUM_CHANNELS):
        if (state >> perm[i]) & 1:
            new |= 1 << i
    return new


def compute_orbits() -> List[List[int]]:
    """Partition {0,…,63} into orbits under the action of OH_GROUP."""
    seen = [False] * NUM_STATES
    orbits: List[List[int]] = []
    for s in range(NUM_STATES):
        if seen[s]:
            continue
        orb = {apply_channel_perm(g, s) for g in OH_GROUP}
        for x in orb:
            seen[x] = True
        orbits.append(sorted(orb))
    return orbits


def compute_stabilizer(state: int) -> FrozenSet[Tuple[int, ...]]:
    """Subgroup of OH_GROUP that fixes ``state``."""
    return frozenset(g for g in OH_GROUP if apply_channel_perm(g, state) == state)


def orbit_signature(orbit: List[int]) -> Tuple[int, int, FrozenSet[Tuple[int, ...]]]:
    """(Hamming weight, orbit size, stabilizer subgroup of orbit[0])."""
    rep = orbit[0]
    return bin(rep).count("1"), len(orbit), compute_stabilizer(rep)


# ---------------------------------------------------------------------------
# 4. Streaming, collision, packing / unpacking.
# ---------------------------------------------------------------------------

def pack(grid: np.ndarray) -> np.ndarray:
    """Pack a bit grid (..., 6) into an integer grid in 0..63."""
    if grid.ndim < 1 or grid.shape[-1] != NUM_CHANNELS:
        raise ValueError(
            f"grid must have shape (..., {NUM_CHANNELS}); got {grid.shape}"
        )
    out = np.zeros(grid.shape[:-1], dtype=np.uint8)
    for i in range(NUM_CHANNELS):
        out |= (grid[..., i].astype(np.uint8) & 1) << i
    return out


def unpack(packed: np.ndarray) -> np.ndarray:
    """Inverse of :func:`pack`."""
    out = np.zeros(packed.shape + (NUM_CHANNELS,), dtype=np.uint8)
    for i in range(NUM_CHANNELS):
        out[..., i] = ((packed >> i) & 1).astype(np.uint8)
    return out


def stream(grid: np.ndarray, reverse: bool = False) -> np.ndarray:
    """Roll each channel of an (L, L, L, 6) grid by its 3D spatial shift.

    If ``reverse`` is True, roll by the *negated* shift — exactly the inverse
    of the forward operation, so ``stream(stream(g), reverse=True) == g``.
    """
    if grid.ndim != 4 or grid.shape[-1] != NUM_CHANNELS:
        raise ValueError(
            f"grid must have shape (L, L, L, {NUM_CHANNELS}); got {grid.shape}"
        )
    out = np.empty_like(grid)
    sign = -1 if reverse else 1
    for i, (dx, dy, dz) in enumerate(SHIFTS):
        out[..., i] = np.roll(
            grid[..., i],
            shift=(sign * dx, sign * dy, sign * dz),
            axis=(0, 1, 2),
        )
    return out


def collide(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Pack each cell's 6 channels into an integer 0..63, apply the LUT,
    and unpack back to a bit grid."""
    if grid.ndim != 4 or grid.shape[-1] != NUM_CHANNELS:
        raise ValueError(
            f"grid must have shape (L, L, L, {NUM_CHANNELS}); got {grid.shape}"
        )
    if lut.shape != (NUM_STATES,):
        raise ValueError(f"lut must have shape ({NUM_STATES},); got {lut.shape}")
    return unpack(lut[pack(grid)])


def invert_lut(lut: np.ndarray) -> np.ndarray:
    """Inverse of a permutation LUT of size :data:`NUM_STATES`."""
    if lut.shape != (NUM_STATES,):
        raise ValueError(f"lut must have shape ({NUM_STATES},); got {lut.shape}")
    inv = np.empty_like(lut)
    inv[lut.astype(np.int64)] = np.arange(NUM_STATES, dtype=lut.dtype)
    return inv


# ---------------------------------------------------------------------------
# 5. Building a random O_h-equivariant, bit-conserving, bijective LUT.
# ---------------------------------------------------------------------------

def generate_symmetric_lut(seed: int = 0) -> np.ndarray:
    """Random O_h-equivariant, bit-conserving, bijective LUT of size 64.

    Construction
    ------------
    1. Decompose {0,…,63} into orbits under the 48-element O_h channel action.
    2. Compute each orbit's signature ``(weight, |orbit|, stabilizer subgroup
       of orbit[0])`` — orbits sharing a signature can be paired equivariantly.
    3. Within each signature class, draw a random permutation matching each
       source orbit O to a target orbit O'.
    4. For each pairing O → O': pick a representative ``r = O[0]`` and a random
       target ``t ∈ O'`` whose stabilizer contains (and therefore equals)
       Stab(r); then extend equivariantly via ``LUT[g·r] = g·t`` for all
       ``g ∈ OH_GROUP``.

    The resulting map is bijective (orbit sizes preserved by the pairing),
    bit-conserving (orbits live inside a single Hamming-weight class), and
    O_h-equivariant by construction.
    """
    rng = np.random.default_rng(seed)
    orbits = compute_orbits()

    sig_groups: Dict[Tuple[int, int, FrozenSet[Tuple[int, ...]]], List[List[int]]] = {}
    for orb in orbits:
        sig_groups.setdefault(orbit_signature(orb), []).append(orb)

    lut = np.full(NUM_STATES, -1, dtype=np.int16)

    for sig, orbit_list in sig_groups.items():
        n = len(orbit_list)
        order = list(rng.permutation(n))
        for src_idx, tgt_idx in enumerate(order):
            src_orbit = orbit_list[src_idx]
            tgt_orbit = orbit_list[tgt_idx]
            r = src_orbit[0]
            stab_r = compute_stabilizer(r)
            # Candidates: targets fixed by Stab(r). Since orbits in this group
            # share the same stabilizer of orbit[0], the canonical target
            # ``tgt_orbit[0]`` is always a candidate.
            candidates = [
                t
                for t in tgt_orbit
                if all(apply_channel_perm(g, t) == t for g in stab_r)
            ]
            if not candidates:
                raise RuntimeError(
                    f"No equivariant target in orbit starting at {tgt_orbit[0]} "
                    f"for source rep {r}"
                )
            t = int(rng.choice(candidates))
            for g in OH_GROUP:
                lhs = apply_channel_perm(g, r)
                rhs = apply_channel_perm(g, t)
                if lut[lhs] != -1 and lut[lhs] != rhs:
                    raise RuntimeError(
                        f"Equivariance conflict at state {lhs}: "
                        f"existing target {lut[lhs]} vs new target {rhs}"
                    )
                lut[lhs] = rhs

    if (lut == -1).any():
        missing = int((lut == -1).sum())
        raise RuntimeError(f"LUT incomplete: {missing} entries still unset")

    return lut.astype(np.uint8)


# ---------------------------------------------------------------------------
# 6. Verification helpers.
# ---------------------------------------------------------------------------

def verify_lut_bijection(lut: np.ndarray) -> bool:
    """True iff ``lut`` is a permutation of {0,…,63}."""
    return len(set(lut.tolist())) == NUM_STATES


def verify_lut_bit_conservation(lut: np.ndarray) -> bool:
    """True iff every entry preserves Hamming weight."""
    return all(
        bin(int(lut[s])).count("1") == bin(s).count("1") for s in range(NUM_STATES)
    )


def verify_lut_oh_symmetry(lut: np.ndarray) -> bool:
    """True iff ``LUT[g·s] = g·LUT[s]`` for every ``g ∈ OH_GROUP`` and every state ``s``."""
    for g in OH_GROUP:
        for s in range(NUM_STATES):
            gs = apply_channel_perm(g, s)
            if int(lut[gs]) != apply_channel_perm(g, int(lut[s])):
                return False
    return True


def verify_reversibility(grid: np.ndarray, lut: np.ndarray) -> bool:
    """True iff both ``stream`` and ``collide`` can be inverted exactly on ``grid``."""
    streamed = stream(grid)
    if not np.array_equal(grid, stream(streamed, reverse=True)):
        return False
    inv = invert_lut(lut)
    collided = collide(grid, lut)
    return np.array_equal(grid, collide(collided, inv))


def verify_bit_conservation(grid: np.ndarray, lut: np.ndarray) -> bool:
    """True iff stream and collide each preserve the total number of set bits."""
    total = int(grid.sum())
    if int(stream(grid).sum()) != total:
        return False
    return int(collide(grid, lut).sum()) == total


# ---------------------------------------------------------------------------
# 7. Diagnostic driver.
# ---------------------------------------------------------------------------

def _main() -> None:
    print("=" * 72)
    print("engine_d4_spacetime — diagnostic")
    print("=" * 72)

    print("\n[1] D4 channels: 4D vectors, 3D orthogonal projections, spatial shifts")
    for i in range(NUM_CHANNELS):
        v4 = tuple(int(x) for x in D4_VECTORS_4D[i])
        p = PROJECTED_VECTORS[i]
        sh = SHIFTS[i]
        print(
            f"  D{i}: 4D={v4}  proj=({p[0]:+.3f},{p[1]:+.3f},{p[2]:+.3f})  "
            f"shift={sh}"
        )

    print("\n[2] Octahedral group O_h on the 6 channels")
    print(f"  |OH_GROUP| (count of signed perms preserving the set) = {len(OH_GROUP)}")
    print(f"  |unique induced channel perms|                        = {len(set(OH_GROUP))}")
    assert len(set(OH_GROUP)) == 48, "O_h should have 48 elements"

    print("\n[3] Orbit decomposition of {0,1}^6 under O_h")
    orbits = compute_orbits()
    total = sum(len(o) for o in orbits)
    print(f"  # orbits = {len(orbits)};  total states covered = {total} (must be 64)")
    assert total == NUM_STATES

    print("  weight | orbit_size | |stab| | representative (binary) | example states")
    for orb in sorted(orbits, key=lambda o: (bin(o[0]).count("1"), len(o), o[0])):
        w, sz, stab = orbit_signature(orb)
        rep_bin = format(orb[0], "06b")
        sample = orb[: min(4, len(orb))]
        sample_str = ",".join(str(x) for x in sample) + (
            ",…" if len(orb) > 4 else ""
        )
        print(
            f"   {w:>4}  |   {sz:>6}   |   {len(stab):>4}  |          {rep_bin}        | {sample_str}"
        )

    print("\n[4] Symmetric LUTs (5 seeds) and stream/collide self-test on (8,8,8) torus")
    L = 8
    rng_grid = np.random.default_rng(2026)
    grid = rng_grid.integers(0, 2, size=(L, L, L, NUM_CHANNELS), dtype=np.uint8)
    print(f"  grid shape={grid.shape}  initial set bits={int(grid.sum())}")

    overall_ok = True
    for seed in range(5):
        lut = generate_symmetric_lut(seed=seed)
        bij = verify_lut_bijection(lut)
        bcons = verify_lut_bit_conservation(lut)
        symm = verify_lut_oh_symmetry(lut)
        rev = verify_reversibility(grid, lut)
        bitc = verify_bit_conservation(grid, lut)
        identity = bool(np.array_equal(lut, np.arange(NUM_STATES, dtype=np.uint8)))
        print(
            f"  seed={seed}: bij={bij}  bit_cons_LUT={bcons}  O_h_sym={symm}  "
            f"reversible={rev}  bit_cons_grid={bitc}  is_identity={identity}"
        )
        overall_ok &= bij and bcons and symm and rev and bitc

    print("\n[5] Round-trip: 20 forward steps then 20 reverse steps")
    lut = generate_symmetric_lut(seed=42)
    inv = invert_lut(lut)
    initial_bits = int(grid.sum())
    state = grid.copy()
    for _ in range(20):
        state = collide(stream(state), lut)
    forward_bits = int(state.sum())
    for _ in range(20):
        state = stream(collide(state, inv), reverse=True)
    round_trip_ok = bool(np.array_equal(state, grid))
    print(f"  initial bits           = {initial_bits}")
    print(f"  after  20 forward steps = {forward_bits}  (must equal initial)")
    print(f"  round-trip equality     = {round_trip_ok}")
    overall_ok &= round_trip_ok and (forward_bits == initial_bits)

    print("\n[6] Result")
    print(f"  ALL CHECKS PASSED: {overall_ok}")
    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
