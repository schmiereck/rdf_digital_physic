#!/usr/bin/env python3
"""
synchronous_ca_fcc.py -- 3D synchronous Cellular Automaton engine on the FCC lattice.

Step 1 of the pre-registered experiment (src/pre_registration.md).

Architecture:
- FCC lattice with 12 nearest neighbors per site (cuboctahedron vertices).
- Grid: 3D numpy array of shape (L, L, L), dtype uint8 (0 or 1 per cell).
- Toroidal (periodic) boundaries via np.roll.
- Totalistic Birth/Survival (B/S) rule:
    new_cell = 1  if (cell==0 and neighbor_count in B)
                or (cell==1 and neighbor_count in S)
    new_cell = 0  otherwise.
  neighbor_count is the number of live cells among the 12 cuboctahedron
  neighbors (center is NOT counted).
- O_h-equivariant BY CONSTRUCTION because the rule depends only on the count.
"""

from __future__ import annotations
from math import comb
import numpy as np

# The 12 FCC neighbor offsets in (layer, row, col) coordinates.
# These are the same offsets used in src/engine_3d.py (SHIFTS).
FCC_OFFSETS = [
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
    (0, 1, -1),
    (0, -1, 1),
    (1, 1, 1),
    (1, 1, 0),
    (1, 0, 1),
    (-1, -1, -1),
    (-1, -1, 0),
    (-1, 0, -1),
]


def fcc_neighbor_offsets() -> list[tuple[int, int, int]]:
    """Return the 12 nearest-neighbor offsets for the FCC lattice."""
    return FCC_OFFSETS.copy()


def step_ca(grid: np.ndarray, B: set, S: set) -> np.ndarray:
    """Perform one synchronous CA update step on the FCC lattice.

    Parameters
    ----------
    grid : ndarray of shape (L, L, L), dtype uint8
        Current cell states (0 or 1).
    B : set of int
        Birth counts (subset of {0,...,12}). A dead cell becomes alive if its
        number of live neighbors is in B.
    S : set of int
        Survival counts (subset of {0,...,12}). A live cell stays alive if its
        number of live neighbors is in S.

    Returns
    -------
    ndarray of shape (L, L, L), dtype uint8
        Updated cell states.
    """
    assert grid.ndim == 3, f"grid must be 3-D, got shape {grid.shape}"
    assert grid.dtype == np.uint8, f"grid dtype must be uint8, got {grid.dtype}"

    # Vectorized neighbor counting: sum of 12 toroidally-shifted grids.
    count = np.zeros_like(grid, dtype=np.uint8)
    for dl, dr, dc in FCC_OFFSETS:
        count += np.roll(grid, shift=(dl, dr, dc), axis=(0, 1, 2))

    # Build lookup tables for membership in B and S (counts 0..12).
    birth_lut = np.zeros(13, dtype=bool)
    survive_lut = np.zeros(13, dtype=bool)
    for k in B:
        if 0 <= k <= 12:
            birth_lut[k] = True
    for k in S:
        if 0 <= k <= 12:
            survive_lut[k] = True

    birth = (grid == 0) & birth_lut[count]
    survive = (grid == 1) & survive_lut[count]
    return (birth | survive).astype(np.uint8)


def trig_com(grid: np.ndarray, L: int) -> tuple[float, float, float]:
    """Compute center-of-mass on a torus using the trigonometric method.

    Treats each dimension independently using circular means (arctan2).
    """
    l_idx, r_idx, c_idx = np.where(grid > 0)
    if len(l_idx) == 0:
        return (0.0, 0.0, 0.0)

    twopi = 2.0 * np.pi
    result = np.zeros(3)
    for a, coords in enumerate([l_idx, r_idx, c_idx]):
        theta = twopi * coords.astype(float) / L
        x = np.cos(theta).sum()
        y = np.sin(theta).sum()
        result[a] = (L * np.arctan2(y, x) / twopi) % L

    return (float(result[0]), float(result[1]), float(result[2]))


def unwrap_com(
    prev: tuple[float, float, float],
    raw: tuple[float, float, float],
    L: int,
) -> tuple[float, float, float]:
    """Unwrap a raw toroidal COM to avoid jump discontinuities.

    Compares ``raw`` to ``prev`` and shifts by +/-L where the difference
    exceeds L/2, then returns the adjusted absolute coordinate.
    """
    half = L / 2.0
    prev_arr = np.asarray(prev, dtype=float)
    raw_arr = np.asarray(raw, dtype=float)
    delta = raw_arr - prev_arr

    for i in range(3):
        if delta[i] > half:
            delta[i] -= L
        elif delta[i] < -half:
            delta[i] += L

    return tuple(float(v) for v in (prev_arr + delta))


