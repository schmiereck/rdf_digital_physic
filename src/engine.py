#!/usr/bin/env python3
"""
engine.py — Multi-bit hexagonal CA engine.

Generalises the historic 1-bit step (encoded by simulator.py and evolution.py)
to grids whose cells carry N bits.  The grid is represented as a NumPy array of
shape ``(height, width, bits_per_cell)`` where each entry along the last axis
is a single bit (0/1).  Cell value = base-2 with index 0 as the most
significant bit.

For ``bits_per_cell == 1`` the math reduces exactly to the legacy fast path:
state encoding ``(c<<6)|(e<<5)|(se<<4)|(sw<<3)|(w<<2)|(nw<<1)|ne`` and a
length-128 LUT whose output is the new centre bit.

For ``bits_per_cell == N`` the state is a 7*N-bit integer packed
``(c<<6N)|(e<<5N)|(se<<4N)|(sw<<3N)|(w<<2N)|(nw<<N)|ne`` and the LUT (length
2**(7N)) outputs the new centre cell value (0..2**N - 1).
"""

from __future__ import annotations

import numpy as np

# Global default — callers may override per-instance via the ``bits_per_cell``
# argument of HexagonalGrid / Rule / fitness classes.  Kept at 1 so the existing
# pipeline behaves exactly as before unless deliberately bumped.
BITS_PER_CELL = 1

# Same hex direction list used elsewhere in the project (axial coordinates).
HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


# ── dtype helpers ─────────────────────────────────────────────────────────────

def _state_dtype(bits_per_cell: int) -> np.dtype:
    """Return an unsigned dtype wide enough for a 7*bits_per_cell-bit index."""
    width = 7 * int(bits_per_cell)
    if width <= 8:
        return np.uint8
    if width <= 16:
        return np.uint16
    if width <= 32:
        return np.uint32
    return np.uint64


def _cell_dtype(bits_per_cell: int) -> np.dtype:
    """Return an unsigned dtype wide enough for a single cell value."""
    n = int(bits_per_cell)
    if n <= 8:
        return np.uint8
    if n <= 16:
        return np.uint16
    return np.uint32


# ── LUT construction ──────────────────────────────────────────────────────────

def build_lut(rule_dict: dict, bits_per_cell: int = 1) -> np.ndarray:
    """Build the cell-output LUT for a rule dict.

    ``rule_dict`` maps a packed neighbourhood index → packed output
    neighbourhood (both 7*N-bit integers).  Only the top N bits of the output
    (the new centre cell) are kept in the returned LUT.

    Identity baseline: ``output[k] = k`` so the new centre equals the old
    centre when the rule has no entry for that neighbourhood.
    """
    n = int(bits_per_cell)
    if n < 1:
        raise ValueError(f"bits_per_cell must be >= 1 (got {n})")
    lut_size = 1 << (7 * n)
    full = np.arange(lut_size, dtype=_state_dtype(n))
    for k, v in rule_dict.items():
        ki = int(k)
        if not (0 <= ki < lut_size):
            raise ValueError(
                f"rule key {ki} out of range for bits_per_cell={n} "
                f"(allowed 0..{lut_size - 1})"
            )
        full[ki] = int(v)
    center_shift = 6 * n
    center_mask = (1 << n) - 1
    return ((full >> center_shift) & center_mask).astype(_cell_dtype(n))


# ── Stepping ──────────────────────────────────────────────────────────────────

def _pack_cell_values(grid: np.ndarray, bits_per_cell: int) -> np.ndarray:
    """Collapse a (H, W, N) bit-grid to (H, W) per-cell integer values."""
    n = int(bits_per_cell)
    if grid.ndim == 2:
        # Treat a 2D grid as a 1-bit grid for convenience.
        assert n == 1, "2D grid input requires bits_per_cell=1"
        return grid.astype(_state_dtype(1))
    assert grid.ndim == 3 and grid.shape[-1] == n, (
        f"grid shape {grid.shape} incompatible with bits_per_cell={n}"
    )
    if n == 1:
        return grid[:, :, 0].astype(_state_dtype(1))
    weights = (1 << np.arange(n - 1, -1, -1)).astype(_state_dtype(n))
    return (grid.astype(_state_dtype(n)) * weights).sum(axis=-1)


def _unpack_cell_values(cell_vals: np.ndarray, bits_per_cell: int) -> np.ndarray:
    """Expand a (H, W) per-cell integer array back to a (H, W, N) bit-grid."""
    n = int(bits_per_cell)
    h, w = cell_vals.shape
    if n == 1:
        return cell_vals.reshape(h, w, 1).astype(np.uint8)
    out = np.zeros((h, w, n), dtype=np.uint8)
    for i in range(n):
        out[:, :, i] = ((cell_vals >> (n - 1 - i)) & 1).astype(np.uint8)
    return out


