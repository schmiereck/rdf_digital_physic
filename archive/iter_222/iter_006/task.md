Please modify `src/new_fitness.py` to fix the center-of-mass unwrapping loop:
Inside `DisplacementConsistencyFitness.__call__`, replace the loop:
```python
        unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
        for i in range(1, len(sorted_history)):
            prev_com = sorted_history[i - 1]["com"]
            cur_com = sorted_history[i]["com"]
            dx = cur_com[0] - prev_com[0]
            dy = cur_com[1] - prev_com[1]
            if dx > 64:
                dx -= 128.0
            elif dx < -64:
                dx += 128.0
            if dy > 64:
                dy -= 128.0
            elif dy < -64:
                dy += 128.0
            unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))
```
with:
```python
        unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
        for i in range(1, len(sorted_history)):
            prev_com = sorted_history[i - 1]["com"]
            cur_com = sorted_history[i]["com"]
            dx = cur_com[0] - prev_com[0]
            dy = cur_com[1] - prev_com[1]
            if dx > 64:
                dx -= 128.0
            elif dx < -64:
                dx += 128.0
            if dy > 64:
                dy -= 128.0
            elif dy < -64:
                dy += 128.0
            last_unwrapped = unwrapped_coms[-1]
            unwrapped_coms.append((last_unwrapped[0] + dx, last_unwrapped[1] + dy))
```

And modify `src/run_evolution_exp_222.py`:
Replace `_com_and_bits(grid)` with:
```python
def _com_and_bits(grid: np.ndarray) -> tuple[tuple[float, float], int]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    twopi = 2.0 * np.pi
    a_r = twopi * rows.astype(float) / GRID_SIZE
    com_r = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * GRID_SIZE / twopi
    a_c = twopi * cols.astype(float) / GRID_SIZE
    com_c = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * GRID_SIZE / twopi
    return (float(com_r), float(com_c)), int(grid.sum())
```
Ensure you only perform these file changes.