Write and run a python script `src/probe_gliders_223.py` to test different 3-bit and 4-bit contiguous seeds under:
1. The sub-light speed glider rule from `archive/iter_222/results/champion_rule_perfect.json` (uses DisplacementConsistencyFitness).
2. The elastic collision rule from `archive/iter_193/iter_002/results/champion_rule.json` (uses RecessionBiasedFitness).

For each rule:
- Generate all 3-bit and 4-bit contiguous seeds under translation-only canonical form (which naturally includes all rotations, reflections, and orientations of every shape).
- Place each seed near the center of a 128x128 grid (using (row + 64) % 128, (col + 64) % 128) and simulate it for 200 steps.
- Track step-by-step active cell counts and COMs. Use trigonometric toroidal CoM for COM calculations:
  ```python
  def trigonometric_com_and_bits(grid: np.ndarray) -> tuple[tuple[float, float], int]:
      rows, cols = np.where(grid > 0)
      if len(rows) == 0:
          return (0.0, 0.0), 0
      grid_size = 128
      twopi = 2.0 * np.pi
      a_r = twopi * rows.astype(float) / grid_size
      com_r = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * grid_size / twopi
      a_c = twopi * cols.astype(float) / grid_size
      com_c = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * grid_size / twopi
      return (float(com_r), float(com_c)), int(grid.sum())
  ```
- Unwrap the step-by-step COMs:
  ```python
  unwrapped_coms = [coms[0]]
  for i in range(1, len(coms)):
      prev_com = coms[i - 1]
      cur_com = coms[i]
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
- Divide the 200 steps into 5 equal-duration windows of 40 steps each to compute the per-window velocity magnitudes (cells/step) and the standard deviation of velocity magnitudes across the windows.
- Compute the mean velocity magnitude (net displacement vector magnitude divided by 200).
- Check stability and periodicity over the last 50 steps (steps 150 to 200):
  - Translate the active cells of the grid at each step so the lexicographically first cell is at (0,0) (this canonicalizes the shape under translation).
  - Search for a period `p` in `range(1, 21)` such that for all `t` from 150 to `200 - p`, `canonical_active_cells[t] == canonical_active_cells[t + p]` and `bit_counts[t] == bit_counts[t + p]`.
- Classify each seed's behavior:
  - "extinct": if bit count at step 200 is 0.
  - "chaotic/unstable": if active at step 200 but no period <= 20 is detected.
  - "still life": if stable (period == 1) and mean speed < 0.05.
  - "stationary oscillator": if stable (period > 1) and mean speed < 0.05.
  - "v=1c glider": if stable and mean speed >= 0.9.
  - "v<c glider": if stable and 0.05 <= mean speed < 0.9.

Save a comprehensive JSON summary of results to `archive/iter_223/results/glider_probe_results.json` that includes:
- Details about each seed, its classification, period, mean speed, velocity standard deviation, initial bit count, and final bit count.
- A summary count of how many seeds fall into each classification.

Then, analyze and report the findings. Specifically:
1. Does either rule support BOTH a v<c glider and a v=1c glider?
2. Which specific seeds produce them? Include their initial cells (relative coordinates) and their properties.