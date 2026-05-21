Rewrite `src/engine_d4_dynamic.py` to support both 6-channel and 12-channel modes dynamically.
The code for `src/engine_d4_dynamic.py` should be:
```python
#!/usr/bin/env python3
"""engine_d4_dynamic.py — 3D+1 Spacetime LGCA with Fully Dynamic Local Latching/Trapping.

In this engine, there is no permanent static mass. Spacetime coordinate latency (latching)
is driven purely by the moving bits themselves, reflecting a dynamic gravity-like spacetime
deformation. Supports both 6-channel D4 Spacetime and 12-channel FCC space.
"""

from __future__ import annotations

import os
import sys
import numpy as np
from typing import Dict, Any, List, Tuple

# Adjust sys.path to ensure we can import engine_d4_spacetime and engine_3d
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class DynamicLatchingEngine:
    """Manages a 3D toroidal LGCA with dynamic local latching (trapping) driven by moving bits.
    Supports either 6-channel D4 Spacetime LGCA or 12-channel FCC space LGCA.
    """

    def __init__(
        self,
        L: int,
        alpha: float,
        threshold: float,
        exponent: float = 1.0,
        lut_seed: int = 1,
        use_12_channels: bool = True,
    ):
        self.L = L
        self.alpha = alpha
        self.threshold = threshold
        self.exponent = exponent
        self.lut_seed = lut_seed
        self.use_12_channels = use_12_channels
        self.C = 12 if use_12_channels else 6

        # Initialize grids (L, L, L, C)
        self.temporal_grid = np.zeros((L, L, L, self.C), dtype=np.uint8)
        self.latched_grid = np.zeros((L, L, L, self.C), dtype=np.uint8)
        self.timers = np.zeros((L, L, L, self.C), dtype=np.int32)

        # Import and generate LUT dynamically
        if self.use_12_channels:
            try:
                from src.search_3d_gliders import generate_symmetric_lut as generate_lut_12
                from src.engine_3d import collide as collide_12, stream as stream_12
            except ModuleNotFoundError:
                from search_3d_gliders import generate_symmetric_lut as generate_lut_12
                from engine_3d import collide as collide_12, stream as stream_12
            self.lut = generate_lut_12(seed=self.lut_seed)
            self._collide = collide_12
            self._stream = stream_12
        else:
            try:
                from src.engine_d4_spacetime import generate_symmetric_lut as generate_lut_6, collide as collide_6, stream as stream_6
            except ModuleNotFoundError:
                from engine_d4_spacetime import generate_symmetric_lut as generate_lut_6, collide as collide_6, stream as stream_6
            self.lut = generate_lut_6(seed=self.lut_seed)
            self._collide = collide_6
            self._stream = stream_6

    def compute_local_density(self) -> np.ndarray:
        """Compute the smoothed local mass density M for each cell.

        M(x, y, z) is the sum of bits (temporal + latched) in each cell,
        smoothed by summing with its 6 nearest spatial neighbors (using periodic roll).
        """
        # Sum of bits in each cell
        cell_m = (
            self.temporal_grid.sum(axis=-1).astype(np.float64)
            + self.latched_grid.sum(axis=-1).astype(np.float64)
        )

        # Smooth with its 6 nearest spatial neighbors (using periodic roll)
        smoothed = cell_m.copy()
        for dx, dy, dz in [
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ]:
            smoothed += np.roll(cell_m, shift=(dx, dy, dz), axis=(0, 1, 2))
        return smoothed

    def step(self) -> None:
        """Executes a single step of the fully dynamic latching Spacetime LGCA:
        a. Timer decrement and release: release expired latched bits back to `temporal_grid`
           if the target temporal channel is empty. If blocked, keep the timer at 1.
        b. Compute updated local density field M.
        c. Trapping: for any cell with M >= threshold, trap incoming temporal bits (except
           those just released in this step) into the `latched_grid`, setting their timers to
           `round(alpha * (M ** exponent))` (ensure at least 1 step duration). If the target
           latched channel is occupied, trapping is blocked.
        d. Collision: apply the Oh symmetric LUT on remaining temporal bits.
        e. Stream: stream temporal bits.
        """
        # a. Timer decrement and release
        want_to_release = (self.latched_grid == 1) & (self.timers == 1)
        released_mask = want_to_release & (self.temporal_grid == 0)
        blocked_mask = want_to_release & (self.temporal_grid == 1)

        # Decrement active timers
        active_mask = (self.latched_grid == 1) & (~blocked_mask)
        self.timers[active_mask] -= 1

        # Move released bits
        self.temporal_grid[released_mask] = 1
        self.latched_grid[released_mask] = 0
        self.timers[released_mask] = 0

        # b. Compute updated local density field M
        M = self.compute_local_density()

        # c. Trapping
        trap_condition = M >= self.threshold
        trap_mask = (
            trap_condition[..., np.newaxis]
            & (self.temporal_grid == 1)
            & (~released_mask)
            & (self.latched_grid == 0)
        )

        # Compute duration for each cell (ensure at least 1 step duration)
        duration = np.round(self.alpha * (M**self.exponent)).astype(np.int32)
        duration = np.maximum(duration, 1)
        duration_4d = np.repeat(duration[..., np.newaxis], self.C, axis=-1)

        # Move trapped bits
        self.temporal_grid[trap_mask] = 0
        self.latched_grid[trap_mask] = 1
        self.timers[trap_mask] = duration_4d[trap_mask]

        # d. Collision
        self.temporal_grid = self._collide(self.temporal_grid, self.lut)

        # e. Stream
        self.temporal_grid = self._stream(self.temporal_grid)
```
After writing this file, execute `python src/execute_attraction.py` to re-run the simulation.