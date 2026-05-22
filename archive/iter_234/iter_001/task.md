1. Implement the new closed-loop cellular automaton engine in `src/engine_d4_closed_loop_v2.py`.
The engine should manage a 3D toroidal LGCA with dynamic latency driven by a pheromone-like field.
The update rule for the latency field in each step is:
  - Compute active bits at each cell: `active_bits = self.temporal_grid.sum(axis=-1) + self.latched_grid.sum(axis=-1)` (shape (L, L, L)).
  - Apply temporal decay and deposition: `decayed_field = self.gamma * self.latency_field + self.eta * active_bits` (where self.gamma is the temporal retention rate, e.g. 0.95, and self.eta is deposition).
  - Apply 3D periodic Gaussian smoothing with standard deviation `self.sigma` using 3D FFT to prevent discrete gradient shock:
    ```python
    def gaussian_blur_3d_fft(self, field: np.ndarray, sigma: float) -> np.ndarray:
        L = field.shape[0]
        k = np.fft.fftfreq(L)
        KX, KY, KZ = np.meshgrid(k, k, k, indexing="ij")
        K_sq = KX**2 + KY**2 + KZ**2
        H = np.exp(-2.0 * (np.pi * sigma)**2 * K_sq)
        field_fft = np.fft.fftn(field)
        return np.real(np.fft.ifftn(field_fft * H))
    ```
  - Clamp small values: `self.latency_field[self.latency_field < 1e-5] = 0.0`.
  - Let total potential `M = self.latency_field + self.permanent_mass` (permanent_mass defaults to zeros).
  - In trapping: trap temporal bits if `M >= self.threshold` with duration `round(alpha * (M**exponent))`, minimum duration 1.
  - Implement a robust self-test within `src/engine_d4_closed_loop_v2.py` verifying perfect bit conservation and dynamic latency field evolution.

2. Create `src/explore_two_body_attraction_v3.py` to run a compact parameter sweep over the new engine.
  - Load the LUT-08 sub-light glider configuration from `archive/iter_224/results/glider_00_lut08_sub03.json`.
  - Grid size L=32, steps=80, initial Y-separation of 6 cells (cy1=13, cy2=19).
  - Sweep parameters:
    - `alpha`: [2.0, 2.5, 3.0]
    - `threshold`: [0.1, 0.2, 0.4]
    - `gamma` (retention): [0.90, 0.95]
    - `eta`: [0.5, 1.0, 1.5, 2.0]
    - `sigma` = 2.5 (fixed)
  - Keep logging extremely compact and vectorized to avoid token/runtime limit.
  - For each configuration, run the simulation. Reject if bit conservation is violated or if gliders break up (support of active cells > 16 cells per glider or total support > 32 cells).
  - Identify stable configurations that achieve the highest mutual deflection (decrease in separation) at step 80.
  - For the best configuration(s), run a longer validation of 120 steps to confirm that attraction is non-transient and continues to grow.
  - Save the summary of the best sweep results to `archive/iter_234/results/v3_sweep_results.json` and print a summary table.