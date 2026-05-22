Modify `src/engine_d4_dynamic.py` to support a permanent background mass.
Specifically:
1. In `DynamicLatchingEngine.__init__`, initialize `self.permanent_mass = np.zeros((L, L, L), dtype=np.float64)`.
2. In `compute_local_density()`, add `self.permanent_mass` to `cell_m`:
   ```python
   cell_m = (
       self.temporal_grid.sum(axis=-1).astype(np.float64)
       + self.latched_grid.sum(axis=-1).astype(np.float64)
       + self.permanent_mass
   )
   ```
3. Verify that the file compiles successfully and is backwards-compatible.