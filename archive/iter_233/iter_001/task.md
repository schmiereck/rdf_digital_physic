Create the new closed-loop latching CA engine at `src/engine_d4_closed_loop.py`. It must implement `ClosedLoopLatchingEngine` which supports:
- Deposition of latency charge based on local active bits: deposition = eta * active_bits.
- Discrete diffusion and decay of the latency_field using:
  new_latency = (1.0 - gamma) * latency_field + kappa * Laplacian + deposition.
- Optimized update mask: only compute diffusion and update latency_field in cells within `cutoff_radius` of active bits or non-trivial latency (> 1e-4), using periodic roll. Clear potential float noise outside the mask to exactly 0.0.
- Trapping based on the total potential M = latency_field + permanent_mass.

Then, write and run a test script `src/test_engine_d4_closed_loop.py` to:
1. Seed a single stable LUT-08 glider (using glider_00_lut08_sub03.json).
2. Verify perfect bit conservation (always exactly 4 bits) and stable propagation under zero coupling (vacuum).
3. Verify perfect bit conservation and stable engine steps under non-zero coupling (e.g. gamma=0.1, kappa=0.05, eta=1.0, threshold=1.5, alpha=2.0, cutoff_radius=4). Ensure the latency field dynamically builds up and decays as the glider passes.
Make sure all tests pass and print a clear summary.