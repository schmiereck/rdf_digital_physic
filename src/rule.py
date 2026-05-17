#!/usr/bin/env python3
"""
rule.py — Thin wrapper around a cellular automaton rule dict.

The Rule wraps a packed-neighbourhood → packed-neighbourhood integer map and
exposes the LUT used by the engine to step the grid.  ``bits_per_cell`` defaults
to 1 so that the existing 1-bit pipeline (LUT length 128, key range 0..127)
continues to work unchanged.  Passing a larger ``bits_per_cell`` enables N-bit
cells, in which case the LUT has length ``2**(7*bits_per_cell)``.
"""

from __future__ import annotations

import numpy as np

from engine import BITS_PER_CELL, build_lut


class Rule:
    """Wraps an integer→integer rule mapping for the hexagonal CA."""

    def __init__(
        self,
        rule_dict: dict,
        bits_per_cell: int | None = None,
    ):
        if bits_per_cell is None:
            bits_per_cell = BITS_PER_CELL
        self.bits_per_cell = int(bits_per_cell)
        self.rule_dict = {int(k): int(v) for k, v in rule_dict.items()}
        self._lut: np.ndarray | None = None

    # ── LUT ────────────────────────────────────────────────────────────────
    @property
    def lut(self) -> np.ndarray:
        """Return (and cache) the length-2**(7N) cell-output LUT."""
        if self._lut is None:
            self._lut = build_lut(self.rule_dict, self.bits_per_cell)
        return self._lut

    # ── Neighbourhood key helpers ──────────────────────────────────────────
    def neighborhood_key(
        self,
        center,
        e,
        se,
        sw,
        w,
        nw,
        ne,
    ) -> int:
        """Pack a 7-cell neighbourhood into the rule's lookup key.

        Each argument may be either an integer cell value (0..2**N - 1) or an
        iterable of N bits (MSB first, matching engine.HexagonalGrid encoding).
        """
        n = self.bits_per_cell
        cells = [center, e, se, sw, w, nw, ne]
        ints = []
        for c in cells:
            if hasattr(c, "__iter__") and not isinstance(c, (int, np.integer)):
                bits = list(c)
                if len(bits) != n:
                    raise ValueError(
                        f"expected {n} bits per cell, got {len(bits)}: {bits}"
                    )
                v = 0
                for b in bits:
                    v = (v << 1) | (int(b) & 1)
                ints.append(v)
            else:
                ints.append(int(c))
        shifts = [6 * n, 5 * n, 4 * n, 3 * n, 2 * n, n, 0]
        key = 0
        for v, s in zip(ints, shifts):
            key |= v << s
        return key

    # ── Convenience ────────────────────────────────────────────────────────
    def lookup(
        self,
        center,
        e,
        se,
        sw,
        w,
        nw,
        ne,
    ) -> int:
        """Return the new centre cell value for the given neighbourhood."""
        return int(self.lut[self.neighborhood_key(center, e, se, sw, w, nw, ne)])