def _dim_extent(coords: np.ndarray, L: int) -> int:
    """Minimum circular extent of integer coordinates on a 1-D ring of length L."""
    if len(coords) == 0:
        return 0
    s = np.sort(np.unique(coords))
    if len(s) == 1:
        return 1
    gaps = np.diff(s)
    wrap_gap = s[0] + L - s[-1]
    all_gaps = np.concatenate([gaps, [wrap_gap]])
    max_gap = int(np.max(all_gaps))
    return L - max_gap + 1


def bounding_extent(grid: np.ndarray, L: int) -> int:
    """Bounding box size = max over dimensions of the minimum-wrapped extent.

    For each dimension we compute the shortest arc on the torus that contains
    all occupied cells, then return the largest of the three side lengths.
    """
    l_idx, r_idx, c_idx = np.where(grid > 0)
    if len(l_idx) == 0:
        return 0
    ext_l = _dim_extent(l_idx, L)
    ext_r = _dim_extent(r_idx, L)
    ext_c = _dim_extent(c_idx, L)
    return int(max(ext_l, ext_r, ext_c))


def format_rule(B: set, S: set) -> str:
    """Format a totalistic rule as a conventional B{...}/S{...} string."""
    b_str = "".join(str(k) for k in sorted(B))
    s_str = "".join(str(k) for k in sorted(S))
    return f"B{b_str}/S{s_str}"


def lambda_param(B: set, S: set) -> float:
    """Compute Langton's lambda for the 13-neighbor FCC CA.

    The total number of neighbourhood configurations is 2**13 = 8192
    (centre cell x 12 neighbours).  For a totalistic rule, the fraction of
    configurations that map to the live state is:

        lambda = ( sum_{k in B} C(12,k)  +  sum_{k in S} C(12,k) ) / 8192
    """
    numerator = sum(comb(12, k) for k in B) + sum(comb(12, k) for k in S)
    return numerator / 8192.0