def step_grid(
    grid: np.ndarray,
    lut: np.ndarray,
    bits_per_cell: int = 1,
) -> np.ndarray:
    """Advance one CA step.

    Accepts either a 3D ``(H, W, N)`` bit-grid or, for ``N == 1``, a 2D
    ``(H, W)`` grid for backward compatibility.  Always returns a 3D
    ``(H, W, N)`` array.
    """
    n = int(bits_per_cell)
    cell = _pack_cell_values(grid, n)
    e = np.roll(cell, -1, axis=0)
    w = np.roll(cell, 1, axis=0)
    ne = np.roll(cell, -1, axis=1)
    sw = np.roll(cell, 1, axis=1)
    se = np.roll(e, 1, axis=1)
    nw = np.roll(w, -1, axis=1)

    if n == 1:
        # Legacy fast path — produces uint8 indices identical to evolution.step_grid.
        state = (
            (cell.astype(np.uint16) << 6)
            | (e.astype(np.uint16) << 5)
            | (se.astype(np.uint16) << 4)
            | (sw.astype(np.uint16) << 3)
            | (w.astype(np.uint16) << 2)
            | (nw.astype(np.uint16) << 1)
            | ne.astype(np.uint16)
        ).astype(np.uint8)
    else:
        dt = _state_dtype(n)
        state = (
            (cell.astype(dt) << (6 * n))
            | (e.astype(dt) << (5 * n))
            | (se.astype(dt) << (4 * n))
            | (sw.astype(dt) << (3 * n))
            | (w.astype(dt) << (2 * n))
            | (nw.astype(dt) << n)
            | ne.astype(dt)
        )
    new_cell = lut[state]
    return _unpack_cell_values(new_cell, n)


def step_grid_2d(grid_2d: np.ndarray, lut_1bit: np.ndarray) -> np.ndarray:
    """Backward-compatible 2D variant — kept so that existing 1-bit callers
    that prefer a flat 2D output can use the engine directly.
    """
    out_3d = step_grid(grid_2d, lut_1bit, bits_per_cell=1)
    return out_3d[:, :, 0]


# ── Grid-level helpers ────────────────────────────────────────────────────────

def bit_count(grid: np.ndarray) -> int:
    """Total number of set bits across all cells and bit-slots."""
    return int(grid.sum())


def occupancy_mask(grid: np.ndarray) -> np.ndarray:
    """Boolean-ish (uint8) mask of cells whose value is non-zero."""
    if grid.ndim == 2:
        return (grid > 0).astype(np.uint8)
    return (grid.sum(axis=-1) > 0).astype(np.uint8)


def center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    """Centre of mass of all occupied cells (any bit set)."""
    mask = occupancy_mask(grid)
    rs, cs = np.where(mask > 0)
    if len(rs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(rs)), float(np.mean(cs)))


# ── HexagonalGrid container ───────────────────────────────────────────────────

class HexagonalGrid:
    """Multi-bit hexagonal grid of shape ``(height, width, bits_per_cell)``.

    Provides the small API the rest of the codebase needs: ``bit_count``,
    ``center_of_mass``, ``step(lut)``, ``copy()`` and bit/cell-level setters.
    The underlying NumPy array is exposed as ``.data``.
    """

    def __init__(
        self,
        height: int,
        width: int,
        bits_per_cell: int | None = None,
    ):
        if bits_per_cell is None:
            bits_per_cell = BITS_PER_CELL
        self.bits_per_cell = int(bits_per_cell)
        self.data = np.zeros(
            (int(height), int(width), self.bits_per_cell),
            dtype=np.uint8,
        )

    # construction helpers -----------------------------------------------------

    @classmethod
    def from_2d(
        cls,
        grid_2d: np.ndarray,
        bits_per_cell: int | None = None,
    ) -> "HexagonalGrid":
        """Wrap a 2D occupancy grid.  Non-zero entries set the LSB of each
        target cell (i.e. cell value = 1) — for ``bits_per_cell == 1`` this
        is identical to the original 1-bit semantics.
        """
        if bits_per_cell is None:
            bits_per_cell = BITS_PER_CELL
        h, w = grid_2d.shape
        hg = cls(h, w, bits_per_cell)
        # LSB slot = index N-1 (since slot 0 is MSB in our encoding).
        hg.data[:, :, -1] = (grid_2d != 0).astype(np.uint8)
        return hg

    @classmethod
    def from_3d(cls, data: np.ndarray) -> "HexagonalGrid":
        assert data.ndim == 3, "from_3d requires (H, W, bits_per_cell) array"
        h, w, n = data.shape
        hg = cls(h, w, n)
        hg.data = data.astype(np.uint8).copy()
        return hg

    # accessors ---------------------------------------------------------------

    @property
    def shape(self) -> tuple:
        return self.data.shape

    @property
    def height(self) -> int:
        return int(self.data.shape[0])

    @property
    def width(self) -> int:
        return int(self.data.shape[1])

    @property
    def bit_count(self) -> int:
        return int(self.data.sum())

    def occupancy_mask(self) -> np.ndarray:
        return occupancy_mask(self.data)

    def cell_values(self) -> np.ndarray:
        """(H, W) integer array of per-cell decoded values."""
        return _pack_cell_values(self.data, self.bits_per_cell)

    def center_of_mass(self) -> tuple[float, float]:
        return center_of_mass(self.data)

    def copy(self) -> "HexagonalGrid":
        new = HexagonalGrid(self.height, self.width, self.bits_per_cell)
        new.data = self.data.copy()
        return new

    # mutation ----------------------------------------------------------------

    def set_cell(self, r: int, c: int, value: int) -> None:
        """Set cell (r, c) to integer ``value`` (0..2**bits_per_cell - 1)."""
        v = int(value)
        max_v = (1 << self.bits_per_cell) - 1
        if not (0 <= v <= max_v):
            raise ValueError(
                f"value {v} out of range for bits_per_cell={self.bits_per_cell}"
            )
        for i in range(self.bits_per_cell):
            self.data[r, c, i] = (v >> (self.bits_per_cell - 1 - i)) & 1

    # stepping ----------------------------------------------------------------

    def step(self, lut: np.ndarray) -> None:
        self.data = step_grid(self.data, lut, self.bits_per_cell)
