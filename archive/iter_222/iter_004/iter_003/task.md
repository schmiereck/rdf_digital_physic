Update `src/run_evolution_exp_222.py` and the champion characterization to use trigonometric toroidal CoM tracking.

Specifically:
1. Define the perfect trigonometric torus CoM helper in `src/run_evolution_exp_222.py`:
```python
def torus_com(grid: np.ndarray, grid_size: int = GRID_SIZE) -> tuple[float, float]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0)
    twopi = 2.0 * np.pi
    a_r = twopi * rows.astype(float) / grid_size
    com_r = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * grid_size / twopi
    a_c = twopi * cols.astype(float) / grid_size
    com_c = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * grid_size / twopi
    return (float(com_r), float(com_c))
```
2. Replace the old arithmetic mean-based `_com_and_bits` function in `src/run_evolution_exp_222.py` with this trigonometric function.
3. Re-simulate the champion rule from `archive/iter_222/results/champion_rule_perfect.json` using the corrected code, calculate its new artifact-free fitness and per-window velocities. Verify that the velocity in all windows is smooth (around 0.107 cells/step) and the standard deviation is extremely low, leading to a much higher and correct fitness score.
4. Update `archive/iter_222/results/champion_rule_perfect.json` with the new fitness and metrics.
5. Re-generate `archive/iter_222/results/trajectory_analysis.txt` using the perfect unwrapped trajectory, showing the smooth, clean coordinates and per-window velocities.
6. Re-generate the champion animated GIF in `archive/iter_222/results/champion_vc_glider_perfect.gif` (making sure it looks spectacular).