def simulate(
    grid: np.ndarray,
    B: set,
    S: set,
    steps: int,
    snapshot_interval: int | None = None,
) -> dict:
    """Run a synchronous CA simulation and record diagnostics.

    Parameters
    ----------
    grid : ndarray (L, L, L), uint8
        Initial state.
    B, S : sets of int
        Birth / Survival neighbour counts.
    steps : int
        Number of update steps to run.
    snapshot_interval : int or None
        Save grid state every N steps.  Defaults to max(1, steps // 20).

    Returns
    -------
    dict with keys:
        bit_counts       : list[int]      -- live cells at each step (0..steps)
        coms             : list[tuple]    -- unwrapped trigonometric COM
        extents          : list[int]      -- bounding box size at each step
        survival_time    : int            -- first step with 0 bits, or steps
        net_displacement : tuple[floatx3] -- final - initial unwrapped COM
        snapshots        : dict{int: ndarray} -- saved grids at intervals
        final_grid       : ndarray        -- state after the last step
    """
    if snapshot_interval is None:
        snapshot_interval = max(1, steps // 20)

    L = grid.shape[0]
    assert grid.shape == (L, L, L), f"grid must be cubic, got {grid.shape}"

    bit_counts = [int(grid.sum())]
    raw_com0 = trig_com(grid, L)
    coms = [raw_com0]
    extents = [bounding_extent(grid, L)]
    snapshots = {0: grid.copy()}

    g = grid
    survival_time = steps
    for step in range(1, steps + 1):
        g = step_ca(g, B, S)
        bc = int(g.sum())
        bit_counts.append(bc)

        if bc == 0:
            coms.append(coms[-1])
            extents.append(0)
            survival_time = step
            # Pad remaining entries for uniform list length
            for _ in range(step + 1, steps + 1):
                bit_counts.append(0)
                coms.append(coms[-1])
                extents.append(0)
            break
        else:
            raw_com = trig_com(g, L)
            unwrapped = unwrap_com(coms[-1], raw_com, L)
            coms.append(unwrapped)
            extents.append(bounding_extent(g, L))

        if step % snapshot_interval == 0:
            snapshots[step] = g.copy()

    net_displacement = tuple(
        coms[-1][i] - coms[0][i] for i in range(3)
    )

    return {
        "bit_counts": bit_counts,
        "coms": coms,
        "extents": extents,
        "survival_time": survival_time,
        "net_displacement": net_displacement,
        "snapshots": snapshots,
        "final_grid": g.copy(),
    }


def validate_engine() -> bool:
    """Run positive-control sanity checks and print PASS/FAIL for each."""
    L = 16
    c = L // 2
    all_pass = True

    # ------------------------------------------------------------------
    # 1. All-die rule
    # ------------------------------------------------------------------
    print("=" * 70)
    print("VALIDATION TESTS")
    print("=" * 70)

    B = frozenset()
    S = frozenset()
    grid = np.zeros((L, L, L), dtype=np.uint8)
    grid[c, c, c] = 1
    new_grid = step_ca(grid, B, S)
    bc = int(new_grid.sum())
    ok = bc == 0
    print(f"[1] All-die  ({format_rule(B,S)}):  single bit -> bc={bc}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    # ------------------------------------------------------------------
    # 2. All-live rule
    # ------------------------------------------------------------------
    B = frozenset(range(13))
    S = frozenset(range(13))
    grid = np.zeros((L, L, L), dtype=np.uint8)
    grid[c, c, c] = 1
    new_grid = step_ca(grid, B, S)
    bc = int(new_grid.sum())
    ok = bc > 1
    print(f"[2] All-live ({format_rule(B,S)}):  single bit -> bc={bc}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    # ------------------------------------------------------------------
    # 3. Still-life rule  (B={}, S={12})
    # ------------------------------------------------------------------
    B = frozenset()
    S = frozenset({12})

    # 3a -- isolated bit should die immediately
    grid = np.zeros((L, L, L), dtype=np.uint8)
    grid[c, c, c] = 1
    new_grid = step_ca(grid, B, S)
    bc = int(new_grid.sum())
    ok = bc == 0
    print(f"[3a] Still-life single bit ({format_rule(B,S)}): bc={bc}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    # 3b -- centre cell surrounded by all 12 neighbours: centre has count 12,
    #       therefore survives at least one step.  (The 12 edge cells each
    #       have fewer than 12 neighbours and die, so total drops toward 1.)
    grid = np.zeros((L, L, L), dtype=np.uint8)
    grid[c, c, c] = 1
    for dl, dr, dc in FCC_OFFSETS:
        grid[(c + dl) % L, (c + dr) % L, (c + dc) % L] = 1
    new_grid = step_ca(grid, B, S)
    bc = int(new_grid.sum())
    ok = bc > 0  # at least the centre survives
    print(f"[3b] Still-life 13-block ({format_rule(B,S)}): bc={bc}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    # ------------------------------------------------------------------
    # 4. Cooperative survival rule  (B={3}, S={2,3})
    # ------------------------------------------------------------------
    B = frozenset({3})
    S = frozenset({2, 3})

    # 4a -- isolated bit dies (0 neighbours -> not in S)
    grid = np.zeros((L, L, L), dtype=np.uint8)
    grid[c, c, c] = 1
    new_grid = step_ca(grid, B, S)
    bc = int(new_grid.sum())
    ok = bc == 0
    print(f"[4a] Cooperative 1-bit ({format_rule(B,S)}): bc={bc}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    # 4b -- 3 mutually adjacent bits form a triangle: each has exactly 2
    #       neighbours, so all survive (cooperative survival).
    grid = np.zeros((L, L, L), dtype=np.uint8)
    grid[c, c, c] = 1          # origin
    grid[c, c + 1, c] = 1      # offset (0, 1, 0)
    grid[c, c, c + 1] = 1      # offset (0, 0, 1)
    result = simulate(grid, B, S, steps=5)
    step1_bc = result["bit_counts"][1]
    # All three survive because each sees 2 neighbours.
    ok = step1_bc >= 3
    changed = any(b != result["bit_counts"][0] for b in result["bit_counts"][1:])
    print(f"[4b] Cooperative 3-bit triangle ({format_rule(B,S)}): "
          f"step1_bc={step1_bc}, dynamics={changed}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    print("=" * 70)
    print(f"OVERALL: {'ALL PASSED' if all_pass else 'SOME TESTS FAILED'}")
    print("=" * 70)
    return all_pass


def _performance_benchmark():
    """Quick internal benchmark: 40 cubed grid x 500 steps."""
    import time
    L = 40
    steps = 500
    np.random.seed(0)
    grid = (np.random.rand(L, L, L) < 0.05).astype(np.uint8)
    B = frozenset({3, 4})
    S = frozenset({2, 3})

    t0 = time.time()
    result = simulate(grid, B, S, steps=steps)
    elapsed = time.time() - t0
    print(f"\nPerformance: {steps} steps on {L}^3 grid in {elapsed:.3f}s")
    print(f"  Initial bits: {result['bit_counts'][0]}")
    print(f"  Final bits:   {result['bit_counts'][-1]}")
    print(f"  Survival:     {result['survival_time']} steps")
    print(f"  Target:       < 120 s")
    print(f"  Target met:   {'YES' if elapsed < 120 else 'NO'}")
    return elapsed < 120


if __name__ == "__main__":
    ok = validate_engine()
    perf_ok = _performance_benchmark()
    if not ok or not perf_ok:
        raise SystemExit(1)
