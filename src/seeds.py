"""
seeds.py — Standard initial seeds for CA evolution experiments.
"""

import numpy as np

_GRID = 128


def _make_seed(cells, grid_size=_GRID):
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in cells:
        grid[r % grid_size, c % grid_size] = 1
    return grid


# 3-cell L-tromino centred near the middle of a 128x128 grid
L_TROMINO_SEED = _make_seed([(63, 63), (64, 63), (64, 64)])
