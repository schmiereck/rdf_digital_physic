Modify `src/search_mixed_gliders_final.py` to optimize the simulation loop for massive speedups.

In `simulate_seed_fast`, we should do a very fast initial check:
```python
def simulate_seed_fast(seed_cells, lut):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_cells:
        grid[(r + 64) % GRID_SIZE, (c + 64) % GRID_SIZE] = 1

    initial_bits = len(seed_cells)
    
    # 1. Fast check: just step and check bit count
    grids = [grid.copy()]
    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        if int(grid.sum()) != initial_bits:
            return None
        grids.append(grid.copy())
        
    # 2. If it survives, do the heavy computation
    coms = []
    bit_counts = []
    canonical_history = []
    for g in grids:
        com, bits = trigonometric_com_and_bits(g)
        coms.append(com)
        bit_counts.append(bits)
        canonical_history.append(canonical_active_cells(g))
...
```

Write this optimized script to `src/search_mixed_gliders_final.py`, run it, and print its full stdout/stderr. It should run in just a few seconds!