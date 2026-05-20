The goal of this sub-task is to resolve the toroidal CoM wrapping artifacts and calculate the correct, high fitness score for the discovered v<c glider.

Please perform the following actions:

1. Modify `src/new_fitness.py`:
Inside `DisplacementConsistencyFitness.__call__`, fix the center-of-mass unwrapping loop. It should accumulate the unwrapped position relative to the last accumulated unwrapped position (`unwrapped_coms[-1]`) instead of relative to raw `prev_com`.
Here is the correct code:
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

2. Modify `src/run_evolution_exp_222.py`:
Update the `_com_and_bits` function to use trigonometric toroidal center-of-mass calculations, which are mathematically rigorous and immune to periodic boundary crossings:
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

3. Create and run a Python script `src/recharacterize_champion.py` which:
  - Loads the champion rule from `archive/iter_222/results/champion_rule_perfect.json`.
  - Runs a 500-step simulation starting from the 3-bit L-tromino seed using the corrected `_com_and_bits` function.
  - Re-evaluates this trajectory with the fixed `DisplacementConsistencyFitness` (with `num_windows=5`, `max_bit_threshold=12`, `max_velocity_threshold=0.9`, `min_velocity=0.05`).
  - Prints the recalculated fitness, mean speed, and the per-window velocity magnitudes. Verify that the velocities are smooth and standard deviation is very low, yielding a much higher, artifact-free fitness.
  - Updates the `fitness` field and other metadata inside `archive/iter_222/results/champion_rule_perfect.json` with the new values.
  - Re-writes `archive/iter_222/results/trajectory_analysis.txt` with the clean, smooth coordinates and correct per-window velocities.
  - Re-generates the animated GIF `archive/iter_222/results/champion_vc_glider_perfect.gif` using matplotlib.

Verify that the script runs successfully and completes all tasks.